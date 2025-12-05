"""
Management command to set up permissions and groups for the contraventions system.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from contraventions.models import (
    AgentControleurProfile,
    Conducteur,
    ConfigurationSysteme,
    Contestation,
    Contravention,
    ContraventionAuditLog,
    DossierFourriere,
    PhotoContravention,
    TypeInfraction,
)


class Command(BaseCommand):
    help = "Configure les groupes et permissions pour le système de contraventions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Configuration des permissions de contraventions..."))

        # Create groups
        self.create_groups()

        # Assign permissions
        self.assign_agent_controleur_permissions()
        self.assign_superviseur_permissions()
        self.assign_admin_permissions()

        self.stdout.write(self.style.SUCCESS("✓ Configuration des permissions terminée avec succès!"))

    def create_groups(self):
        """Create the necessary groups"""
        self.stdout.write("Création des groupes...")

        groups = [
            ("Agent Contrôleur", "Agents de police/gendarmerie autorisés à créer des contraventions"),
            ("Superviseur Police", "Superviseurs pouvant valider les annulations et contestations"),
            ("Administrateur Contraventions", "Administrateurs avec accès complet au système"),
        ]

        for group_name, description in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Groupe créé: {group_name}"))
            else:
                self.stdout.write(f"  - Groupe existant: {group_name}")

    def assign_agent_controleur_permissions(self):
        """Assign permissions to Agent Contrôleur group"""
        self.stdout.write("\nConfiguration des permissions Agent Contrôleur...")

        group = Group.objects.get(name="Agent Contrôleur")

        # Permissions for Contravention
        contravention_ct = ContentType.objects.get_for_model(Contravention)
        permissions = [
            Permission.objects.get(codename="add_contravention", content_type=contravention_ct),
            Permission.objects.get(codename="view_contravention", content_type=contravention_ct),
            Permission.objects.get(codename="change_contravention", content_type=contravention_ct),
        ]

        # Permissions for PhotoContravention
        photo_ct = ContentType.objects.get_for_model(PhotoContravention)
        permissions.extend(
            [
                Permission.objects.get(codename="add_photocontravention", content_type=photo_ct),
                Permission.objects.get(codename="view_photocontravention", content_type=photo_ct),
                Permission.objects.get(codename="delete_photocontravention", content_type=photo_ct),
            ]
        )

        # Permissions for DossierFourriere
        fourriere_ct = ContentType.objects.get_for_model(DossierFourriere)
        permissions.extend(
            [
                Permission.objects.get(codename="add_dossierfourriere", content_type=fourriere_ct),
                Permission.objects.get(codename="view_dossierfourriere", content_type=fourriere_ct),
                Permission.objects.get(codename="change_dossierfourriere", content_type=fourriere_ct),
            ]
        )

        # Permissions for Conducteur
        conducteur_ct = ContentType.objects.get_for_model(Conducteur)
        permissions.extend(
            [
                Permission.objects.get(codename="add_conducteur", content_type=conducteur_ct),
                Permission.objects.get(codename="view_conducteur", content_type=conducteur_ct),
            ]
        )

        # Permissions for TypeInfraction (view only)
        infraction_ct = ContentType.objects.get_for_model(TypeInfraction)
        permissions.append(Permission.objects.get(codename="view_typeinfraction", content_type=infraction_ct))

        # Assign permissions
        group.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {len(permissions)} permissions assignées au groupe Agent Contrôleur")
        )

    def assign_superviseur_permissions(self):
        """Assign permissions to Superviseur Police group"""
        self.stdout.write("\nConfiguration des permissions Superviseur Police...")

        group = Group.objects.get(name="Superviseur Police")

        # All Agent Contrôleur permissions
        agent_group = Group.objects.get(name="Agent Contrôleur")
        permissions = list(agent_group.permissions.all())

        # Additional permissions for Contravention (delete/cancel)
        contravention_ct = ContentType.objects.get_for_model(Contravention)
        permissions.append(Permission.objects.get(codename="delete_contravention", content_type=contravention_ct))

        # Permissions for Contestation
        contestation_ct = ContentType.objects.get_for_model(Contestation)
        permissions.extend(
            [
                Permission.objects.get(codename="view_contestation", content_type=contestation_ct),
                Permission.objects.get(codename="change_contestation", content_type=contestation_ct),
            ]
        )

        # Permissions for ContraventionAuditLog (view only)
        audit_ct = ContentType.objects.get_for_model(ContraventionAuditLog)
        permissions.append(Permission.objects.get(codename="view_contraventionauditlog", content_type=audit_ct))

        # Assign permissions
        group.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {len(permissions)} permissions assignées au groupe Superviseur Police")
        )

    def assign_admin_permissions(self):
        """Assign permissions to Administrateur Contraventions group"""
        self.stdout.write("\nConfiguration des permissions Administrateur Contraventions...")

        group = Group.objects.get(name="Administrateur Contraventions")

        # Get all permissions for all contraventions models
        models = [
            TypeInfraction,
            AgentControleurProfile,
            Conducteur,
            Contravention,
            DossierFourriere,
            PhotoContravention,
            Contestation,
            ContraventionAuditLog,
            ConfigurationSysteme,
        ]

        permissions = []
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            model_permissions = Permission.objects.filter(content_type=ct)
            permissions.extend(model_permissions)

        # Assign all permissions
        group.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {len(permissions)} permissions assignées au groupe Administrateur Contraventions")
        )

        self.stdout.write(
            self.style.WARNING("\n⚠ Note: Les administrateurs ont accès complet à tous les modèles de contraventions")
        )
