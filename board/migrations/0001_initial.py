# Generated by Django 4.0.3 on 2022-04-12 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0008_user_use_is_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeneficiaryCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ben_description', models.CharField(max_length=250)),
                ('ben_status', models.BooleanField(default=False)),
                ('ben_date_created', models.DateTimeField(editable=False)),
                ('ben_date_updated', models.DateTimeField()),
                ('ben_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.user')),
            ],
        ),
    ]
