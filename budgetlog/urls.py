from django.urls import path
from . import url_handlers
from . import views

"""
Definujeme URL vzory pro všechny naše views.
Používáme as_view(), abychom převedli třídy views na funkce, které Django může použít pro směrování.
"""

urlpatterns = [
    # URL pro knihy
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('select-book/', views.SelectBookView.as_view(), name='select-book'),
    # URL pro trasakce
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/edit/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-edit'),
    path('transactions/delete/<int:pk>/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    # URL pro kategorie
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category-delete'),
    # URL pro účty
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/add/', views.AccountCreateView.as_view(), name='account-add'),
    path('accounts/edit/<int:pk>/', views.AccountUpdateView.as_view(), name='account-edit'),
    path('accounts/delete/<int:pk>/', views.AccountDeleteView.as_view(), name='account-delete'),
    # URL pro dashboard
    path('', url_handlers.index_handler),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/month/<int:year>/<int:month>/', views.MonthDetailView.as_view(), name='month-detail'),
    path('dashboard/year/<int:year>/', views.YearDetailView.as_view(), name='year-detail'),
    # URL pro uživatele
    path('register/', views.UserViewRegister.as_view(), name='registration'),
    path('login/', views.UserViewLogin.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
]
