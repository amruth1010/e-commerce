# Generated by Django 3.2.25 on 2024-09-21 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
        ('product', '0002_remove_products_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='product_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='category.category'),
        ),
    ]
