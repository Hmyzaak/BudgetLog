from django.contrib import admin
from .models import *
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# superadmin; superadmin@budgetlog.cz; heslojeveslo

# admin@budgetlog.cz; ???
# demo@budgetlog.cz; demoheslo


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = ["email"]

    def save(self, commit=True):
        if self.is_valid():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password"])
            """Kolekce 'cleaned_data[]' používáme pro získání zadaných dat a preferujeme ji před vytahováním dat z 
            čistého POST. Lze ji použít pouze po validaci a je tak zaručeno, že jsou čtená data vždy validní."""
            if commit:
                user.save()
            return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AppUser
        fields = ["email", "is_admin"]

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.Meta.fields.remove("password")
        # Odebíráme políčko pro změnu hesla


# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Zobrazuje sloupce 'name' a 'description' v admin seznamu."""
    list_display = ('name', 'description', 'owner')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Zobrazuje sloupce v admin seznamu."""
    list_display = ('name', 'color', 'description', 'book')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Zobrazuje sloupce 'name' , 'color', 'description' a 'book' v admin seznamu."""
    list_display = ('name', 'color', 'description', 'book')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Zobrazuje všechny atributy transakce ve sloupcích v admin seznamu a umožňuje podle níže uvedených filtrovat."""
    list_display = ('amount', 'category', 'datestamp', 'display_tags', 'description', 'type', 'book')
    list_filter = ('type', 'category', 'datestamp', 'book')


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    """Konfigurace pro zobrazení a správu uživatelů v admin prostředí."""
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["email", "is_admin"]
    list_filter = ["is_admin"]
    ordering = ["email"]
    search_fields = ["email"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ) # Úprava jednotlivých uživatelů

    add_fieldsets = (
        (None, {
            "fields": ["email", "password"]}
         ),
    ) # Vytvoření uživatele

    filter_horizontal = []
    """
    řádek výše překonal errory uvedené níže
ERRORS:
<class 'budgetlog.admin.UserAdmin'>: (admin.E019) The value of 'filter_horizontal[0]' refers to 'groups', which is not a field of 'budgetlog.User'.
<class 'budgetlog.admin.UserAdmin'>: (admin.E019) The value of 'filter_horizontal[1]' refers to 'user_permissions', which is not a field of 'budgetlog.User'.
"""
