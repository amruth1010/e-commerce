# Generated by Django 3.2.25 on 2024-10-04 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_alter_sizevariant_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
