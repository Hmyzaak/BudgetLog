"""Spusť Django shell a uveď příkazy"""
# py manage.py shell
# quit()

from django.core.management import BaseCommand
from budgetlog.models import Category, Transaction, Tag, Book


class Command(BaseCommand):
    help = 'Generate test data for categories, tags, and transactions for a specific user and book'

    def handle(self, *args, **kwargs):
        book_id = 37
        book = Book.objects.get(id=book_id)

        # Smažte všechny transakce
        Transaction.objects.filter(book=book).delete()

        # Smažte všechny kategorie
        Category.objects.filter(book=book).delete()

        # Smažte všechny tagy
        Tag.objects.filter(book=book).delete()

        """
        # Smaže všechny knihy
        Book.objects.all().delete()
        """
