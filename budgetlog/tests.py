from django.test import TestCase
from django.urls import reverse

from budgetlog.models import *


# Create your tests here.
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
