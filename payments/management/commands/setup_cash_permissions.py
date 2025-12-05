"""
Management command to set up permission groups for cash payment system
Creates "Agent Partenaire" and "Admin Staff" groups with appropriate permissions
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from payments.models import (
    AgentPartenaireProfile,
    CashAuditLog,
    CashReceipt,
    CashSession,
    CashSystemConfig,
    CashTransaction,
    CommissionRecord,
)


class Command(BaseCommand):
    help = "Set up permission groups for cash payment system"

    def handle(self, *args, **options):
        self.stdout.write("Setting up cash payment permission groups...")

        # Create Agent Partenaire group
        agent_group, created = Group.objects.get_or_create(name="Agent Partenaire")
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Agent Partenaire" group'))
        else:
            self.stdout.write("Agent Partenaire group already exists")

        # Create Admin Staff group
        admin_group, created = Group.objects.get_or_create(name="Admin Staff")
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Admin Staff" group'))
        else:
            self.stdout.write("Admin Staff group already exists")

        # Clear existing permissions
        agent_group.permissions.clear()
        admin_group.permissions.clear()

        # Get content types
        agent_profile_ct = ContentType.objects.get_for_model(AgentPartenaireProfile)
        cash_session_ct = ContentType.objects.get_for_model(CashSession)
        cash_transaction_ct = ContentType.objects.get_for_model(CashTransaction)
        cash_receipt_ct = ContentType.objects.get_for_model(CashReceipt)
        commission_record_ct = ContentType.objects.get_for_model(CommissionRecord)
        cash_audit_log_ct = ContentType.objects.get_for_model(CashAuditLog)
        cash_system_config_ct = ContentType.objects.get_for_model(CashSystemConfig)

        # ====================================================================
        # AGENT PARTENAIRE PERMISSIONS
        # ====================================================================
        agent_permissions = []

        # CashSession permissions - can manage their own sessions
        agent_permissions.extend(
            [
                Permission.objects.get(content_type=cash_session_ct, codename="add_cashsession"),
                Permission.objects.get(content_type=cash_session_ct, codename="view_cashsession"),
                Permission.objects.get(content_type=cash_session_ct, codename="change_cashsession"),
            ]
        )

        # CashTransaction permissions - can create and view transactions
        agent_permissions.extend(
            [
                Permission.objects.get(content_type=cash_transaction_ct, codename="add_cashtransaction"),
                Permission.objects.get(content_type=cash_transaction_ct, codename="view_cashtransaction"),
            ]
        )

        # CashReceipt permissions - can create and view receipts
        agent_permissions.extend(
            [
                Permission.objects.get(content_type=cash_receipt_ct, codename="add_cashreceipt"),
                Permission.objects.get(content_type=cash_receipt_ct, codename="view_cashreceipt"),
            ]
        )

        # CommissionRecord permissions - can view their own commission
        agent_permissions.append(
            Permission.objects.get(content_type=commission_record_ct, codename="view_commissionrecord")
        )

        # View their own agent profile
        agent_permissions.append(
            Permission.objects.get(content_type=agent_profile_ct, codename="view_agentpartenaireprofile")
        )

        # View system config (read-only)
        agent_permissions.append(
            Permission.objects.get(content_type=cash_system_config_ct, codename="view_cashsystemconfig")
        )

        # Add permissions to Agent Partenaire group
        agent_group.permissions.set(agent_permissions)
        self.stdout.write(self.style.SUCCESS(f"Added {len(agent_permissions)} permissions to Agent Partenaire group"))

        # ====================================================================
        # ADMIN STAFF PERMISSIONS (Full access)
        # ====================================================================
        admin_permissions = []

        # AgentPartenaireProfile - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=agent_profile_ct, codename="add_agentpartenaireprofile"),
                Permission.objects.get(content_type=agent_profile_ct, codename="view_agentpartenaireprofile"),
                Permission.objects.get(content_type=agent_profile_ct, codename="change_agentpartenaireprofile"),
                Permission.objects.get(content_type=agent_profile_ct, codename="delete_agentpartenaireprofile"),
            ]
        )

        # CashSession - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=cash_session_ct, codename="add_cashsession"),
                Permission.objects.get(content_type=cash_session_ct, codename="view_cashsession"),
                Permission.objects.get(content_type=cash_session_ct, codename="change_cashsession"),
                Permission.objects.get(content_type=cash_session_ct, codename="delete_cashsession"),
            ]
        )

        # CashTransaction - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=cash_transaction_ct, codename="add_cashtransaction"),
                Permission.objects.get(content_type=cash_transaction_ct, codename="view_cashtransaction"),
                Permission.objects.get(content_type=cash_transaction_ct, codename="change_cashtransaction"),
                Permission.objects.get(content_type=cash_transaction_ct, codename="delete_cashtransaction"),
            ]
        )

        # CashReceipt - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=cash_receipt_ct, codename="add_cashreceipt"),
                Permission.objects.get(content_type=cash_receipt_ct, codename="view_cashreceipt"),
                Permission.objects.get(content_type=cash_receipt_ct, codename="change_cashreceipt"),
                Permission.objects.get(content_type=cash_receipt_ct, codename="delete_cashreceipt"),
            ]
        )

        # CommissionRecord - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=commission_record_ct, codename="add_commissionrecord"),
                Permission.objects.get(content_type=commission_record_ct, codename="view_commissionrecord"),
                Permission.objects.get(content_type=commission_record_ct, codename="change_commissionrecord"),
                Permission.objects.get(content_type=commission_record_ct, codename="delete_commissionrecord"),
            ]
        )

        # CashAuditLog - view only (immutable)
        admin_permissions.append(Permission.objects.get(content_type=cash_audit_log_ct, codename="view_cashauditlog"))

        # CashSystemConfig - full CRUD
        admin_permissions.extend(
            [
                Permission.objects.get(content_type=cash_system_config_ct, codename="add_cashsystemconfig"),
                Permission.objects.get(content_type=cash_system_config_ct, codename="view_cashsystemconfig"),
                Permission.objects.get(content_type=cash_system_config_ct, codename="change_cashsystemconfig"),
                Permission.objects.get(content_type=cash_system_config_ct, codename="delete_cashsystemconfig"),
            ]
        )

        # Add permissions to Admin Staff group
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS(f"Added {len(admin_permissions)} permissions to Admin Staff group"))

        # Summary
        self.stdout.write(self.style.SUCCESS("\n=== Permission Setup Complete ==="))
        self.stdout.write(f"Agent Partenaire: {len(agent_permissions)} permissions")
        self.stdout.write(f"Admin Staff: {len(admin_permissions)} permissions")
        self.stdout.write("\nTo assign users to groups:")
        self.stdout.write('  user.groups.add(Group.objects.get(name="Agent Partenaire"))')
        self.stdout.write('  user.groups.add(Group.objects.get(name="Admin Staff"))')
