# Generated by Django 4.0.3 on 2022-04-20 18:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_user_use_is_manager'),
        ('board', '0006_beneficiarycategory_cat_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiary',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.user'),
        ),
    ]
