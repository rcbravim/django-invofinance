# Generated by Django 4.0.3 on 2022-04-23 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_user_use_is_manager'),
        ('board', '0007_alter_beneficiary_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_name', models.CharField(max_length=250)),
                ('cat_slug', models.SlugField(max_length=250, unique=True)),
                ('cat_status', models.BooleanField(default=False)),
                ('cat_date_created', models.DateTimeField(editable=False)),
                ('cat_date_updated', models.DateTimeField()),
                ('cat_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.user')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_name', models.CharField(max_length=250)),
                ('sub_slug', models.SlugField(max_length=250, unique=True)),
                ('sub_status', models.BooleanField(default=False)),
                ('sub_date_created', models.DateTimeField(editable=False)),
                ('sub_date_updated', models.DateTimeField()),
                ('sub_date_deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.category')),
            ],
        ),
    ]