from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *


class TransactionForm(forms.ModelForm):
    """Formulář pro přidání a úpravu transakcí."""

    class Meta:
        model = Transaction
        # Odkazuje na model, pro který formulář vytváříme
        fields = ['amount', 'category', 'datestamp', 'description', 'account', 'type']
        # Pole zahrnuta ve formuláři
        widgets = {'datestamp': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 1})
                   }
        # Upravuje vzhled polí ve formuláři. DateInput s type='date' umožňuje vybrat datum pomocí kalendáře.
        help_texts = {'datestamp': "Zadejte datum provedení, příp. započtení, transakce."}
        # Upravuje pomocný text pro pole datestamp

    def __init__(self, *args, **kwargs):
        # Přidání pop argumentu 'book'
        self.book = kwargs.pop('book', None)  # Získání knihy z kwargs
        super().__init__(*args, **kwargs)  # Volání parent konstruktoru

        # Aktualizace querysetů pro category a account pouze pro aktuální knihu
        if self.book:
            self.fields['category'].queryset = Category.objects.filter(book=self.book)
            self.fields['account'].queryset = Account.objects.filter(book=self.book)
        else:
            self.fields['category'].queryset = Category.objects.none()
            self.fields['account'].queryset = Account.objects.none()


class CategoryForm(forms.ModelForm):
    """Formulář pro přidání a úpravu kategorií transakcí."""

    class Meta:
        model = Category
        fields = ['name', 'color', 'description']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 1})
        }


class AccountForm(forms.ModelForm):
    """Formulář pro přidání a úpravu účtů pro transakce."""

    class Meta:
        model = Account
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 1})}


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = ['email']  # Zobrazujeme jen email, hesla jsou již obsažena v UserCreationForm

    # Přidáme vlastní validaci hesla
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Zadaná hesla se neshodují.")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ["email", "password"]
