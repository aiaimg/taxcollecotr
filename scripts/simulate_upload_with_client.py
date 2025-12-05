import os
import sys
from pathlib import Path

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxcollector_project.settings")
import django

django.setup()

from django.conf import settings

# Allow Django test client host
if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from vehicles.models import DocumentVehicule, Vehicule


def main():
    username = "testuser1"
    password = "TestPass123!"
    plaque = "1234 TAA"

    client = Client()
    if not client.login(username=username, password=password):
        print("CLIENT_LOGIN_FAIL")
        return
    print("CLIENT_LOGIN_OK")

    veh = Vehicule.objects.get(plaque_immatriculation=plaque)
    upload_url = reverse("vehicles:vehicle_document_upload", args=[veh.plaque_immatriculation])
    print("UPLOAD_URL", upload_url)

    # Prepare a simple uploaded file
    su_file = SimpleUploadedFile("sample.jpg", b"fake-image-bytes", content_type="image/jpeg")

    data = {
        "document_type": "photo_plaque",
        "fichier": su_file,
        "note": "Test upload via client",
        "expiration_date": "",
    }

    response = client.post(upload_url, data, follow=False)
    print("UPLOAD_STATUS_CODE", response.status_code)
    print("REDIRECT_LOCATION", response.headers.get("Location"))

    qs = DocumentVehicule.objects.filter(vehicule=veh).order_by("-created_at")
    print("DOC_COUNT", qs.count())
    if qs.exists():
        last = qs.first()
        print("DOC_LAST_TYPE", last.document_type)
        print("DOC_LAST_FILE", last.fichier.name)
    print("DONE")


if __name__ == "__main__":
    main()
