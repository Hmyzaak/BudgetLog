import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from budgetlog.models import Book, Category, Tag, Transaction


class Command(BaseCommand):
    help = 'Generate test data for categories, tags, and transactions for a specific user and book'

    def handle(self, *args, **kwargs):
        book_id = 37

        # Získání konkrétní knihy
        book = Book.objects.get(id=book_id)

        # Generování 5 kategorií
        categories = []
        for i in range(5):
            category = Category.objects.create(
                name=f'Kategorie {i+1}',
                color=f'#{random.randint(0, 0xFFFFFF):06x}',
                description=f'Popis kategorie {i+1}',
                book=book
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f'Vygenerováno 5 kategorií pro knihu s id={book_id}'))

        # Generování 9 tagů
        tags = []
        for i in range(9):
            tag = Tag.objects.create(
                name=f'Tag {i+1}',
                color=f'#{random.randint(0, 0xFFFFFF):06x}',
                description=f'Popis tagu {i+1}',
                book=book
            )
            tags.append(tag)

        self.stdout.write(self.style.SUCCESS(f'Vygenerováno 9 tagů pro knihu s id={book_id}'))

        # Generování 1000 transakcí
        transaction_types = ['income', 'expense']
        for _ in range(1000):
            # Náhodná částka mezi 10 a 10000 CZK, se 2 desetinnými místy
            amount = Decimal(random.uniform(10, 10000)).quantize(Decimal('0.01'))
            # Náhodný typ transakce
            type_choice = random.choice(transaction_types)
            # Náhodné datum v rámci posledních 1000 dnech
            datestamp = timezone.now().date() - timezone.timedelta(days=random.randint(0, 1000))
            # Náhodná kategorie z vytvořených kategorií nebo None
            category = random.choice(categories)
            # Vytvoření transakce
            transaction = Transaction.objects.create(
                book=book,
                amount=amount,
                category=category,
                datestamp=datestamp,
                description=f'Popis transakce {_+1}',
                type=type_choice
            )

            # Přiřazení 0 až 5 náhodných tagů
            transaction_tags = random.sample(tags, random.randint(0, 5))
            transaction.tags.set(transaction_tags)

        self.stdout.write(self.style.SUCCESS(f'Vygenerováno 1000 transakcí pro knihu s id={book_id}'))
