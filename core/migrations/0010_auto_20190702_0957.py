# Generated by Django 2.2 on 2019-07-02 09:57

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_order_billing_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingadress',
            name='countries',
        ),
        migrations.AddField(
            model_name='billingadress',
            name='country',
            field=django_countries.fields.CountryField(default='FI', max_length=2),
            preserve_default=False,
        ),
    ]
