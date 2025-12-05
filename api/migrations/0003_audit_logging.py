from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('api', '0002_increase_api_key_length'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correlation_id', models.CharField(db_index=True, max_length=64)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('endpoint', models.CharField(db_index=True, max_length=512)),
                ('method', models.CharField(max_length=10)),
                ('status_code', models.IntegerField(db_index=True)),
                ('duration_ms', models.IntegerField(blank=True, null=True)),
                ('client_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('request_headers', models.JSONField(blank=True, default=dict)),
                ('request_body', models.JSONField(blank=True, default=dict)),
                ('response_body', models.JSONField(blank=True, default=dict)),
                ('error_type', models.CharField(blank=True, max_length=255)),
                ('error_message', models.TextField(blank=True)),
                ('api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='api.apikey')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='auth.user')),
            ],
            options={
                'db_table': 'api_audit_logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='apiauditlog',
            index=models.Index(fields=['timestamp'], name='api_audit_timestam_idx'),
        ),
        migrations.AddIndex(
            model_name='apiauditlog',
            index=models.Index(fields=['correlation_id'], name='api_audit_corr_id_idx'),
        ),
        migrations.AddIndex(
            model_name='apiauditlog',
            index=models.Index(fields=['endpoint'], name='api_audit_endpoint_idx'),
        ),
        migrations.AddIndex(
            model_name='apiauditlog',
            index=models.Index(fields=['status_code'], name='api_audit_status_idx'),
        ),
        migrations.CreateModel(
            name='DataChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('correlation_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('operation', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')], max_length=10)),
                ('object_id', models.CharField(max_length=64)),
                ('object_repr', models.CharField(blank=True, max_length=255)),
                ('changed_fields', models.JSONField(blank=True, default=list)),
                ('previous_data', models.JSONField(blank=True, default=dict)),
                ('new_data', models.JSONField(blank=True, default=dict)),
                ('api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_change_logs', to='api.apikey')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_change_logs', to='auth.user')),
            ],
            options={
                'db_table': 'data_change_logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='datachangelog',
            index=models.Index(fields=['timestamp'], name='data_change_timestam_idx'),
        ),
        migrations.AddIndex(
            model_name='datachangelog',
            index=models.Index(fields=['correlation_id'], name='data_change_corr_id_idx'),
        ),
        migrations.AddIndex(
            model_name='datachangelog',
            index=models.Index(fields=['operation'], name='data_change_operation_idx'),
        ),
        migrations.AddIndex(
            model_name='datachangelog',
            index=models.Index(fields=['content_type'], name='data_change_contenttype_idx'),
        ),
    ]

