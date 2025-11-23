from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

"""
Definujeme URL vzory pro všechny naše views.
Používáme as_view(), abychom převedli třídy views na funkce, které Django může použít pro směrování.
"""

urlpatterns = [
    # Prohlížeče opakovaně hledaly favicon na rootu a nikoli v šabloně
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),

    # Sekce pro knihy
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/create/', views.BookCreateView.as_view(), name='book-add'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-edit'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('select-book/<int:book_id>/', views.SelectBookView.as_view(), name='select-book'),

    # Sekce pro trasakce
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/edit/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-edit'),
    path('transactions/delete/<int:pk>/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/bulk-action/', views.BulkTransactionActionView.as_view(), name='bulk-transaction-action'),
    path('transactions/upload/', views.UploadTransactionsView.as_view(), name='upload-transactions'),
    path("download-template/", views.download_csv_template, name="download_csv_template"),

    # Sekce pro kategorie
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Sekce pro tagy
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('tags/add/', views.TagCreateView.as_view(), name='tag-add'),
    path('tags/edit/<int:pk>/', views.TagUpdateView.as_view(), name='tag-edit'),
    path('tags/delete/<int:pk>/', views.TagDeleteView.as_view(), name='tag-delete'),

    # Sekce pro dashboard
    path('', views.index_handler, name='index'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/month/<int:year>/<int:month>/', views.MonthDetailView.as_view(), name='month-detail'),
    path('dashboard/year/<int:year>/', views.YearDetailView.as_view(), name='year-detail'),

    # Sekce pro uživatele
    path('register/', views.UserViewRegister.as_view(), name='registration'),
    path('setup-book/', views.SetupBookView.as_view(), name='setup-book'),
    path('login/', views.UserViewLogin.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete-account'),

    # Sekce pro reset hesla
    path('password-reset/', views.CustomPasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',views.CustomPasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
