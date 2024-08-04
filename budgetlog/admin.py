from django.contrib import admin
from .models import Category, Transaction, Account

# superadmin; superadmin@budgetlog.cz; heslojeveslo


# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    # Zobrazuje sloupce 'name' a 'description' v admin seznamu


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    # Zobrazuje sloupce 'name' a 'description' v admin seznamu


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'datestamp', 'description', 'account', 'type')
    list_filter = ('type', 'category', 'datestamp', 'account')
    search_fields = ('category__name', 'account')

