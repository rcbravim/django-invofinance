# Generated by Django 4.0.3 on 2022-04-19 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_rename_ben_description_beneficiary_ben_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiary',
            name='ben_slug',
            field=models.SlugField(default=0, unique=True),
            preserve_default=False,
        ),
    ]
