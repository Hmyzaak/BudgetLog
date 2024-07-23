from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    """Formulář pro přidání a úpravu transakcí."""

    class Meta:
        model = Transaction
        # Odkazuje na model, pro který formulář vytváříme
        fields = ['amount', 'category', 'datestamp', 'description', 'person', 'type']
        # Pole zahrnuta ve formuláři
        widgets = {'datestamp': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 1})
                   }
        # Upravuje vzhled polí ve formuláři. DateInput s type='date' umožňuje vybrat datum pomocí kalendáře.
        help_texts = {'datestamp': "Zadejte datum provedení, příp. započtení, transakce."}
        # Upravuje pomocný text pro pole datestamp


class CategoryForm(forms.ModelForm):
    """Formulář pro přidání a úpravu kategorií transakcí."""

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 1})}

