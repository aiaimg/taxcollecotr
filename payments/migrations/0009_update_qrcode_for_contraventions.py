# Generated manually for contravention QR code support

from django.db import migrations, models
import django.db.models.deletion


def populate_code_field(apps, schema_editor):
    """Populate the code field for existing QRCode records"""
    QRCode = apps.get_model('payments', 'QRCode')
    
    # For existing records, copy token to code field
    for qr in QRCode.objects.all():
        if qr.token:
            qr.code = qr.token
            qr.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_modify_paiementtaxe_for_contraventions'),
        ('vehicles', '0001_initial'),
    ]

    operations = [
        # Add type_code field
        migrations.AddField(
            model_name='qrcode',
            name='type_code',
            field=models.CharField(
                choices=[('TAXE_VEHICULE', 'Taxe véhicule'), ('CONTRAVENTION', 'Contravention')],
                default='TAXE_VEHICULE',
                max_length=30,
                verbose_name='Type de QR code'
            ),
        ),
        # Add code field with temporary default
        migrations.AddField(
            model_name='qrcode',
            name='code',
            field=models.CharField(
                default='',
                max_length=255,
                verbose_name='Code unique',
                help_text='Numéro PV pour contravention ou token pour taxe véhicule'
            ),
            preserve_default=False,
        ),
        # Add data field
        migrations.AddField(
            model_name='qrcode',
            name='data',
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name='Données additionnelles',
                help_text='Données spécifiques au type de QR code'
            ),
        ),
        # Populate code field from token for existing records
        migrations.RunPython(populate_code_field, migrations.RunPython.noop),
        # Make code field unique after population
        migrations.AlterField(
            model_name='qrcode',
            name='code',
            field=models.CharField(
                max_length=255,
                unique=True,
                verbose_name='Code unique',
                help_text='Numéro PV pour contravention ou token pour taxe véhicule'
            ),
        ),
        # Make vehicule_plaque nullable
        migrations.AlterField(
            model_name='qrcode',
            name='vehicule_plaque',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='qr_codes',
                to='vehicles.vehicule',
                to_field='plaque_immatriculation'
            ),
        ),
        # Make annee_fiscale nullable
        migrations.AlterField(
            model_name='qrcode',
            name='annee_fiscale',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name='Année fiscale'
            ),
        ),
        # Make token nullable and non-unique temporarily
        migrations.AlterField(
            model_name='qrcode',
            name='token',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='Token de vérification'
            ),
        ),
        # Make date_expiration nullable
        migrations.AlterField(
            model_name='qrcode',
            name='date_expiration',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Date d'expiration"
            ),
        ),
        # Remove old unique_together constraint
        migrations.AlterUniqueTogether(
            name='qrcode',
            unique_together=set(),
        ),
        # Add new index for type_code
        migrations.AddIndex(
            model_name='qrcode',
            index=models.Index(fields=['type_code'], name='payments_qr_type_co_idx'),
        ),
        # Add new index for code
        migrations.AddIndex(
            model_name='qrcode',
            index=models.Index(fields=['code'], name='payments_qr_code_idx'),
        ),
    ]
