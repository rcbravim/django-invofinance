# Generated by Django 4.0.3 on 2022-05-03 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0016_client_cli_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='cou_phone_digits',
            field=models.CharField(default=1, max_length=128),
            preserve_default=False,
        ),
    ]
