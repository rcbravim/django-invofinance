# Generated by Django 4.0.3 on 2022-05-03 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0017_country_cou_phone_digits'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='cou_country_code',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
    ]
