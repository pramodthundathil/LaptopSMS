# Generated by Django 5.0.6 on 2025-07-08 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0021_inventory_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='brand_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
