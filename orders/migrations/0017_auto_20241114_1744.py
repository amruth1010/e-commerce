# Generated by Django 3.2.25 on 2024-11-14 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_alter_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('razorpay', 'Razorpay'), ('cod', 'Cash on Delivery')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Failed', 'Failed'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]
