from django.urls import path
from . import url_handlers
from . import views

"""
Definujeme URL vzory pro všechny naše views.
Používáme as_view(), abychom převedli třídy views na funkce, které Django může použít pro směrování.
"""

urlpatterns = [
    # Projekty
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project-create'),
    # path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    # path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),

    # Transakce
    path('projects/<int:project_id>/transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('projects/<int:project_id>/transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('projects/<int:project_id>/transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(),
         name='transaction-edit'),
    path('projects/<int:project_id>/transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(),
         name='transaction-delete'),
    path('projects/<int:project_id>/transaction/<int:pk>/', views.TransactionDetailView.as_view(),
         name='transaction-detail'),

    # Kategorie
    path('projects/<int:project_id>/categories/', views.CategoryListView.as_view(), name='category-list'),
    path('projects/<int:project_id>/categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('projects/<int:project_id>/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(),
         name='category-edit'),
    path('projects/<int:project_id>/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(),
         name='category-delete'),

    # Účty
    path('projects/<int:project_id>/accounts/', views.AccountListView.as_view(), name='account-list'),
    path('projects/<int:project_id>/accounts/add/', views.AccountCreateView.as_view(), name='account-add'),
    path('projects/<int:project_id>/accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account-edit'),
    path('projects/<int:project_id>/accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account-delete'),

    # Dashboard
    path('projects/<int:project_id>/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('projects/<int:project_id>/dashboard/month/<int:year>/<int:month>/', views.MonthDetailView.as_view(), name='month-detail'),
    path('projects/<int:project_id>/dashboard/year/<int:year>/', views.YearDetailView.as_view(), name='year-detail'),

    # Uživatelé
    path('register/', views.UserViewRegister.as_view(), name='registration'),
    path('login/', views.UserViewLogin.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('', url_handlers.index_handler),
]
