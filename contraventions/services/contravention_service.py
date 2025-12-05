"""
Service de gestion des contraventions.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contravention,
    ContraventionAuditLog,
    TypeInfraction,
)
from payments.models import QRCode
from vehicles.models import Vehicule


class ContraventionService:
    """Service pour gérer les contraventions"""

    @staticmethod
    @transaction.atomic
    def creer_contravention(
        agent,
        type_infraction_id,
        conducteur_data,
        lieu_data,
        vehicule_plaque=None,
        vehicule_data_manuelle=None,
        date_heure_infraction=None,
        observations="",
        a_accident_associe=False,
        signature_electronique="",
        coordonnees_gps=None,
        **kwargs,
    ):
        """
        Crée une nouvelle contravention avec validation complète.

        Args:
            agent: User object de l'agent contrôleur
            type_infraction_id: UUID du type d'infraction
            conducteur_data: dict avec les données du conducteur (cin, nom_complet, etc.)
            lieu_data: dict avec lieu_infraction, route_type, route_numero
            vehicule_plaque: str, plaque d'immatriculation (optionnel)
            vehicule_data_manuelle: dict avec marque, modele si véhicule non trouvé
            date_heure_infraction: datetime, par défaut timezone.now()
            observations: str, observations de l'agent
            a_accident_associe: bool, si un accident est associé
            signature_electronique: str, signature en base64
            coordonnees_gps: dict avec lat et lon
            **kwargs: autres paramètres optionnels

        Returns:
            Contravention: L'objet contravention créé

        Raises:
            PermissionDenied: Si l'agent n'a pas les permissions
            ValidationError: Si les données sont invalides
        """

        # 1. Vérifier les permissions de l'agent
        try:
            agent_profile = AgentControleurProfile.objects.get(user=agent, est_actif=True)
        except AgentControleurProfile.DoesNotExist:
            raise PermissionDenied("Cet utilisateur n'est pas un agent contrôleur actif ou n'a pas de profil agent.")

        # 2. Récupérer le type d'infraction
        try:
            type_infraction = TypeInfraction.objects.get(id=type_infraction_id, est_actif=True)
        except TypeInfraction.DoesNotExist:
            raise ValidationError("Type d'infraction invalide ou inactif.")

        # 3. Rechercher le véhicule dans la base si plaque fournie
        vehicule = None
        vehicule_plaque_manuelle = ""
        vehicule_marque_manuelle = ""
        vehicule_modele_manuelle = ""

        if vehicule_plaque:
            try:
                vehicule = Vehicule.objects.get(
                    plaque_immatriculation=vehicule_plaque.upper().replace(" ", ""), est_actif=True
                )
            except Vehicule.DoesNotExist:
                # Véhicule non trouvé, utiliser les données manuelles
                vehicule_plaque_manuelle = vehicule_plaque
                if vehicule_data_manuelle:
                    vehicule_marque_manuelle = vehicule_data_manuelle.get("marque", "")
                    vehicule_modele_manuelle = vehicule_data_manuelle.get("modele", "")

        # 4. Rechercher ou créer le conducteur
        if not conducteur_data or "cin" not in conducteur_data:
            raise ValidationError("Les données du conducteur (CIN) sont obligatoires.")

        cin = conducteur_data["cin"].strip()
        if len(cin) != 12 or not cin.isdigit():
            raise ValidationError("Le numéro CIN doit contenir exactement 12 chiffres.")

        conducteur, created = Conducteur.objects.get_or_create(
            cin=cin,
            defaults={
                "nom_complet": conducteur_data.get("nom_complet", ""),
                "date_naissance": conducteur_data.get("date_naissance"),
                "adresse": conducteur_data.get("adresse", ""),
                "telephone": conducteur_data.get("telephone", ""),
                "numero_permis": conducteur_data.get("numero_permis", ""),
                "categorie_permis": conducteur_data.get("categorie_permis", ""),
                "date_delivrance_permis": conducteur_data.get("date_delivrance_permis"),
            },
        )

        # Si le conducteur existe déjà, mettre à jour les informations si fournies
        if not created and conducteur_data.get("nom_complet"):
            conducteur.nom_complet = conducteur_data.get("nom_complet", conducteur.nom_complet)
            conducteur.telephone = conducteur_data.get("telephone", conducteur.telephone)
            conducteur.adresse = conducteur_data.get("adresse", conducteur.adresse)
            if conducteur_data.get("numero_permis"):
                conducteur.numero_permis = conducteur_data["numero_permis"]
            if conducteur_data.get("categorie_permis"):
                conducteur.categorie_permis = conducteur_data["categorie_permis"]
            conducteur.save()

        # 5. Détecter les récidives
        est_recidive = ContraventionService.detecter_recidive(
            conducteur=conducteur, type_infraction=type_infraction, periode_mois=12
        )

        # 6. Calculer le montant avec aggravations
        montant_amende = ContraventionService.calculer_montant_amende(
            type_infraction=type_infraction,
            has_accident=a_accident_associe,
            is_recidive=est_recidive,
            autorite=agent_profile.autorite_type,
        )

        # 7. Récupérer la configuration pour le délai de paiement
        config = ConfigurationSysteme.get_config()
        delai_paiement_jours = config.delai_paiement_standard_jours

        # 8. Définir la date/heure de l'infraction
        if not date_heure_infraction:
            date_heure_infraction = timezone.now()

        # 9. Créer la contravention
        contravention = Contravention(
            agent_controleur=agent_profile,
            type_infraction=type_infraction,
            vehicule=vehicule,
            vehicule_plaque_manuelle=vehicule_plaque_manuelle,
            vehicule_marque_manuelle=vehicule_marque_manuelle,
            vehicule_modele_manuelle=vehicule_modele_manuelle,
            conducteur=conducteur,
            date_heure_infraction=date_heure_infraction,
            lieu_infraction=lieu_data.get("lieu_infraction", ""),
            route_type=lieu_data.get("route_type", ""),
            route_numero=lieu_data.get("route_numero", ""),
            montant_amende_ariary=montant_amende,
            a_accident_associe=a_accident_associe,
            est_recidive=est_recidive,
            observations=observations,
            statut="IMPAYEE",
            delai_paiement_jours=delai_paiement_jours,
            signature_electronique_conducteur=signature_electronique,
        )

        # Ajouter les coordonnées GPS si fournies
        if coordonnees_gps:
            contravention.coordonnees_gps_lat = coordonnees_gps.get("lat")
            contravention.coordonnees_gps_lon = coordonnees_gps.get("lon")

        # Le numéro PV et la date limite seront générés automatiquement par save()
        contravention.save()

        # 10. Créer le QR code de vérification
        qr_code = ContraventionService._creer_qr_code_contravention(contravention)
        if qr_code:
            contravention.qr_code = qr_code
            contravention.save(update_fields=["qr_code"])

        # 11. Enregistrer dans l'audit log
        ContraventionService._enregistrer_audit_log(
            action_type="CREATE",
            user=agent,
            contravention=contravention,
            action_data={
                "agent_matricule": agent_profile.matricule,
                "type_infraction": type_infraction.nom,
                "montant_amende": str(montant_amende),
                "est_recidive": est_recidive,
                "a_accident_associe": a_accident_associe,
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # 12. Envoyer les notifications au propriétaire si disponible
        # (À implémenter avec le système de notifications existant)
        if vehicule and vehicule.proprietaire:
            ContraventionService._envoyer_notification_proprietaire(contravention=contravention, vehicule=vehicule)

        return contravention

    @staticmethod
    def detecter_recidive(conducteur, type_infraction, periode_mois=12):
        """
        Détecte si le conducteur a commis la même infraction récemment.

        Args:
            conducteur: Conducteur object
            type_infraction: TypeInfraction object
            periode_mois: int, période en mois pour vérifier (défaut: 12)

        Returns:
            bool: True si récidive détectée, False sinon
        """
        date_limite = timezone.now() - timedelta(days=periode_mois * 30)

        # Chercher des contraventions du même type dans la période
        contraventions_precedentes = Contravention.objects.filter(
            conducteur=conducteur,
            type_infraction=type_infraction,
            date_heure_infraction__gte=date_limite,
            statut__in=["IMPAYEE", "PAYEE"],  # Exclure les annulées
        ).exists()

        return contraventions_precedentes

    @staticmethod
    def calculer_montant_amende(type_infraction, has_accident=False, is_recidive=False, autorite=None):
        """
        Calcule le montant final de l'amende avec aggravations.

        Args:
            type_infraction: TypeInfraction object
            has_accident: bool, si un accident est associé
            is_recidive: bool, si c'est une récidive
            autorite: str, type d'autorité (POLICE_NATIONALE, GENDARMERIE, POLICE_COMMUNALE)

        Returns:
            Decimal: Montant final de l'amende
        """
        return type_infraction.calculer_montant_avec_aggravations(
            has_accident=has_accident, is_recidive=is_recidive, autorite=autorite
        )

    @staticmethod
    def _creer_qr_code_contravention(contravention):
        """
        Crée un QR code de vérification pour la contravention.

        Args:
            contravention: Contravention object

        Returns:
            QRCode object ou None
        """
        try:
            # Générer l'URL de vérification
            # Format: /contraventions/verify/{numero_pv}/
            verification_url = f"/contraventions/verify/{contravention.numero_pv}/"

            qr_code = QRCode.objects.create(
                code=contravention.numero_pv,
                type_code="CONTRAVENTION",
                data={
                    "numero_pv": contravention.numero_pv,
                    "montant_amende": str(contravention.montant_amende_ariary),
                    "date_infraction": contravention.date_heure_infraction.isoformat(),
                    "verification_url": verification_url,
                },
            )
            return qr_code
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la création du QR code: {str(e)}")
            return None

    @staticmethod
    def _enregistrer_audit_log(action_type, user, contravention, action_data, ip_address=None, user_agent=None):
        """
        Enregistre une action dans le journal d'audit.

        Args:
            action_type: str, type d'action (CREATE, UPDATE, etc.)
            user: User object
            contravention: Contravention object
            action_data: dict, données de l'action
            ip_address: str, adresse IP (optionnel)
            user_agent: str, user agent (optionnel)
        """
        try:
            ContraventionAuditLog.objects.create(
                action_type=action_type,
                user=user,
                contravention=contravention,
                action_data=action_data,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de l'enregistrement de l'audit log: {str(e)}")

    @staticmethod
    def _envoyer_notification_proprietaire(contravention, vehicule):
        """
        Envoie une notification au propriétaire du véhicule.

        Args:
            contravention: Contravention object
            vehicule: Vehicule object
        """
        try:
            from notifications.services import NotificationService

            # Déterminer la langue de l'utilisateur
            langue = "fr"
            if hasattr(vehicule.proprietaire, "profile") and hasattr(vehicule.proprietaire.profile, "langue_preferee"):
                langue = vehicule.proprietaire.profile.langue_preferee

            # Utiliser la méthode spécialisée pour les contraventions
            NotificationService.create_contravention_notification(
                user=vehicule.proprietaire, contravention=contravention, langue=langue
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de l'envoi de la notification: {str(e)}")

    @staticmethod
    @transaction.atomic
    def annuler_contravention(contravention, user, motif, **kwargs):
        """
        Annule une contravention avec validation des règles métier.

        Args:
            contravention: Contravention object à annuler
            user: User object qui demande l'annulation
            motif: str, motif de l'annulation
            **kwargs: paramètres optionnels (ip_address, user_agent, force_superviseur)

        Returns:
            tuple: (success: bool, message: str)

        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
            ValidationError: Si l'annulation n'est pas possible
        """
        import logging

        logger = logging.getLogger(__name__)

        # Vérifier que la contravention n'est pas déjà annulée
        if contravention.statut == "ANNULEE":
            raise ValidationError("Cette contravention est déjà annulée.")

        # Récupérer la configuration
        config = ConfigurationSysteme.get_config()

        # Calculer le temps écoulé depuis la création
        temps_ecoule = timezone.now() - contravention.created_at
        heures_ecoulees = temps_ecoule.total_seconds() / 3600

        # Vérifier si l'utilisateur est l'agent qui a créé la contravention
        est_agent_createur = False
        try:
            agent_profile = AgentControleurProfile.objects.get(user=user, est_actif=True)
            est_agent_createur = contravention.agent_controleur == agent_profile
        except AgentControleurProfile.DoesNotExist:
            pass

        # Vérifier si l'utilisateur est un superviseur
        est_superviseur = user.groups.filter(name__in=["Superviseur Police", "Administrateur Contraventions"]).exists()

        # Règle 1: Annulation directe dans les 24h par l'agent créateur
        peut_annuler_directement = est_agent_createur and heures_ecoulees <= config.delai_annulation_directe_heures

        # Règle 2: Annulation par superviseur après 24h
        peut_annuler_superviseur = est_superviseur or kwargs.get("force_superviseur", False)

        # Vérifier les permissions
        if not (peut_annuler_directement or peut_annuler_superviseur):
            if est_agent_createur:
                raise PermissionDenied(
                    f"Le délai d'annulation directe de {config.delai_annulation_directe_heures}h est dépassé. "
                    "Une validation par un superviseur est requise."
                )
            else:
                raise PermissionDenied(
                    "Vous n'avez pas les permissions pour annuler cette contravention. "
                    "Seul l'agent créateur (dans les 24h) ou un superviseur peut annuler une contravention."
                )

        # Vérifier si le véhicule est en fourrière
        if hasattr(contravention, "dossier_fourriere"):
            dossier = contravention.dossier_fourriere
            if dossier.statut == "EN_FOURRIERE" and not est_superviseur:
                raise ValidationError(
                    "Cette contravention est liée à un véhicule en fourrière. "
                    "Seul un administrateur de niveau supérieur peut l'annuler."
                )

        # Vérifier si la contravention a été payée
        contravention_payee = contravention.statut == "PAYEE"
        montant_a_rembourser = Decimal("0")

        if contravention_payee:
            # Récupérer le paiement associé
            from payments.models import PaiementTaxe

            paiements = PaiementTaxe.objects.filter(contravention=contravention, statut="PAYE")

            if paiements.exists():
                # Calculer le montant total payé
                montant_a_rembourser = sum(p.montant_paye_ariary or Decimal("0") for p in paiements)

                logger.info(
                    f"Contravention {contravention.numero_pv} payée. "
                    f"Montant à rembourser: {montant_a_rembourser} Ariary"
                )

                # Marquer les paiements comme annulés
                for paiement in paiements:
                    paiement.statut = "ANNULE"
                    paiement.details_paiement["annulation"] = {
                        "date": timezone.now().isoformat(),
                        "motif": motif,
                        "annule_par": user.username,
                        "montant_rembourse": str(montant_a_rembourser),
                    }
                    paiement.save()

                # Note: Le remboursement effectif doit être géré manuellement
                # ou via un processus de remboursement séparé selon la méthode de paiement

        # Annuler la contravention
        ancien_statut = contravention.statut
        contravention.statut = "ANNULEE"
        contravention.save()

        # Enregistrer dans l'audit log
        ContraventionService._enregistrer_audit_log(
            action_type="CANCEL",
            user=user,
            contravention=contravention,
            action_data={
                "motif": motif,
                "ancien_statut": ancien_statut,
                "annule_par": user.username,
                "est_agent_createur": est_agent_createur,
                "est_superviseur": est_superviseur,
                "heures_ecoulees": round(heures_ecoulees, 2),
                "contravention_payee": contravention_payee,
                "montant_a_rembourser": str(montant_a_rembourser) if contravention_payee else "0",
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # Envoyer une notification au conducteur si possible
        if contravention.conducteur and contravention.conducteur.telephone:
            try:
                ContraventionService._envoyer_notification_annulation(
                    contravention=contravention,
                    motif=motif,
                    montant_rembourse=montant_a_rembourser if contravention_payee else None,
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification d'annulation: {str(e)}")

        # Construire le message de retour
        message = f"Contravention {contravention.numero_pv} annulée avec succès."
        if contravention_payee and montant_a_rembourser > 0:
            message += f" Un remboursement de {montant_a_rembourser} Ariary doit être effectué."

        return True, message

    @staticmethod
    def get_contraventions_impayees(conducteur=None, vehicule=None):
        """
        Récupère les contraventions impayées pour un conducteur ou un véhicule.

        Args:
            conducteur: Conducteur object (optionnel)
            vehicule: Vehicule object (optionnel)

        Returns:
            QuerySet: Liste des contraventions impayées

        Raises:
            ValidationError: Si aucun paramètre n'est fourni
        """
        if not conducteur and not vehicule:
            raise ValidationError("Au moins un paramètre (conducteur ou véhicule) doit être fourni.")

        # Construire la requête de base
        queryset = (
            Contravention.objects.filter(statut__in=["IMPAYEE", "CONTESTEE"])
            .select_related("type_infraction", "agent_controleur", "conducteur", "vehicule")
            .order_by("-date_heure_infraction")
        )

        # Filtrer par conducteur
        if conducteur:
            queryset = queryset.filter(conducteur=conducteur)

        # Filtrer par véhicule
        if vehicule:
            queryset = queryset.filter(vehicule=vehicule)

        return queryset

    @staticmethod
    def _envoyer_notification_annulation(contravention, motif, montant_rembourse=None):
        """
        Envoie une notification d'annulation de contravention.

        Args:
            contravention: Contravention object
            motif: str, motif de l'annulation
            montant_rembourse: Decimal, montant à rembourser (optionnel)
        """
        try:
            from notifications.services import NotificationService

            # Si le conducteur a un compte utilisateur
            if hasattr(contravention.conducteur, "user"):
                user = contravention.conducteur.user
                langue = "fr"
                if hasattr(user, "profile") and hasattr(user.profile, "langue_preferee"):
                    langue = user.profile.langue_preferee

                # Créer la notification
                titre = "Contravention annulée" if langue == "fr" else "Contravention annulée"
                message = f"Votre contravention {contravention.numero_pv} a été annulée. Motif: {motif}"

                if montant_rembourse and montant_rembourse > 0:
                    message += f" Un remboursement de {montant_rembourse} Ariary sera effectué."

                NotificationService.create_notification(
                    user=user, titre=titre, message=message, type_notification="INFO", langue=langue
                )

            # Si le véhicule a un propriétaire
            elif contravention.vehicule and contravention.vehicule.proprietaire:
                user = contravention.vehicule.proprietaire
                langue = "fr"
                if hasattr(user, "profile") and hasattr(user.profile, "langue_preferee"):
                    langue = user.profile.langue_preferee

                titre = "Contravention annulée" if langue == "fr" else "Contravention annulée"
                message = (
                    f"La contravention {contravention.numero_pv} pour votre véhicule a été annulée. Motif: {motif}"
                )

                if montant_rembourse and montant_rembourse > 0:
                    message += f" Un remboursement de {montant_rembourse} Ariary sera effectué."

                NotificationService.create_notification(
                    user=user, titre=titre, message=message, type_notification="INFO", langue=langue
                )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de l'envoi de la notification d'annulation: {str(e)}")
