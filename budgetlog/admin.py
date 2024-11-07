# Django importy
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Lokální aplikace
from .models import AppUser, Book, Tag, Category, Transaction


class UserCreationForm(forms.ModelForm):
    """
    Formulář pro vytvoření uživatele, který zahrnuje nastavení hesla.
    """
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = ["email"]

    def save(self, commit=True):
        """
        Ukládá uživatele a nastavuje heslo pomocí metody set_password pro bezpečné uložení.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Formulář pro úpravu uživatele, s heslem jako polem pouze ke čtení.
    """
    password = ReadOnlyPasswordHashField(label="Password")

    class Meta:
        model = AppUser
        fields = ["email", "is_admin"]

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.Meta.fields.remove("password")
        # Odebíráme políčko pro změnu hesla


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin konfigurace pro model Book, která zobrazuje sloupce 'name' a 'description' a podporuje základní hledání.
    """
    list_display = ('name', 'description', 'owner')
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin konfigurace pro model Tag, který zobrazuje sloupce 'name', 'color', 'description' a 'book'.
    """
    list_display = ('name', 'color', 'description', 'book')
    search_fields = ('name', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin konfigurace pro model Category, která zobrazuje sloupce 'name', 'color', 'description' a 'book'.
    """
    list_display = ('name', 'color', 'description', 'book')
    search_fields = ('name', 'description')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin konfigurace pro model Transaction s možností zobrazení všech atributů a filtrování podle zadaných parametrů.
    """
    list_display = ('amount', 'category', 'datestamp', 'description', 'type', 'book')
    list_filter = ('type', 'category', 'datestamp', 'book')
    search_fields = ('description', 'category__name', 'type')


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    """
    Konfigurace pro správu uživatelů v administraci, zahrnující vytvoření a úpravu uživatelů.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["email", "is_admin"]
    list_filter = ["is_admin"]
    ordering = ["email"]
    search_fields = ["email"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    )

    add_fieldsets = (
        (None, {
            "fields": ["email", "password"]}
        ),
    )

    filter_horizontal = []
    """
    řádek výše překonal errory uvedené níže
    ERRORS:
    <class 'budgetlog.admin.UserAdmin'>: (admin.E019) The value of 'filter_horizontal[0]' refers to 'groups', which is not a field of 'budgetlog.User'.
    <class 'budgetlog.admin.UserAdmin'>: (admin.E019) The value of 'filter_horizontal[1]' refers to 'user_permissions', which is not a field of 'budgetlog.User'.
    """
