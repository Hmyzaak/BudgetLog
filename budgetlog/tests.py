from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from budgetlog.models import AppUser, Book, Category, Tag, RecurringTransaction, Transaction
from budgetlog.tasks import generate_transactions_from_recurring

# Create your tests here.


class RecurringTransactionTest(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(email="test@example.com", password="password")
        self.book = Book.objects.create(name="Test Book", owner=self.user)
        self.category = Category.objects.create(name="Test Category", book=self.book)
        self.tag = Tag.objects.create(name="Test Tag", book=self.book)

        # Vytvoříme aktivní opakovanou transakci se start_date = dnes
        self.recurring = RecurringTransaction.objects.create(
            name="Test Recurrence",
            book=self.book,
            amount=100.00,
            category=self.category,
            description="Testovací opakovaná transakce",
            type="expense",
            start_date=now().date(),
            frequency="daily",
            is_active=True,
        )
        self.recurring.tags.add(self.tag)

    def test_transaction_is_created_once(self):
        """Transakce by měla být vytvořena při prvním spuštění."""
        generate_transactions_from_recurring()
        transactions = Transaction.objects.filter(book=self.book)
        self.assertEqual(transactions.count(), 1)

        transaction = transactions.first()
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.category, self.category)
        self.assertEqual(transaction.book, self.book)
        self.assertEqual(transaction.type, "expense")
        self.assertIn("Automaticky vygenerováno", transaction.description)

    def test_transaction_not_duplicated(self):
        """Transakce se nevytvoří podruhé pro stejné datum."""
        generate_transactions_from_recurring()
        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_transaction_not_created_outside_schedule(self):
        """Transakce se negeneruje, pokud dnešní datum nesouhlasí s plánem."""
        self.recurring.frequency = "yearly"
        self.recurring.save()

        # Nastavíme start_date na zítřek → dnešek by neměl projít should_generate_on
        self.recurring.start_date = now().date() + timedelta(days=1)
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 0)

    def test_weekly_frequency_generates_correctly(self):
        """Transakce se vygeneruje jednou týdně, pokud start_date je stejný den v týdnu."""
        today = now().date()
        self.recurring.frequency = "weekly"
        self.recurring.start_date = today - timedelta(weeks=1)  # přesně před týdnem
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_weekly_frequency_not_generated_too_soon(self):
        """Transakce se negeneruje, pokud týden ještě neuplynul."""
        today = now().date()
        self.recurring.frequency = "weekly"
        self.recurring.start_date = today - timedelta(days=6)
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 0)

    def test_monthly_frequency_generates_correctly(self):
        """Transakce se vygeneruje jednou měsíčně, pokud měsíc uplynul."""
        today = now().date()
        self.recurring.frequency = "monthly"
        self.recurring.start_date = today - timedelta(days=30)
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_monthly_frequency_not_generated_too_soon(self):
        """Transakce se negeneruje, pokud měsíc ještě neuplynul."""
        today = now().date()
        self.recurring.frequency = "monthly"
        self.recurring.start_date = today - timedelta(days=20)
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 0)

    def test_custom_interval_generates_correctly(self):
        """Transakce se generuje podle vlastního intervalu."""
        today = now().date()
        self.recurring.frequency = "custom"
        self.recurring.custom_interval_days = 5
        self.recurring.start_date = today - timedelta(days=10)  # 2 cykly po 5 dnech
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_custom_interval_not_generated_too_soon(self):
        """Transakce se negeneruje, pokud vlastní interval ještě neuběhl."""
        today = now().date()
        self.recurring.frequency = "custom"
        self.recurring.custom_interval_days = 7
        self.recurring.start_date = today - timedelta(days=5)
        self.recurring.save()

        generate_transactions_from_recurring()
        self.assertEqual(Transaction.objects.count(), 0)


"""
def test_user_registration_creates_book(self):
    user = AppUser.objects.create_user(email='testuser@budgetlog.cz', password='password123')
    self.assertTrue(Book.objects.filter(owner=user).exists(), "Nový uživatel nemá vlastní knihu.")


def test_add_accounts_categories_transactions(self):
    user = AppUser.objects.create_user(email='testuser@budgetlog.cz', password='password123')
    book = Book.objects.create(name="Kniha 1", owner=user)
    account = Account.objects.create(name="Účet 1", book=book)
    category = Category.objects.create(name="Kategorie 1", book=book)
    transaction = Transaction.objects.create(amount=100, account=account, category=category, book=book)
    self.assertEqual(transaction.book, book)


def test_books_separation(self):
    user = AppUser.objects.create_user(email='testuser@budgetlog.cz', password='password123')
    book1 = Book.objects.create(name="Kniha 1", owner=user)
    book2 = Book.objects.create(name="Kniha 2", owner=user)
    account1 = Account.objects.create(name="Účet 1", book=book1)
    account2 = Account.objects.create(name="Účet 2", book=book2)
    self.assertNotEqual(account1.book, account2.book)


def test_no_access_between_users(self):
    user1 = AppUser.objects.create_user(email='user1@budgetlog.cz', password='password123')
    user2 = AppUser.objects.create_user(email='user2@budgetlog.cz', password='password123')
    book1 = Book.objects.create(name="Kniha User 1", owner=user1)
    self.client.login(email='user2@budgetlog.cz', password='password123')
    response = self.client.get(reverse('book-detail', kwargs={'pk': book1.id}))
    self.assertEqual(response.status_code, 403)


def test_select_book_after_login(self):
    user = AppUser.objects.create_user(email='testuser@budgetlog.cz', password='password123')
    self.client.login(email='testuser@budgetlog.cz', password='password123')
    response = self.client.get(reverse('transaction-list'))
    self.assertRedirects(response, reverse('select-book'))


def test_switch_book_without_logout(self):
    user = AppUser.objects.create_user(email='testuser@budgetlog.cz', password='password123')
    book1 = Book.objects.create(name="Kniha 1", owner=user)
    book2 = Book.objects.create(name="Kniha 2", owner=user)
    self.client.login(email='testuser@budgetlog.cz', password='password123')
    self.client.post(reverse('select-book'), {'book_id': book1.id})
    self.assertEqual(self.client.session['current_book_id'], str(book1.id))
    self.client.post(reverse('select-book'), {'book_id': book2.id})
    self.assertEqual(self.client.session['current_book_id'], str(book2.id))


def test_data_collision(self):
    user1 = AppUser.objects.create_user(email='user1@budgetlog.cz', password='password123')
    user2 = AppUser.objects.create_user(email='user2@budgetlog.cz', password='password123')
    book1 = Book.objects.create(name="Kniha", owner=user1)
    book2 = Book.objects.create(name="Kniha", owner=user2)
    account1 = Account.objects.create(name="Účet", book=book1)
    account2 = Account.objects.create(name="Účet", book=book2)
    self.assertNotEqual(account1.id, account2.id)


def test_url_protection(self):
    user1 = AppUser.objects.create_user(email='user1@budgetlog.cz', password='password123')
    user2 = AppUser.objects.create_user(email='user2@budgetlog.cz', password='password123')
    book1 = Book.objects.create(name="Kniha User 1", owner=user1)
    self.client.login(email='user2@budgetlog.cz', password='password123')
    response = self.client.get(reverse('transaction-detail', kwargs={'pk': book1.id}))
    self.assertEqual(response.status_code, 403)
"""