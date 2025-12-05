"""
Management command to display QR codes for testing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from payments.models import QRCode


class Command(BaseCommand):
    help = "Display QR codes for testing verification"

    def add_arguments(self, parser):
        parser.add_argument("--active-only", action="store_true", help="Show only active QR codes")
        parser.add_argument("--limit", type=int, default=10, help="Number of QR codes to display")

    def handle(self, *args, **options):
        active_only = options["active_only"]
        limit = options["limit"]

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("QR Codes for Testing"))
        self.stdout.write("=" * 80)
        self.stdout.write("")

        # Get QR codes
        qr_codes = QRCode.objects.all()

        if active_only:
            qr_codes = qr_codes.filter(est_actif=True)

        qr_codes = qr_codes.select_related("vehicule_plaque", "vehicule_plaque__proprietaire").order_by(
            "-date_generation"
        )[:limit]

        if not qr_codes.exists():
            self.stdout.write(self.style.WARNING("No QR codes found!"))
            self.stdout.write("Run: python manage.py create_test_data --create-agent")
            return

        now = timezone.now()

        for i, qr in enumerate(qr_codes, 1):
            # Determine status
            if not qr.est_actif:
                status = "❌ Inactive"
                status_color = self.style.ERROR
            elif qr.date_expiration < now:
                status = "⏰ Expired"
                status_color = self.style.WARNING
            else:
                status = "✅ Valid"
                status_color = self.style.SUCCESS

            self.stdout.write(f"\n{i}. QR Code: {self.style.HTTP_INFO(qr.token[:16])}...")
            self.stdout.write(f"   Status: {status_color(status)}")
            self.stdout.write(f"   Vehicle: {qr.vehicule_plaque.plaque_immatriculation}")
            self.stdout.write(
                f"   Owner: {qr.vehicule_plaque.proprietaire.get_full_name() or qr.vehicule_plaque.proprietaire.username}"
            )
            self.stdout.write(f"   Type: {qr.vehicule_plaque.type_vehicule.nom}")
            self.stdout.write(f"   Year: {qr.annee_fiscale}")
            self.stdout.write(f"   Expires: {qr.date_expiration.strftime('%d/%m/%Y')}")
            self.stdout.write(f"   Scan Count: {qr.nombre_scans}")

            # Generate scan URL
            scan_url = f"http://127.0.0.1:8000/payments/qr/verify/{qr.token}/"
            self.stdout.write(f"   Scan URL: {self.style.HTTP_INFO(scan_url)}")

            # Generate QR code image URL
            qr_image_url = f"http://127.0.0.1:8000/payments/qr/image/{qr.token}/"
            self.stdout.write(f"   QR Image: {qr_image_url}")

        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(f"Total QR codes shown: {qr_codes.count()}")
        self.stdout.write("=" * 80)
        self.stdout.write("")

        # Show verification instructions
        self.stdout.write("📱 How to Test QR Code Verification:")
        self.stdout.write("")
        self.stdout.write("1. Login as verification agent:")
        self.stdout.write("   Username: agent1")
        self.stdout.write("   Password: agent123")
        self.stdout.write("")
        self.stdout.write("2. Scan QR code using one of these methods:")
        self.stdout.write("   • Use the scan URL above in your browser")
        self.stdout.write("   • Use a QR code scanner app to scan the QR image")
        self.stdout.write("   • Use the verification interface in the admin panel")
        self.stdout.write("")
        self.stdout.write("3. Check verification logs:")
        self.stdout.write("   http://127.0.0.1:8000/admin/administration/verificationqr/")
        self.stdout.write("")
