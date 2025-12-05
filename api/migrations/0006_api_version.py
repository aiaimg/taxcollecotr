from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_webhooks"),
    ]

    operations = [
        migrations.CreateModel(
            name="APIVersion",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.CharField(max_length=20, db_index=True)),
                ("released_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("summary", models.CharField(max_length=255, blank=True)),
                ("changes", models.JSONField(default=list, blank=True, help_text="List of changes for this release")),
                ("deprecated_endpoints", models.JSONField(default=list, blank=True, help_text="List of endpoint patterns deprecated in this release")),
                ("notify_emails", models.JSONField(default=list, blank=True, help_text="Optional list of recipients to notify")),
            ],
            options={
                "db_table": "api_versions",
                "ordering": ["-released_at"],
            },
        ),
    ]

