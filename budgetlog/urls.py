from django.urls import path
from . import url_handlers
from . import views

"""
Definujeme URL vzory pro všechny naše views.
Používáme as_view(), abychom převedli třídy views na funkce, které Django může použít pro směrování.
"""

urlpatterns = [
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/edit/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-edit'),
    path('transactions/delete/<int:pk>/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category-delete'),
    path('', url_handlers.index_handler),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/month/<int:year>/<int:month>/', views.month_detail_view, name='month-detail'),
    path('dashboard/year/<int:year>/', views.YearSummaryView.as_view(), name='year-summary'),
]
