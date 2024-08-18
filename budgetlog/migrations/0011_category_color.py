# Generated by Django 5.0.7 on 2024-08-18 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetlog', '0010_remove_transaction_person_alter_transaction_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(default='#000000', help_text='Barva kategorie pro zobrazení v grafu ročního přehledu', max_length=7, verbose_name='Barva kategorie'),
        ),
    ]