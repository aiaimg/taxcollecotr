"""
Commande pour importer les 24 types d'infractions de la Loi n°2017-002.
"""

from django.core.management.base import BaseCommand

from contraventions.services import InfractionService


class Command(BaseCommand):
    help = "Importe les 24 types d'infractions de la Loi n°2017-002 du Code de la Route Malagasy"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Importation des infractions en cours..."))

        try:
            result = InfractionService.importer_infractions_loi_2017()

            if result["success"]:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Importation réussie!"))
                self.stdout.write(f'  - Infractions créées: {result["created"]}')
                self.stdout.write(f'  - Infractions mises à jour: {result["updated"]}')
                self.stdout.write(f'  - Total: {result["total"]}')

                # Afficher le résumé par catégorie
                self.stdout.write(self.style.WARNING("\nRésumé par catégorie:"))
                infractions_grouped = InfractionService.get_infractions_par_categorie()

                categories_labels = {
                    "DELIT_GRAVE": "Délits routiers graves",
                    "CIRCULATION": "Infractions de circulation",
                    "DOCUMENTAIRE": "Infractions documentaires",
                    "SECURITE": "Infractions de sécurité",
                }

                for categorie, label in categories_labels.items():
                    count = len(infractions_grouped.get(categorie, []))
                    self.stdout.write(f"  - {label}: {count} infractions")

            else:
                self.stdout.write(self.style.ERROR("✗ Erreur lors de l'importation"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Erreur: {str(e)}"))
            raise
