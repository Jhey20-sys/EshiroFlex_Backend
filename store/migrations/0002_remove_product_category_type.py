# Generated by Django 5.1.6 on 2025-02-25 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category_type',
        ),
    ]
