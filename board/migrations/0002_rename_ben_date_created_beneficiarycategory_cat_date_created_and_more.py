# Generated by Django 4.0.3 on 2022-04-12 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_user_use_is_manager'),
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beneficiarycategory',
            old_name='ben_date_created',
            new_name='cat_date_created',
        ),
        migrations.RenameField(
            model_name='beneficiarycategory',
            old_name='ben_date_deleted',
            new_name='cat_date_deleted',
        ),
        migrations.RenameField(
            model_name='beneficiarycategory',
            old_name='ben_date_updated',
            new_name='cat_date_updated',
        ),
        migrations.RenameField(
            model_name='beneficiarycategory',
            old_name='ben_description',
            new_name='cat_description',
        ),
        migrations.RenameField(
            model_name='beneficiarycategory',
            old_name='ben_status',
            new_name='cat_status',
        ),
        migrations.CreateModel(
            name='Beneficiary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ben_description', models.CharField(max_length=250)),
                ('ben_status', models.BooleanField(default=False)),
                ('ben_date_created', models.DateTimeField(editable=False)),
                ('ben_date_updated', models.DateTimeField()),
                ('ben_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('beneficiary_category', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='board.beneficiarycategory')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.user')),
            ],
        ),
    ]