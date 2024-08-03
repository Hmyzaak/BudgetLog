# Generated by Django 5.0.7 on 2024-08-03 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetlog', '0007_alter_transaction_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(help_text='Vyber kategorii pro tuto transakci.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='budgetlog.category', verbose_name='Kategorie'),
        ),
    ]