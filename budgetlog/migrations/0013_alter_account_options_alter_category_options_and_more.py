# Generated by Django 5.0.7 on 2024-08-21 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgetlog', '0012_user_alter_transaction_account_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'verbose_name': 'Účet', 'verbose_name_plural': 'Účty'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategorie', 'verbose_name_plural': 'Kategorie'},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'verbose_name': 'Transakce', 'verbose_name_plural': 'Transakce'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Uživatel', 'verbose_name_plural': 'Uživatelé'},
        ),
    ]