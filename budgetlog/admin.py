from django.contrib import admin
from .models import Category, Transaction

# superadmin; superadmin@budgetlog.cz; heslojeveslo


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    # Zobrazuje sloupce 'name' a 'description' v admin seznamu


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'datestamp', 'description', 'person', 'type')
    list_filter = ('type', 'category', 'datestamp', 'person')
    search_fields = ('category__name', 'person')

