"""
Service de gestion des paiements d'amendes.
Intégration avec les systèmes de paiement existants (MVola, Stripe, Cash).
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from contraventions.models import Contravention, ContraventionAuditLog, DossierFourriere
from payments.models import CashSystemConfig, PaiementTaxe, QRCode
from payments.services.cash_payment_service import CashPaymentService
from payments.services.commission_service import CommissionService
from payments.services.mvola.api_client import MvolaAPIClient
from payments.services.mvola.exceptions import MvolaAPIError, MvolaAuthenticationError

logger = logging.getLogger(__name__)


class PaiementAmendeService:
    """Service pour gérer les paiements d'amendes"""

    @staticmethod
    @transaction.atomic
    def initier_paiement_mvola(contravention, customer_msisdn, user=None, **kwargs):
        """
        Initie un paiement MVola pour une amende.
        Réutilise MvolaAPIClient existant.

        Args:
            contravention: Contravention object
            customer_msisdn: str, numéro de téléphone du client (format: 261XXXXXXXXX)
            user: User object qui initie le paiement (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            dict: {
                'success': bool,
                'paiement': PaiementTaxe object,
                'transaction_id': str,
                'server_correlation_id': str,
                'message': str
            }

        Raises:
            ValidationError: Si les données sont invalides
            MvolaAPIError: Si l'API MVola retourne une erreur
        """
        # Vérifier que la contravention peut être payée
        if contravention.statut == "PAYEE":
            raise ValidationError("Cette contravention a déjà été payée.")

        if contravention.statut == "ANNULEE":
            raise ValidationError("Cette contravention a été annulée et ne peut pas être payée.")

        # Calculer le montant total (amende + pénalités si applicable)
        montant_total = contravention.get_montant_total()

        # Créer l'enregistrement de paiement
        paiement = PaiementTaxe.objects.create(
            type_paiement="AMENDE_CONTRAVENTION",
            contravention=contravention,
            vehicule_plaque=contravention.vehicule if contravention.vehicule else None,
            annee_fiscale=contravention.date_heure_infraction.year,
            montant_du_ariary=montant_total,
            statut="EN_ATTENTE",
            methode_paiement="mvola",
            details_paiement={
                "numero_pv": contravention.numero_pv,
                "type_infraction": contravention.type_infraction.nom,
                "customer_msisdn": customer_msisdn,
                "date_initiation": timezone.now().isoformat(),
            },
        )

        try:
            # Initialiser le client MVola
            mvola_client = MvolaAPIClient()

            # Préparer la description
            description = f"Amende PV {contravention.numero_pv}"

            # Initier le paiement via MVola
            response = mvola_client.initiate_payment(
                amount=float(montant_total),
                customer_msisdn=customer_msisdn,
                description=description,
                reference_id=str(paiement.id),
            )

            # Mettre à jour le paiement avec les informations MVola
            paiement.transaction_id = response.get("transaction_id", "")
            paiement.mvola_transaction_ref = response.get("transaction_id", "")
            paiement.mvola_server_correlation_id = response.get("server_correlation_id", "")
            paiement.details_paiement.update(
                {
                    "mvola_response": response,
                    "status": response.get("status", "PENDING"),
                }
            )
            paiement.save()

            # Enregistrer dans l'audit log
            if user:
                ContraventionAuditLog.objects.create(
                    action_type="PAYMENT_INITIATED",
                    user=user,
                    contravention=contravention,
                    action_data={
                        "methode_paiement": "mvola",
                        "montant": str(montant_total),
                        "transaction_id": response.get("transaction_id", ""),
                        "customer_msisdn": customer_msisdn,
                    },
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                )

            logger.info(
                f"Paiement MVola initié pour contravention {contravention.numero_pv}. "
                f"Transaction ID: {response.get('transaction_id')}"
            )

            return {
                "success": True,
                "paiement": paiement,
                "transaction_id": response.get("transaction_id", ""),
                "server_correlation_id": response.get("server_correlation_id", ""),
                "message": "Paiement MVola initié avec succès. Veuillez confirmer sur votre téléphone.",
            }

        except (MvolaAPIError, MvolaAuthenticationError) as e:
            # Marquer le paiement comme échoué
            paiement.statut = "ANNULE"
            paiement.details_paiement["error"] = str(e)
            paiement.save()

            logger.error(f"Erreur lors de l'initiation du paiement MVola: {str(e)}")

            raise ValidationError(f"Erreur lors de l'initiation du paiement MVola: {str(e)}")

    @staticmethod
    @transaction.atomic
    def initier_paiement_stripe(contravention, payment_method_id=None, user=None, **kwargs):
        """
        Initie un paiement Stripe pour une amende.
        Réutilise l'intégration Stripe existante.

        Args:
            contravention: Contravention object
            payment_method_id: str, ID de la méthode de paiement Stripe (optionnel)
            user: User object qui initie le paiement (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            dict: {
                'success': bool,
                'paiement': PaiementTaxe object,
                'client_secret': str,
                'payment_intent_id': str,
                'message': str
            }

        Raises:
            ValidationError: Si les données sont invalides
        """
        import stripe

        # Vérifier que la contravention peut être payée
        if contravention.statut == "PAYEE":
            raise ValidationError("Cette contravention a déjà été payée.")

        if contravention.statut == "ANNULEE":
            raise ValidationError("Cette contravention a été annulée et ne peut pas être payée.")

        # Calculer le montant total
        montant_total = contravention.get_montant_total()

        # Convertir en centimes pour Stripe (Ariary n'a pas de centimes, mais Stripe attend des centimes)
        montant_stripe = int(montant_total * 100)

        # Créer l'enregistrement de paiement
        paiement = PaiementTaxe.objects.create(
            type_paiement="AMENDE_CONTRAVENTION",
            contravention=contravention,
            vehicule_plaque=contravention.vehicule if contravention.vehicule else None,
            annee_fiscale=contravention.date_heure_infraction.year,
            montant_du_ariary=montant_total,
            statut="EN_ATTENTE",
            methode_paiement="carte_bancaire",
            details_paiement={
                "numero_pv": contravention.numero_pv,
                "type_infraction": contravention.type_infraction.nom,
                "date_initiation": timezone.now().isoformat(),
            },
        )

        try:
            # Configurer Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Créer le PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=montant_stripe,
                currency="mga",  # Ariary malgache
                payment_method=payment_method_id,
                confirmation_method="automatic",
                confirm=True if payment_method_id else False,
                metadata={
                    "paiement_id": str(paiement.id),
                    "numero_pv": contravention.numero_pv,
                    "type": "amende_contravention",
                },
                description=f"Amende PV {contravention.numero_pv}",
            )

            # Mettre à jour le paiement avec les informations Stripe
            paiement.stripe_payment_intent_id = payment_intent.id
            paiement.transaction_id = payment_intent.id
            paiement.amount_stripe = montant_stripe
            paiement.details_paiement.update(
                {
                    "stripe_payment_intent_id": payment_intent.id,
                    "stripe_status": payment_intent.status,
                    "client_secret": payment_intent.client_secret,
                }
            )
            paiement.save()

            # Enregistrer dans l'audit log
            if user:
                ContraventionAuditLog.objects.create(
                    action_type="PAYMENT_INITIATED",
                    user=user,
                    contravention=contravention,
                    action_data={
                        "methode_paiement": "stripe",
                        "montant": str(montant_total),
                        "payment_intent_id": payment_intent.id,
                    },
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                )

            logger.info(
                f"Paiement Stripe initié pour contravention {contravention.numero_pv}. "
                f"Payment Intent ID: {payment_intent.id}"
            )

            return {
                "success": True,
                "paiement": paiement,
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "message": "Paiement Stripe initié avec succès.",
            }

        except stripe.error.StripeError as e:
            # Marquer le paiement comme échoué
            paiement.statut = "ANNULE"
            paiement.details_paiement["error"] = str(e)
            paiement.save()

            logger.error(f"Erreur lors de l'initiation du paiement Stripe: {str(e)}")

            raise ValidationError(f"Erreur lors de l'initiation du paiement Stripe: {str(e)}")

    @staticmethod
    @transaction.atomic
    def enregistrer_paiement_cash(contravention, agent_partenaire, montant_remis, cash_session, user=None, **kwargs):
        """
        Enregistre un paiement en espèces via un agent partenaire.
        Réutilise le système CashSession/CashTransaction.

        Args:
            contravention: Contravention object
            agent_partenaire: AgentPartenaireProfile object
            montant_remis: Decimal, montant remis par le client
            cash_session: CashSession object (session ouverte de l'agent)
            user: User object (l'agent partenaire)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            dict: {
                'success': bool,
                'paiement': PaiementTaxe object,
                'cash_transaction': CashTransaction object,
                'monnaie': Decimal,
                'message': str
            }

        Raises:
            ValidationError: Si les données sont invalides
        """
        from payments.models import CashTransaction

        # Vérifier que la contravention peut être payée
        if contravention.statut == "PAYEE":
            raise ValidationError("Cette contravention a déjà été payée.")

        if contravention.statut == "ANNULEE":
            raise ValidationError("Cette contravention a été annulée et ne peut pas être payée.")

        # Vérifier que la session est ouverte
        if cash_session.status != "open":
            raise ValidationError("La session de caisse n'est pas ouverte.")

        # Calculer le montant total
        montant_total = contravention.get_montant_total()

        # Calculer la monnaie
        monnaie, is_valid, error_msg = CashPaymentService.calculate_change(
            tax_amount=montant_total, amount_tendered=montant_remis
        )

        if not is_valid:
            raise ValidationError(error_msg)

        # Créer l'enregistrement de paiement
        paiement = PaiementTaxe.objects.create(
            type_paiement="AMENDE_CONTRAVENTION",
            contravention=contravention,
            vehicule_plaque=contravention.vehicule if contravention.vehicule else None,
            annee_fiscale=contravention.date_heure_infraction.year,
            montant_du_ariary=montant_total,
            montant_paye_ariary=montant_total,
            date_paiement=timezone.now(),
            statut="PAYE",
            methode_paiement="cash",
            details_paiement={
                "numero_pv": contravention.numero_pv,
                "type_infraction": contravention.type_infraction.nom,
                "agent_partenaire": agent_partenaire.nom_complet,
                "montant_remis": str(montant_remis),
                "monnaie": str(monnaie),
                "date_paiement": timezone.now().isoformat(),
            },
        )

        # Générer un transaction_id unique
        import uuid

        paiement.transaction_id = f"CASH-{uuid.uuid4().hex[:12].upper()}"
        paiement.save()

        # Créer la transaction de caisse
        cash_transaction = CashTransaction.objects.create(
            session=cash_session,
            paiement=paiement,
            amount_due=montant_total,
            amount_tendered=montant_remis,
            change_given=monnaie,
            transaction_type="AMENDE",
            status="completed",
            notes=f"Paiement amende PV {contravention.numero_pv}",
        )

        # Calculer la commission pour l'agent partenaire
        config = CashSystemConfig.get_config()
        commission = CommissionService.calculate_commission(
            amount=montant_total, commission_rate=config.commission_rate
        )

        # Enregistrer la commission
        CommissionService.record_commission(
            transaction=cash_transaction, collector=agent_partenaire, amount=montant_total, commission_amount=commission
        )

        # Mettre à jour le statut de la contravention
        contravention.statut = "PAYEE"
        contravention.date_paiement = timezone.now()
        contravention.save()

        # Enregistrer dans l'audit log
        if user:
            ContraventionAuditLog.objects.create(
                action_type="PAYMENT_COMPLETED",
                user=user,
                contravention=contravention,
                action_data={
                    "methode_paiement": "cash",
                    "montant": str(montant_total),
                    "montant_remis": str(montant_remis),
                    "monnaie": str(monnaie),
                    "agent_partenaire": agent_partenaire.nom_complet,
                    "commission": str(commission),
                },
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
            )

        logger.info(
            f"Paiement cash enregistré pour contravention {contravention.numero_pv}. "
            f"Montant: {montant_total} Ariary, Commission: {commission} Ariary"
        )

        return {
            "success": True,
            "paiement": paiement,
            "cash_transaction": cash_transaction,
            "monnaie": monnaie,
            "commission": commission,
            "message": "Paiement en espèces enregistré avec succès.",
        }

    @staticmethod
    @transaction.atomic
    def confirmer_paiement(contravention, paiement, user=None, **kwargs):
        """
        Confirme le paiement d'une amende.
        - Met à jour le statut de la contravention
        - Génère le reçu avec QR code
        - Envoie les notifications

        Args:
            contravention: Contravention object
            paiement: PaiementTaxe object
            user: User object (optionnel)
            **kwargs: paramètres optionnels (ip_address, user_agent)

        Returns:
            dict: {
                'success': bool,
                'qr_code': QRCode object,
                'message': str
            }

        Raises:
            ValidationError: Si les données sont invalides
        """
        # Vérifier que le paiement est bien pour cette contravention
        if paiement.contravention != contravention:
            raise ValidationError("Le paiement ne correspond pas à cette contravention.")

        # Vérifier que le paiement est confirmé
        if paiement.statut != "PAYE":
            raise ValidationError("Le paiement n'est pas confirmé.")

        # Mettre à jour le statut de la contravention
        contravention.statut = "PAYEE"
        contravention.date_paiement = timezone.now()
        contravention.save()

        # Générer le QR code du reçu
        qr_code = PaiementAmendeService._generer_qr_code_recu(contravention, paiement)

        # Mettre à jour le paiement avec le QR code
        if qr_code:
            paiement.qr_code = qr_code
            paiement.save()

        # Enregistrer dans l'audit log
        if user:
            ContraventionAuditLog.objects.create(
                action_type="PAYMENT_CONFIRMED",
                user=user,
                contravention=contravention,
                action_data={
                    "paiement_id": str(paiement.id),
                    "montant": str(paiement.montant_paye_ariary or paiement.montant_du_ariary),
                    "methode_paiement": paiement.methode_paiement,
                    "transaction_id": paiement.transaction_id,
                },
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
            )

        # Envoyer les notifications
        PaiementAmendeService._envoyer_notifications_paiement(contravention, paiement)

        logger.info(
            f"Paiement confirmé pour contravention {contravention.numero_pv}. "
            f"Montant: {paiement.montant_paye_ariary or paiement.montant_du_ariary} Ariary"
        )

        return {"success": True, "qr_code": qr_code, "message": "Paiement confirmé avec succès. Reçu généré."}

    @staticmethod
    def _generer_qr_code_recu(contravention, paiement):
        """
        Génère un QR code pour le reçu de paiement.

        Args:
            contravention: Contravention object
            paiement: PaiementTaxe object

        Returns:
            QRCode object ou None
        """
        try:
            # Générer l'URL de vérification du reçu
            verification_url = f"/contraventions/recu/{paiement.transaction_id}/"

            qr_code = QRCode.objects.create(
                code=paiement.transaction_id,
                type_code="RECU_AMENDE",
                data={
                    "numero_pv": contravention.numero_pv,
                    "transaction_id": paiement.transaction_id,
                    "montant_paye": str(paiement.montant_paye_ariary or paiement.montant_du_ariary),
                    "date_paiement": (
                        paiement.date_paiement.isoformat() if paiement.date_paiement else timezone.now().isoformat()
                    ),
                    "methode_paiement": paiement.methode_paiement,
                    "verification_url": verification_url,
                },
            )
            return qr_code
        except Exception as e:
            logger.error(f"Erreur lors de la création du QR code du reçu: {str(e)}")
            return None

    @staticmethod
    def _envoyer_notifications_paiement(contravention, paiement):
        """
        Envoie les notifications de confirmation de paiement.

        Args:
            contravention: Contravention object
            paiement: PaiementTaxe object
        """
        try:
            from notifications.services import NotificationService

            # Notification au conducteur (si compte utilisateur)
            if hasattr(contravention.conducteur, "user"):
                user = contravention.conducteur.user
                langue = "fr"
                if hasattr(user, "profile") and hasattr(user.profile, "langue_preferee"):
                    langue = user.profile.langue_preferee

                titre = "Paiement confirmé" if langue == "fr" else "Paiement confirmé"
                message = (
                    f"Votre paiement pour la contravention {contravention.numero_pv} a été confirmé. "
                    f"Montant: {paiement.montant_paye_ariary or paiement.montant_du_ariary} Ariary. "
                    f"Reçu disponible en ligne."
                )

                NotificationService.create_notification(
                    user=user, titre=titre, message=message, type_notification="SUCCESS", langue=langue
                )

            # Notification au propriétaire du véhicule (si différent du conducteur)
            elif contravention.vehicule and contravention.vehicule.proprietaire:
                user = contravention.vehicule.proprietaire
                langue = "fr"
                if hasattr(user, "profile") and hasattr(user.profile, "langue_preferee"):
                    langue = user.profile.langue_preferee

                titre = "Paiement confirmé" if langue == "fr" else "Paiement confirmé"
                message = (
                    f"Le paiement pour la contravention {contravention.numero_pv} de votre véhicule a été confirmé. "
                    f"Montant: {paiement.montant_paye_ariary or paiement.montant_du_ariary} Ariary."
                )

                NotificationService.create_notification(
                    user=user, titre=titre, message=message, type_notification="SUCCESS", langue=langue
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des notifications de paiement: {str(e)}")

    @staticmethod
    def calculer_frais_plateforme(montant, methode_paiement):
        """
        Calcule les frais de plateforme selon la méthode de paiement.

        Args:
            montant: Decimal, montant de l'amende
            methode_paiement: str, méthode de paiement

        Returns:
            Decimal: Montant des frais de plateforme
        """
        # Récupérer la configuration des frais
        if methode_paiement == "mvola":
            # Frais MVola (à configurer selon le contrat)
            taux_frais = Decimal("0.02")  # 2%
            frais = montant * taux_frais
        elif methode_paiement == "carte_bancaire":
            # Frais Stripe (à configurer selon le contrat)
            taux_frais = Decimal("0.029")  # 2.9%
            frais_fixes = Decimal("100")  # 100 Ariary
            frais = (montant * taux_frais) + frais_fixes
        elif methode_paiement == "cash":
            # Commission pour agent partenaire
            config = CashSystemConfig.get_config()
            frais = montant * (config.commission_rate / Decimal("100"))
        else:
            frais = Decimal("0")

        return frais.quantize(Decimal("0.01"))
