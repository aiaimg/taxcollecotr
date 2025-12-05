from django.core.management.base import BaseCommand

from vehicles.models import Vehicule


class Command(BaseCommand):
    help = "Populate nom_proprietaire field for existing vehicles from user data"

    def handle(self, *args, **options):
        vehicles = Vehicule.objects.filter(nom_proprietaire="")
        count = 0

        for vehicle in vehicles:
            # Use the user's full name or username as the owner name
            owner_name = vehicle.proprietaire.get_full_name() or vehicle.proprietaire.username
            vehicle.nom_proprietaire = owner_name
            vehicle.save(update_fields=["nom_proprietaire"])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully populated owner names for {count} vehicles"))
