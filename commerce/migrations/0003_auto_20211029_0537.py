# Generated by Django 3.2.8 on 2021-10-29 05:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0002_auto_20211027_1637'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name': 'address', 'verbose_name_plural': 'addresses'},
        ),
        migrations.AlterModelOptions(
            name='orderstatus',
            options={'verbose_name': 'order status', 'verbose_name_plural': 'order statuses'},
        ),
    ]