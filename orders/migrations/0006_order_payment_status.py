# Generated by Django 3.2.25 on 2024-10-15 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20241014_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]
