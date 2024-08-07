# Generated by Django 4.2.1 on 2024-07-21 08:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('budgetlog', '0003_rename_timestamp_transaction_datestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, help_text='Detailnější popis kategorie pro transakce (volitelný)', null=True, verbose_name='Popis'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text='Uveď název kategorie pro transakce (např. potraviny, doprava, zábava)', max_length=200, verbose_name='Název'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Uveď částku transakce v [CZK]', max_digits=10, verbose_name='Částka'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(help_text='Vyber kategorii pro tuto transakci', null=True, on_delete=django.db.models.deletion.SET_NULL, to='budgetlog.category', verbose_name='Kategorie'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='datestamp',
            field=models.DateField(default=django.utils.timezone.now, help_text='Datum provedení transakce', verbose_name='Datum'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, help_text='Detailnější popis transakce (volitelný)', null=True, verbose_name='Popis'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='person',
            field=models.CharField(choices=[('kuba', 'Kuba'), ('romca', 'Romča')], help_text='Kdo transakci prováděl?', max_length=10, verbose_name='Osoba'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('income', 'Příjem'), ('expense', 'Výdaj')], default='expense', help_text='Je tato transakce výdaj nebo příjem?', max_length=7, verbose_name='Typ'),
        ),
    ]
