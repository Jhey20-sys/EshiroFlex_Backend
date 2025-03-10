# Generated by Django 5.1.6 on 2025-03-08 08:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_remove_order_cart_items_remove_order_total_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10),
            preserve_default=False,
        ),
         migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),  
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.order'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
