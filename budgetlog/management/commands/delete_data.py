"""Spusť Django shell a uveď příkazy"""
# py manage.py shell
# quit()

from budgetlog.models import Category, Transaction, Account

# Smažte všechny transakce
Transaction.objects.all().delete()

# Smažte všechny kategorie
Category.objects.all().delete()

# Smažte všechny účty
Account.objects.all().delete()