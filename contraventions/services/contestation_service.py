"""
Service de gestion des contestations de contraventions.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from contraventions.models import ConfigurationSysteme, Contestation, Contravention, ContraventionAuditLog

logger = logging.getLogger(__name__)


class ContestationService:
    """Service pour gérer les contestations de contraventions"""

    @staticmethod
    @transaction.atomic
    def soumettre_contestation(contravention, demandeur_data, motif, documents=None, user=None, **kwargs):
        """
        Soumet une nouvelle contestation avec upload de documents.

        Args:
            contravention: Contravention object
            demandeur_data: dict avec nom_demandeur, email_demandeur, telephone_demandeur
            motif: str, motif détaillé de la contestation
            documents: list de fichiers uploadés (optionnel)
            user: User object du demandeur (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            Contestation: L'objet contestation créé

        Raises:
            ValidationError: Si les données sont invalides ou si le délai est dépassé
        """
        # Vérifier que la contravention peut être contestée
        if contravention.statut == "ANNULEE":
            raise ValidationError("Cette contravention a été annulée et ne peut pas être contestée.")

        if contravention.statut == "CONTESTEE":
            # Vérifier s'il y a déjà une contestation en cours
            contestations_actives = Contestation.objects.filter(
                contravention=contravention, statut__in=["EN_ATTENTE", "EN_EXAMEN"]
            )
            if contestations_actives.exists():
                raise ValidationError("Une contestation est déjà en cours pour cette contravention.")

        # Vérifier le délai de contestation
        config = ConfigurationSysteme.get_config()
        delai_contestation = timedelta(days=config.delai_contestation_jours)
        temps_ecoule = timezone.now() - contravention.created_at

        if temps_ecoule > delai_contestation:
            raise ValidationError(f"Le délai de contestation de {config.delai_contestation_jours} jours est dépassé.")

        # Valider les données du demandeur
        if not demandeur_data.get("nom_demandeur"):
            raise ValidationError("Le nom du demandeur est obligatoire.")

        if not motif or len(motif.strip()) < 20:
            raise ValidationError("Le motif de la contestation doit contenir au moins 20 caractères.")

        # Générer le numéro de contestation
        date_str = timezone.now().strftime("%Y%m%d")
        count_today = Contestation.objects.filter(numero_contestation__startswith=f"CONT-{date_str}").count()
        numero_contestation = f"CONT-{date_str}-{str(count_today + 1).zfill(5)}"

        # Créer la contestation
        contestation = Contestation.objects.create(
            contravention=contravention,
            numero_contestation=numero_contestation,
            demandeur=user,
            nom_demandeur=demandeur_data.get("nom_demandeur", ""),
            email_demandeur=demandeur_data.get("email_demandeur", ""),
            telephone_demandeur=demandeur_data.get("telephone_demandeur", ""),
            motif=motif,
            statut="EN_ATTENTE",
            date_soumission=timezone.now(),
        )

        # Traiter les documents justificatifs
        documents_urls = []
        if documents:
            for document in documents:
                try:
                    # Sauvegarder le document
                    file_path = f"contestations/{contravention.numero_pv}/{document.name}"
                    saved_path = default_storage.save(file_path, document)
                    documents_urls.append(saved_path)
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde du document: {str(e)}")

        contestation.documents_justificatifs = documents_urls
        contestation.save()

        # Suspendre le délai de paiement
        ContestationService._suspendre_delai_paiement(contravention)

        # Mettre à jour le statut de la contravention
        contravention.statut = "CONTESTEE"
        contravention.save()

        # Enregistrer dans l'audit log
        ContraventionAuditLog.objects.create(
            action_type="CONTESTATION_SUBMITTED",
            user=user,
            contravention=contravention,
            action_data={
                "numero_contestation": numero_contestation,
                "nom_demandeur": demandeur_data.get("nom_demandeur", ""),
                "motif_preview": motif[:100] + "..." if len(motif) > 100 else motif,
                "nombre_documents": len(documents_urls),
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # Envoyer une notification à l'agent contrôleur
        ContestationService._notifier_agent_contestation(contravention, contestation)

        logger.info(f"Contestation {numero_contestation} soumise pour la contravention {contravention.numero_pv}")

        return contestation

    @staticmethod
    @transaction.atomic
    def examiner_contestation(contestation, examinateur, decision, motif_decision, user=None, **kwargs):
        """
        Examine une contestation (pour superviseurs).

        Args:
            contestation: Contestation object
            examinateur: User object (superviseur)
            decision: str, 'ACCEPTEE' ou 'REJETEE'
            motif_decision: str, motif de la décision
            user: User object (optionnel, par défaut = examinateur)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            tuple: (success: bool, message: str)

        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
            ValidationError: Si les données sont invalides
        """
        # Vérifier les permissions
        if not examinateur.groups.filter(name__in=["Superviseur Police", "Administrateur Contraventions"]).exists():
            raise PermissionDenied("Seuls les superviseurs peuvent examiner les contestations.")

        # Vérifier que la contestation est en attente ou en examen
        if contestation.statut not in ["EN_ATTENTE", "EN_EXAMEN"]:
            raise ValidationError(
                f"Cette contestation a déjà été traitée (statut: {contestation.get_statut_display()})."
            )

        # Valider la décision
        if decision not in ["ACCEPTEE", "REJETEE"]:
            raise ValidationError("La décision doit être 'ACCEPTEE' ou 'REJETEE'.")

        if not motif_decision or len(motif_decision.strip()) < 10:
            raise ValidationError("Le motif de la décision doit contenir au moins 10 caractères.")

        # Mettre à jour la contestation
        contestation.statut = "EN_EXAMEN"
        contestation.examine_par = examinateur
        contestation.date_examen = timezone.now()
        contestation.save()

        # Enregistrer dans l'audit log
        ContraventionAuditLog.objects.create(
            action_type="CONTESTATION_EXAMINED",
            user=user or examinateur,
            contravention=contestation.contravention,
            action_data={
                "numero_contestation": contestation.numero_contestation,
                "examinateur": examinateur.username,
                "decision": decision,
                "motif_decision_preview": motif_decision[:100] + "..." if len(motif_decision) > 100 else motif_decision,
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # Appliquer la décision
        if decision == "ACCEPTEE":
            return ContestationService.accepter_contestation(
                contestation=contestation, motif_decision=motif_decision, user=user or examinateur, **kwargs
            )
        else:
            return ContestationService.rejeter_contestation(
                contestation=contestation, motif_decision=motif_decision, user=user or examinateur, **kwargs
            )

    @staticmethod
    @transaction.atomic
    def accepter_contestation(contestation, motif_decision="", user=None, **kwargs):
        """
        Accepte une contestation et annule la contravention.

        Args:
            contestation: Contestation object
            motif_decision: str, motif de l'acceptation
            user: User object (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            tuple: (success: bool, message: str)
        """
        # Mettre à jour la contestation
        contestation.statut = "ACCEPTEE"
        contestation.decision_motif = motif_decision
        if not contestation.date_examen:
            contestation.date_examen = timezone.now()
        contestation.save()

        # Annuler la contravention
        contravention = contestation.contravention

        # Utiliser le service de contravention pour l'annulation
        from contraventions.services.contravention_service import ContraventionService

        try:
            success, message = ContraventionService.annuler_contravention(
                contravention=contravention,
                user=user or contestation.examine_par,
                motif=f"Contestation acceptée: {motif_decision}",
                force_superviseur=True,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de la contravention: {str(e)}")
            # Continuer même si l'annulation échoue
            contravention.statut = "ANNULEE"
            contravention.save()
            message = f"Contestation acceptée. Erreur lors de l'annulation: {str(e)}"

        # Enregistrer dans l'audit log
        ContraventionAuditLog.objects.create(
            action_type="CONTESTATION_ACCEPTED",
            user=user or contestation.examine_par,
            contravention=contravention,
            action_data={
                "numero_contestation": contestation.numero_contestation,
                "motif_decision": motif_decision,
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # Envoyer une notification au demandeur
        ContestationService._notifier_demandeur_decision(contestation, "ACCEPTEE")

        logger.info(
            f"Contestation {contestation.numero_contestation} acceptée. "
            f"Contravention {contravention.numero_pv} annulée."
        )

        return True, f"Contestation acceptée. La contravention {contravention.numero_pv} a été annulée."

    @staticmethod
    @transaction.atomic
    def rejeter_contestation(contestation, motif_decision="", user=None, **kwargs):
        """
        Rejette une contestation et réactive le délai de paiement.

        Args:
            contestation: Contestation object
            motif_decision: str, motif du rejet
            user: User object (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            tuple: (success: bool, message: str)
        """
        # Mettre à jour la contestation
        contestation.statut = "REJETEE"
        contestation.decision_motif = motif_decision
        if not contestation.date_examen:
            contestation.date_examen = timezone.now()
        contestation.save()

        # Réactiver le délai de paiement
        contravention = contestation.contravention
        ContestationService._reactiver_delai_paiement(contravention)

        # Mettre à jour le statut de la contravention
        contravention.statut = "IMPAYEE"
        contravention.save()

        # Enregistrer dans l'audit log
        ContraventionAuditLog.objects.create(
            action_type="CONTESTATION_REJECTED",
            user=user or contestation.examine_par,
            contravention=contravention,
            action_data={
                "numero_contestation": contestation.numero_contestation,
                "motif_decision": motif_decision,
                "nouvelle_date_limite": contravention.date_limite_paiement.isoformat(),
            },
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )

        # Envoyer une notification au demandeur
        ContestationService._notifier_demandeur_decision(contestation, "REJETEE")

        logger.info(
            f"Contestation {contestation.numero_contestation} rejetée. "
            f"Nouvelle date limite: {contravention.date_limite_paiement}"
        )

        return True, f"Contestation rejetée. Le délai de paiement a été réactivé."

    @staticmethod
    def _suspendre_delai_paiement(contravention):
        """
        Suspend le délai de paiement pendant l'examen de la contestation.

        Args:
            contravention: Contravention object
        """
        # Enregistrer la date limite actuelle dans les détails
        # pour pouvoir la restaurer si la contestation est rejetée
        if not hasattr(contravention, "_date_limite_avant_contestation"):
            contravention._date_limite_avant_contestation = contravention.date_limite_paiement

        # Prolonger la date limite de manière significative (ex: +90 jours)
        # pour suspendre effectivement le délai
        contravention.date_limite_paiement = timezone.now().date() + timedelta(days=90)
        contravention.save()

        logger.info(
            f"Délai de paiement suspendu pour la contravention {contravention.numero_pv}. "
            f"Nouvelle date limite: {contravention.date_limite_paiement}"
        )

    @staticmethod
    def _reactiver_delai_paiement(contravention):
        """
        Réactive le délai de paiement après rejet de la contestation.

        Args:
            contravention: Contravention object
        """
        # Calculer le temps écoulé depuis la création de la contravention
        temps_ecoule = timezone.now() - contravention.created_at
        jours_ecoules = temps_ecoule.days

        # Récupérer la configuration
        config = ConfigurationSysteme.get_config()

        # Accorder un nouveau délai (ex: 15 jours à partir de maintenant)
        nouveau_delai = config.delai_paiement_standard_jours
        contravention.date_limite_paiement = timezone.now().date() + timedelta(days=nouveau_delai)
        contravention.save()

        logger.info(
            f"Délai de paiement réactivé pour la contravention {contravention.numero_pv}. "
            f"Nouvelle date limite: {contravention.date_limite_paiement}"
        )

    @staticmethod
    def _notifier_agent_contestation(contravention, contestation):
        """
        Envoie une notification à l'agent contrôleur qu'une contestation a été soumise.

        Args:
            contravention: Contravention object
            contestation: Contestation object
        """
        try:
            from notifications.services import NotificationService

            agent_user = contravention.agent_controleur.user
            langue = "fr"
            if hasattr(agent_user, "profile") and hasattr(agent_user.profile, "langue_preferee"):
                langue = agent_user.profile.langue_preferee

            titre = "Nouvelle contestation" if langue == "fr" else "Nouvelle contestation"
            message = (
                f"Une contestation a été soumise pour la contravention {contravention.numero_pv}. "
                f"Numéro de contestation: {contestation.numero_contestation}"
            )

            NotificationService.create_notification(
                user=agent_user, titre=titre, message=message, type_notification="INFO", langue=langue
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification à l'agent: {str(e)}")

    @staticmethod
    def _notifier_demandeur_decision(contestation, decision):
        """
        Envoie une notification au demandeur de la décision sur sa contestation.

        Args:
            contestation: Contestation object
            decision: str, 'ACCEPTEE' ou 'REJETEE'
        """
        try:
            from notifications.services import NotificationService

            # Si le demandeur a un compte utilisateur
            if contestation.demandeur:
                user = contestation.demandeur
                langue = "fr"
                if hasattr(user, "profile") and hasattr(user.profile, "langue_preferee"):
                    langue = user.profile.langue_preferee

                if decision == "ACCEPTEE":
                    titre = "Contestation acceptée" if langue == "fr" else "Contestation acceptée"
                    message = (
                        f"Votre contestation {contestation.numero_contestation} a été acceptée. "
                        f"La contravention {contestation.contravention.numero_pv} a été annulée."
                    )
                    type_notif = "SUCCESS"
                else:
                    titre = "Contestation rejetée" if langue == "fr" else "Contestation rejetée"
                    message = (
                        f"Votre contestation {contestation.numero_contestation} a été rejetée. "
                        f"Motif: {contestation.decision_motif}. "
                        f"Vous devez payer l'amende avant le {contestation.contravention.date_limite_paiement}."
                    )
                    type_notif = "WARNING"

                NotificationService.create_notification(
                    user=user, titre=titre, message=message, type_notification=type_notif, langue=langue
                )

            # Sinon, envoyer un email si disponible
            elif contestation.email_demandeur:
                # TODO: Implémenter l'envoi d'email
                logger.info(
                    f"Email à envoyer à {contestation.email_demandeur} pour la décision "
                    f"sur la contestation {contestation.numero_contestation}"
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification de décision: {str(e)}")

    @staticmethod
    def get_contestations_en_attente():
        """
        Récupère toutes les contestations en attente d'examen.

        Returns:
            QuerySet: Liste des contestations en attente
        """
        return (
            Contestation.objects.filter(statut__in=["EN_ATTENTE", "EN_EXAMEN"])
            .select_related(
                "contravention",
                "contravention__type_infraction",
                "contravention__agent_controleur",
                "contravention__conducteur",
                "demandeur",
                "examine_par",
            )
            .order_by("date_soumission")
        )

    @staticmethod
    def get_statistiques_contestations(date_debut=None, date_fin=None):
        """
        Calcule les statistiques des contestations pour une période donnée.

        Args:
            date_debut: datetime, date de début (optionnel)
            date_fin: datetime, date de fin (optionnel)

        Returns:
            dict: Statistiques des contestations
        """
        from django.db.models import Count

        # Construire la requête de base
        queryset = Contestation.objects.all()

        if date_debut:
            queryset = queryset.filter(date_soumission__gte=date_debut)

        if date_fin:
            queryset = queryset.filter(date_soumission__lte=date_fin)

        # Calculer les statistiques
        stats = queryset.aggregate(
            total_contestations=Count("id"),
            contestations_en_attente=Count("id", filter=queryset.filter(statut="EN_ATTENTE").query),
            contestations_en_examen=Count("id", filter=queryset.filter(statut="EN_EXAMEN").query),
            contestations_acceptees=Count("id", filter=queryset.filter(statut="ACCEPTEE").query),
            contestations_rejetees=Count("id", filter=queryset.filter(statut="REJETEE").query),
        )

        # Calculer le taux d'acceptation
        total_traitees = (stats["contestations_acceptees"] or 0) + (stats["contestations_rejetees"] or 0)
        taux_acceptation = 0
        if total_traitees > 0:
            taux_acceptation = (stats["contestations_acceptees"] or 0) / total_traitees * 100

        return {
            "total_contestations": stats["total_contestations"] or 0,
            "contestations_en_attente": stats["contestations_en_attente"] or 0,
            "contestations_en_examen": stats["contestations_en_examen"] or 0,
            "contestations_acceptees": stats["contestations_acceptees"] or 0,
            "contestations_rejetees": stats["contestations_rejetees"] or 0,
            "taux_acceptation": round(taux_acceptation, 2),
        }
