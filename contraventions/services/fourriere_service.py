"""
Service de gestion des dossiers de fourrière.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from contraventions.models import ConfigurationSysteme, Contravention, ContraventionAuditLog, DossierFourriere
from payments.models import PaiementTaxe, QRCode


class FourriereService:
    """Service pour gérer les dossiers de fourrière"""

    @staticmethod
    @transaction.atomic
    def creer_dossier_fourriere(
        contravention,
        lieu_fourriere,
        adresse_fourriere,
        type_vehicule="VOITURE",
        frais_transport=None,
        frais_gardiennage_journalier=None,
        duree_minimale_jours=None,
        notes="",
        user=None,
        **kwargs,
    ):
        """
        Crée un dossier de fourrière lié à une contravention.

        Args:
            contravention: Contravention object
            lieu_fourriere: str, nom du lieu de fourrière
            adresse_fourriere: str, adresse complète de la fourrière
            type_vehicule: str, type de véhicule (VOITURE, MOTO, CAMION, etc.)
            frais_transport: Decimal, frais de transport (optionnel, utilise config par défaut)
            frais_gardiennage_journalier: Decimal, frais journaliers (optionnel, utilise config par défaut)
            duree_minimale_jours: int, durée minimale en jours (optionnel, utilise config par défaut)
            notes: str, notes additionnelles
            user: User object qui crée le dossier
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            DossierFourriere: Le dossier de fourrière créé

        Raises:
            ValidationError: Si les données sont invalides ou si un dossier existe déjà
        """
        import logging

        logger = logging.getLogger(__name__)

        # Vérifier qu'un dossier n'existe pas déjà pour cette contravention
        if hasattr(contravention, "dossier_fourriere"):
            raise ValidationError(
                f"Un dossier de fourrière existe déjà pour la contravention {contravention.numero_pv}."
            )

        # Vérifier que la contravention n'est pas annulée
        if contravention.statut == "ANNULEE":
            raise ValidationError("Impossible de créer un dossier de fourrière pour une contravention annulée.")

        # Récupérer la configuration
        config = ConfigurationSysteme.get_config()

        # Utiliser les valeurs par défaut de la configuration si non fournies
        if frais_transport is None:
            frais_transport = config.frais_transport_fourriere_ariary

        if frais_gardiennage_journalier is None:
            frais_gardiennage_journalier = config.frais_gardiennage_journalier_ariary

        if duree_minimale_jours is None:
            # Vérifier si c'est un produit périssable (à implémenter selon les besoins)
            duree_minimale_jours = config.duree_minimale_fourriere_jours

        # Générer le numéro de dossier
        date_str = timezone.now().strftime("%Y%m%d")
        # Compter les dossiers créés aujourd'hui pour générer un numéro séquentiel
        count_today = DossierFourriere.objects.filter(numero_dossier__startswith=f"FOUR-{date_str}").count()
        numero_dossier = f"FOUR-{date_str}-{str(count_today + 1).zfill(5)}"

        # Créer le dossier de fourrière
        dossier = DossierFourriere.objects.create(
            contravention=contravention,
            numero_dossier=numero_dossier,
            date_mise_fourriere=timezone.now(),
            lieu_fourriere=lieu_fourriere,
            adresse_fourriere=adresse_fourriere,
            type_vehicule=type_vehicule,
            frais_transport_ariary=frais_transport,
            frais_gardiennage_journalier_ariary=frais_gardiennage_journalier,
            duree_minimale_jours=duree_minimale_jours,
            statut="EN_FOURRIERE",
            notes=notes,
        )

        # Calculer les frais initiaux (transport uniquement)
        dossier.frais_totaux_ariary = frais_transport
        dossier.save(update_fields=["frais_totaux_ariary"])

        # Enregistrer dans l'audit log
        if user:
            try:
                ContraventionAuditLog.objects.create(
                    action_type="FOURRIERE_CREATE",
                    user=user,
                    contravention=contravention,
                    action_data={
                        "numero_dossier": numero_dossier,
                        "lieu_fourriere": lieu_fourriere,
                        "type_vehicule": type_vehicule,
                        "frais_transport": str(frais_transport),
                        "frais_gardiennage_journalier": str(frais_gardiennage_journalier),
                        "duree_minimale_jours": duree_minimale_jours,
                    },
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement de l'audit log: {str(e)}")

        logger.info(f"Dossier de fourrière {numero_dossier} créé pour la contravention {contravention.numero_pv}")

        return dossier

    @staticmethod
    def calculer_frais_fourriere(dossier):
        """
        Calcule les frais totaux de fourrière (transport + gardiennage).

        Args:
            dossier: DossierFourriere object

        Returns:
            dict: {
                'frais_transport': Decimal,
                'jours_gardiennage': int,
                'frais_gardiennage': Decimal,
                'frais_totaux': Decimal
            }
        """
        # Frais de transport (fixe)
        frais_transport = dossier.frais_transport_ariary

        # Calculer le nombre de jours de gardiennage
        if dossier.date_sortie_fourriere:
            # Si le véhicule est sorti, calculer jusqu'à la date de sortie
            duree = dossier.date_sortie_fourriere - dossier.date_mise_fourriere
        else:
            # Sinon, calculer jusqu'à maintenant
            duree = timezone.now() - dossier.date_mise_fourriere

        jours_gardiennage = max(0, duree.days)

        # Calculer les frais de gardiennage
        frais_gardiennage = dossier.frais_gardiennage_journalier_ariary * jours_gardiennage

        # Calculer le total
        frais_totaux = frais_transport + frais_gardiennage

        return {
            "frais_transport": frais_transport,
            "jours_gardiennage": jours_gardiennage,
            "frais_gardiennage": frais_gardiennage,
            "frais_totaux": frais_totaux,
        }

    @staticmethod
    def peut_restituer_vehicule(dossier):
        """
        Vérifie si le véhicule peut être restitué.

        Args:
            dossier: DossierFourriere object

        Returns:
            tuple: (peut_restituer: bool, raison: str)
        """
        # Vérifier que le véhicule est toujours en fourrière
        if dossier.statut != "EN_FOURRIERE":
            return False, f"Le véhicule n'est plus en fourrière (statut: {dossier.get_statut_display()})"

        # Vérifier la durée minimale
        duree_ecoulee = timezone.now() - dossier.date_mise_fourriere
        jours_ecoules = duree_ecoulee.days

        if jours_ecoules < dossier.duree_minimale_jours:
            jours_restants = dossier.duree_minimale_jours - jours_ecoules
            return False, f"Durée minimale non atteinte. Il reste {jours_restants} jour(s)."

        # Vérifier que la contravention est payée
        contravention = dossier.contravention
        if contravention.statut != "PAYEE":
            return False, "L'amende de la contravention n'a pas été payée."

        # Vérifier que les frais de fourrière sont payés
        # Chercher un paiement pour les frais de fourrière
        paiements_fourriere = PaiementTaxe.objects.filter(
            type_paiement="FRAIS_FOURRIERE", details_paiement__numero_dossier=dossier.numero_dossier, statut="PAYE"
        )

        if not paiements_fourriere.exists():
            frais = FourriereService.calculer_frais_fourriere(dossier)
            return False, f"Les frais de fourrière ({frais['frais_totaux']} Ariary) n'ont pas été payés."

        # Toutes les conditions sont remplies
        return True, "Le véhicule peut être restitué."

    @staticmethod
    @transaction.atomic
    def generer_bon_sortie(dossier, user=None, **kwargs):
        """
        Génère le bon de sortie de fourrière avec QR code.

        Args:
            dossier: DossierFourriere object
            user: User object qui génère le bon
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            tuple: (success: bool, bon_sortie_numero: str, qr_code: QRCode)

        Raises:
            ValidationError: Si le véhicule ne peut pas être restitué
        """
        import logging

        logger = logging.getLogger(__name__)

        # Vérifier que le véhicule peut être restitué
        peut_restituer, raison = FourriereService.peut_restituer_vehicule(dossier)

        if not peut_restituer:
            raise ValidationError(f"Impossible de générer le bon de sortie: {raison}")

        # Générer le numéro de bon de sortie
        date_str = timezone.now().strftime("%Y%m%d")
        count_today = (
            DossierFourriere.objects.filter(bon_sortie_numero__startswith=f"BS-{date_str}")
            .exclude(bon_sortie_numero="")
            .count()
        )
        bon_sortie_numero = f"BS-{date_str}-{str(count_today + 1).zfill(5)}"

        # Mettre à jour le dossier
        dossier.bon_sortie_numero = bon_sortie_numero
        dossier.date_sortie_fourriere = timezone.now()
        dossier.statut = "RESTITUE"

        # Calculer et enregistrer les frais totaux finaux
        frais = FourriereService.calculer_frais_fourriere(dossier)
        dossier.frais_totaux_ariary = frais["frais_totaux"]

        dossier.save()

        # Créer le QR code pour le bon de sortie
        try:
            qr_code = QRCode.objects.create(
                code=bon_sortie_numero,
                type_code="BON_SORTIE_FOURRIERE",
                data={
                    "numero_dossier": dossier.numero_dossier,
                    "bon_sortie_numero": bon_sortie_numero,
                    "numero_pv": dossier.contravention.numero_pv,
                    "date_sortie": dossier.date_sortie_fourriere.isoformat(),
                    "frais_totaux": str(frais["frais_totaux"]),
                    "jours_gardiennage": frais["jours_gardiennage"],
                },
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création du QR code: {str(e)}")
            qr_code = None

        # Enregistrer dans l'audit log
        if user:
            try:
                ContraventionAuditLog.objects.create(
                    action_type="FOURRIERE_SORTIE",
                    user=user,
                    contravention=dossier.contravention,
                    action_data={
                        "numero_dossier": dossier.numero_dossier,
                        "bon_sortie_numero": bon_sortie_numero,
                        "date_sortie": dossier.date_sortie_fourriere.isoformat(),
                        "jours_gardiennage": frais["jours_gardiennage"],
                        "frais_totaux": str(frais["frais_totaux"]),
                    },
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement de l'audit log: {str(e)}")

        logger.info(
            f"Bon de sortie {bon_sortie_numero} généré pour le dossier {dossier.numero_dossier}. "
            f"Frais totaux: {frais['frais_totaux']} Ariary"
        )

        return True, bon_sortie_numero, qr_code

    @staticmethod
    def get_dossiers_actifs():
        """
        Récupère tous les dossiers de fourrière actifs (véhicules encore en fourrière).

        Returns:
            QuerySet: Liste des dossiers actifs
        """
        return (
            DossierFourriere.objects.filter(statut="EN_FOURRIERE")
            .select_related(
                "contravention",
                "contravention__vehicule",
                "contravention__conducteur",
                "contravention__agent_controleur",
            )
            .order_by("-date_mise_fourriere")
        )

    @staticmethod
    def get_statistiques_fourriere(date_debut=None, date_fin=None):
        """
        Calcule les statistiques de la fourrière pour une période donnée.

        Args:
            date_debut: datetime, date de début (optionnel)
            date_fin: datetime, date de fin (optionnel)

        Returns:
            dict: Statistiques de la fourrière
        """
        from django.db.models import Avg, Count, Sum

        # Construire la requête de base
        queryset = DossierFourriere.objects.all()

        if date_debut:
            queryset = queryset.filter(date_mise_fourriere__gte=date_debut)

        if date_fin:
            queryset = queryset.filter(date_mise_fourriere__lte=date_fin)

        # Calculer les statistiques
        stats = queryset.aggregate(
            total_dossiers=Count("id"),
            dossiers_actifs=Count("id", filter=queryset.filter(statut="EN_FOURRIERE").query),
            dossiers_restitues=Count("id", filter=queryset.filter(statut="RESTITUE").query),
            frais_totaux=Sum("frais_totaux_ariary"),
            duree_moyenne_jours=Avg("date_sortie_fourriere__day") - Avg("date_mise_fourriere__day"),
        )

        return {
            "total_dossiers": stats["total_dossiers"] or 0,
            "dossiers_actifs": stats["dossiers_actifs"] or 0,
            "dossiers_restitues": stats["dossiers_restitues"] or 0,
            "frais_totaux_collectes": stats["frais_totaux"] or Decimal("0"),
            "duree_moyenne_jours": stats["duree_moyenne_jours"] or 0,
        }
