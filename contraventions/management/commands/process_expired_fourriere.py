from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from contraventions.models import Contravention, DossierFourriere


class Command(BaseCommand):
    help = "Traite les dossiers de fourrière arrivés à échéance"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Affiche les actions sans les exécuter")
        parser.add_argument(
            "--days-before", type=int, default=0, help="Nombre de jours avant l'échéance pour traiter (par défaut: 0)"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        days_before = options["days_before"]

        self.stdout.write("Traitement des dossiers de fourrière...")

        # Calculate the deadline date
        deadline_date = timezone.now() + timedelta(days=days_before)

        # Find fourrière cases that have reached their maximum duration
        expired_fourrieres = DossierFourriere.objects.filter(
            statut="en_fourriere", date_mise_fourriere__lte=deadline_date - timedelta(days=30)  # 30 days max duration
        )

        self.stdout.write(f"{expired_fourrieres.count()} dossiers trouvés")

        for fourriere in expired_fourrieres:
            days_elapsed = (timezone.now() - fourriere.date_mise_fourriere).days

            if days_elapsed >= fourriere.duree_maximale_jours:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[DRY RUN] Dossier {fourriere.numero_dossier} expiré " f"({days_elapsed} jours écoulés)"
                        )
                    )
                else:
                    # Mark for sale notification
                    fourriere.observations += f'\n\n[SYSTEM] Dossier expiré le {timezone.now().strftime("%d/%m/%Y")}. '
                    fourriere.observations += "Notification de vente envoyée."
                    fourriere.save()

                    # Here you would typically:
                    # 1. Send notification to vehicle owner
                    # 2. Create sale process
                    # 3. Update status to 'a_vendre'

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Dossier {fourriere.numero_dossier} marqué pour vente " f"({days_elapsed} jours écoulés)"
                        )
                    )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("Traitement des dossiers de fourrière terminé"))
        else:
            self.stdout.write(self.style.WARNING("Mode dry-run - aucune modification effectuée"))
