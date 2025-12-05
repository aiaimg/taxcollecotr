"""
Payment services for Mobile Money integration
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils.translation import gettext_lazy as _

import requests

logger = logging.getLogger(__name__)


class MobileMoneyService:
    """Base class for Mobile Money services"""

    def __init__(self):
        self.timeout = 30
        self.max_retries = 3

    def generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        return f"TXN_{uuid.uuid4().hex[:12].upper()}"

    def validate_phone_number(self, phone: str, operator: str) -> bool:
        """Validate phone number format for specific operator"""
        if not phone or len(phone) < 10:
            return False

        # Remove spaces and special characters
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        # Madagascar phone number validation
        if operator == "mvola":
            return phone.startswith("034") or phone.startswith("261034")
        elif operator == "orange_money":
            return (
                phone.startswith("032")
                or phone.startswith("037")
                or phone.startswith("261032")
                or phone.startswith("261037")
            )
        elif operator == "airtel_money":
            return phone.startswith("033") or phone.startswith("261033")

        return False

    def format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")
        if phone.startswith("261"):
            return phone
        elif phone.startswith("0"):
            return f"261{phone[1:]}"
        else:
            return f"261{phone}"


class MVolaService(MobileMoneyService):
    """MVola Mobile Money service integration"""

    def __init__(self):
        super().__init__()
        self.api_url = getattr(settings, "MVOLA_API_URL", "https://api.mvola.mg/v1")
        self.merchant_id = getattr(settings, "MVOLA_MERCHANT_ID", "")
        self.api_key = getattr(settings, "MVOLA_API_KEY", "")
        self.secret_key = getattr(settings, "MVOLA_SECRET_KEY", "")

    def initiate_payment(self, amount: float, phone: str, reference: str, description: str = "") -> Dict[str, Any]:
        """Initiate MVola payment"""
        try:
            if not self.validate_phone_number(phone, "mvola"):
                return {"success": False, "error": _("Numéro de téléphone MVola invalide")}

            formatted_phone = self.format_phone_number(phone)
            transaction_id = self.generate_transaction_id()

            # In a real implementation, you would make an API call to MVola
            # For now, we'll simulate the response
            if settings.DEBUG:
                # Simulate successful initiation for development
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_url": f"{self.api_url}/payment/{transaction_id}",
                    "status": "INITIATED",
                    "message": _("Paiement MVola initié avec succès"),
                }

            # Real API call would go here
            payload = {
                "merchant_id": self.merchant_id,
                "amount": int(amount),
                "currency": "MGA",
                "phone_number": formatted_phone,
                "reference": reference,
                "description": description or f"Taxe véhicule - {reference}",
                "transaction_id": transaction_id,
                "callback_url": f"{settings.SITE_URL}/api/payments/callback/mvola/",
                "return_url": f"{settings.SITE_URL}/payments/success/",
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Merchant-ID": self.merchant_id,
            }

            response = requests.post(
                f"{self.api_url}/payments/initiate", json=payload, headers=headers, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "transaction_id": data.get("transaction_id", transaction_id),
                    "payment_url": data.get("payment_url"),
                    "status": data.get("status", "INITIATED"),
                    "message": _("Paiement MVola initié avec succès"),
                }
            else:
                logger.error(f"MVola API error: {response.status_code} - {response.text}")
                return {"success": False, "error": _("Erreur lors de l'initiation du paiement MVola")}

        except requests.RequestException as e:
            logger.error(f"MVola request error: {str(e)}")
            return {"success": False, "error": _("Erreur de connexion au service MVola")}
        except Exception as e:
            logger.error(f"MVola unexpected error: {str(e)}")
            return {"success": False, "error": _("Erreur inattendue lors du paiement MVola")}

    def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check MVola payment status"""
        try:
            if settings.DEBUG:
                # Simulate payment status for development
                return {
                    "success": True,
                    "status": "COMPLETED",
                    "transaction_id": transaction_id,
                    "amount": 0,
                    "currency": "MGA",
                    "payment_date": datetime.now().isoformat(),
                }

            headers = {"Authorization": f"Bearer {self.api_key}", "X-Merchant-ID": self.merchant_id}

            response = requests.get(
                f"{self.api_url}/payments/{transaction_id}/status", headers=headers, timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": _("Impossible de vérifier le statut du paiement")}

        except Exception as e:
            logger.error(f"MVola status check error: {str(e)}")
            return {"success": False, "error": _("Erreur lors de la vérification du statut")}


class OrangeMoneyService(MobileMoneyService):
    """Orange Money service integration"""

    def __init__(self):
        super().__init__()
        self.api_url = getattr(settings, "ORANGE_MONEY_API_URL", "https://api.orange.mg/v1")
        self.merchant_id = getattr(settings, "ORANGE_MONEY_MERCHANT_ID", "")
        self.api_key = getattr(settings, "ORANGE_MONEY_API_KEY", "")

    def initiate_payment(self, amount: float, phone: str, reference: str, description: str = "") -> Dict[str, Any]:
        """Initiate Orange Money payment"""
        try:
            if not self.validate_phone_number(phone, "orange_money"):
                return {"success": False, "error": _("Numéro de téléphone Orange Money invalide")}

            formatted_phone = self.format_phone_number(phone)
            transaction_id = self.generate_transaction_id()

            if settings.DEBUG:
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_url": f"{self.api_url}/payment/{transaction_id}",
                    "status": "INITIATED",
                    "message": _("Paiement Orange Money initié avec succès"),
                }

            # Real implementation would make API call here
            payload = {
                "merchant_id": self.merchant_id,
                "amount": int(amount),
                "currency": "MGA",
                "phone_number": formatted_phone,
                "reference": reference,
                "description": description or f"Taxe véhicule - {reference}",
                "transaction_id": transaction_id,
            }

            # API call implementation...
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "INITIATED",
                "message": _("Paiement Orange Money initié avec succès"),
            }

        except Exception as e:
            logger.error(f"Orange Money error: {str(e)}")
            return {"success": False, "error": _("Erreur lors du paiement Orange Money")}

    def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Orange Money payment status"""
        if settings.DEBUG:
            return {
                "success": True,
                "status": "COMPLETED",
                "transaction_id": transaction_id,
                "amount": 0,
                "currency": "MGA",
                "payment_date": datetime.now().isoformat(),
            }

        # Real implementation...
        return {"success": True, "status": "PENDING"}


class AirtelMoneyService(MobileMoneyService):
    """Airtel Money service integration"""

    def __init__(self):
        super().__init__()
        self.api_url = getattr(settings, "AIRTEL_MONEY_API_URL", "https://api.airtel.mg/v1")
        self.merchant_id = getattr(settings, "AIRTEL_MONEY_MERCHANT_ID", "")
        self.api_key = getattr(settings, "AIRTEL_MONEY_API_KEY", "")

    def initiate_payment(self, amount: float, phone: str, reference: str, description: str = "") -> Dict[str, Any]:
        """Initiate Airtel Money payment"""
        try:
            if not self.validate_phone_number(phone, "airtel_money"):
                return {"success": False, "error": _("Numéro de téléphone Airtel Money invalide")}

            formatted_phone = self.format_phone_number(phone)
            transaction_id = self.generate_transaction_id()

            if settings.DEBUG:
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "payment_url": f"{self.api_url}/payment/{transaction_id}",
                    "status": "INITIATED",
                    "message": _("Paiement Airtel Money initié avec succès"),
                }

            # Real implementation would make API call here
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "INITIATED",
                "message": _("Paiement Airtel Money initié avec succès"),
            }

        except Exception as e:
            logger.error(f"Airtel Money error: {str(e)}")
            return {"success": False, "error": _("Erreur lors du paiement Airtel Money")}

    def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check Airtel Money payment status"""
        if settings.DEBUG:
            return {
                "success": True,
                "status": "COMPLETED",
                "transaction_id": transaction_id,
                "amount": 0,
                "currency": "MGA",
                "payment_date": datetime.now().isoformat(),
            }

        # Real implementation...
        return {"success": True, "status": "PENDING"}


class PaymentServiceFactory:
    """Factory for creating payment service instances"""

    @staticmethod
    def get_service(payment_method: str):
        """Get payment service instance based on method"""
        services = {"mvola": MVolaService, "orange_money": OrangeMoneyService, "airtel_money": AirtelMoneyService}

        service_class = services.get(payment_method)
        if not service_class:
            raise ValueError(f"Unsupported payment method: {payment_method}")

        return service_class()

    @staticmethod
    def initiate_payment(
        payment_method: str, amount: float, phone: str, reference: str, description: str = ""
    ) -> Dict[str, Any]:
        """Initiate payment using specified method"""
        try:
            service = PaymentServiceFactory.get_service(payment_method)
            return service.initiate_payment(amount, phone, reference, description)
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}")
            return {"success": False, "error": _("Erreur lors de l'initiation du paiement")}

    @staticmethod
    def check_payment_status(payment_method: str, transaction_id: str) -> Dict[str, Any]:
        """Check payment status using specified method"""
        try:
            service = PaymentServiceFactory.get_service(payment_method)
            return service.check_payment_status(transaction_id)
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Payment status check error: {str(e)}")
            return {"success": False, "error": _("Erreur lors de la vérification du statut")}
