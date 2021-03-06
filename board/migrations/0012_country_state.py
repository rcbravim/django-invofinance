# Generated by Django 4.0.3 on 2022-05-02 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0011_alter_beneficiary_beneficiary_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cou_name', models.CharField(max_length=250)),
                ('cou_status', models.BooleanField(default=False)),
                ('cou_date_created', models.DateTimeField(editable=False)),
                ('cou_date_updated', models.DateTimeField()),
                ('cou_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sta_name', models.CharField(max_length=250)),
                ('sta_status', models.BooleanField(default=False)),
                ('sta_date_created', models.DateTimeField(editable=False)),
                ('sta_date_updated', models.DateTimeField()),
                ('sta_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.country')),
            ],
        ),
    ]
