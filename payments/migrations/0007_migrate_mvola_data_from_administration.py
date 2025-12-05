# Generated migration to copy data from administration.MvolaConfiguration to payments.MvolaConfiguration

from django.db import migrations


def copy_mvola_config_data(apps, schema_editor):
    """Copy data from administration.MvolaConfiguration to payments.MvolaConfiguration"""
    AdministrationMvolaConfig = apps.get_model('administration', 'MvolaConfiguration')
    PaymentsMvolaConfig = apps.get_model('payments', 'MvolaConfiguration')
    
    # Only copy if administration model still exists (it will be deleted in next migration)
    try:
        admin_configs = AdministrationMvolaConfig.objects.all()
        if admin_configs.exists():
            # Copy all existing configurations
            configs_to_create = []
            for admin_config in admin_configs:
                configs_to_create.append(
                    PaymentsMvolaConfig(
                        name=admin_config.name,
                        environment=admin_config.environment,
                        consumer_key=admin_config.consumer_key,
                        consumer_secret=admin_config.consumer_secret,
                        merchant_msisdn=admin_config.merchant_msisdn,
                        merchant_name=admin_config.merchant_name,
                        base_url=admin_config.base_url,
                        callback_url=admin_config.callback_url,
                        min_amount=admin_config.min_amount,
                        max_amount=admin_config.max_amount,
                        platform_fee_percentage=admin_config.platform_fee_percentage,
                        logo=admin_config.logo,
                        is_active=admin_config.is_active,
                        is_enabled=admin_config.is_enabled,
                        is_verified=admin_config.is_verified,
                        last_test_date=admin_config.last_test_date,
                        last_test_result=admin_config.last_test_result,
                        total_transactions=admin_config.total_transactions,
                        successful_transactions=admin_config.successful_transactions,
                        failed_transactions=admin_config.failed_transactions,
                        total_amount_processed=admin_config.total_amount_processed,
                        description=admin_config.description,
                        created_by=admin_config.created_by,
                        modified_by=admin_config.modified_by,
                        created_at=admin_config.created_at,
                        updated_at=admin_config.updated_at,
                    )
                )
            # Bulk create for efficiency
            if configs_to_create:
                PaymentsMvolaConfig.objects.bulk_create(configs_to_create)
    except Exception:
        # If administration model doesn't exist yet or has been deleted, skip
        # This handles the case where migrations are run on a fresh database
        pass


def reverse_copy_mvola_config_data(apps, schema_editor):
    """Reverse: copy data back from payments to administration (if needed)"""
    # This is a one-way migration, so reverse is a no-op
    # The administration model will be deleted in a separate migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_add_mvola_configuration'),
        ('administration', '0004_add_mvola_configuration'),  # Ensure administration model exists
    ]

    operations = [
        migrations.RunPython(copy_mvola_config_data, reverse_copy_mvola_config_data),
    ]

