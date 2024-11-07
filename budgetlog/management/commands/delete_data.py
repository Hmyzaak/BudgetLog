"""Spusť Django shell a uveď příkazy"""
# py manage.py shell
# quit()

from budgetlog.models import Category, Transaction, Tag, Book

# Smažte všechny transakce
Transaction.objects.all().delete()

# Smažte všechny kategorie
Category.objects.all().delete()

# Smažte všechny tagy
Tag.objects.all().delete()

# Smaže všechny knihy
Book.objects.all().delete()
