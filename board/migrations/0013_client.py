# Generated by Django 4.0.3 on 2022-05-02 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0012_country_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cli_name', models.CharField(max_length=250)),
                ('cli_city', models.CharField(max_length=250)),
                ('cli_email', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('cli_phone', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('cli_responsible', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('cli_status', models.BooleanField(default=False)),
                ('cli_date_created', models.DateTimeField(editable=False)),
                ('cli_date_updated', models.DateTimeField()),
                ('cli_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('country', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='board.country')),
                ('state', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='board.state')),
            ],
        ),
    ]
