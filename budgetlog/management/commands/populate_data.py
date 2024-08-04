from django.core.management.base import BaseCommand
from budgetlog.models import Transaction, Category, Account
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        """
        # Vytvoření kategorií
        categories = ['Potraviny', 'Doprava', 'Zábava', 'Nájem', 'Úspory']
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
        """

        # Vložení transakcí
        categories = Category.objects.all()
        accounts = Account.objects.all()
        types = ['income', 'expense']
        now = timezone.now()
        for _ in range(1000):  # Vložení 1000 transakcí
            Transaction.objects.create(
                amount=Decimal(random.uniform(5, 500)),
                category=random.choice(categories),
                datestamp=now - timedelta(days=random.randint(0, 365*2)),
                description='Testovací transakce',
                account=random.choice(accounts),
                type=random.choice(types)
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database'))
