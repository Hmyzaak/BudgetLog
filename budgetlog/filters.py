import django_filters
from django import forms
from .models import Transaction, Category, Account


class TransactionFilter(django_filters.FilterSet):
    # Částka s rozsahem
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    # Typ transakce (příjem/výdaj)
    type = django_filters.ChoiceFilter(
        choices=Transaction.TYPE_CHOICES,
        label='Typ transakce',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Datum s rozsahem
    datestamp__gte = django_filters.DateFilter(
        field_name='datestamp',
        lookup_expr='gte',
        label='Datum (od)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    datestamp__lte = django_filters.DateFilter(
        field_name='datestamp',
        lookup_expr='lte',
        label='Datum (do)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    # Kategorie a účet
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.none(),  # Prázdný queryset, bude nastaven dynamicky
        label='Kategorie',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    account = django_filters.ModelChoiceFilter(
        queryset=Account.objects.none(),  # Prázdný queryset, bude nastaven dynamicky
        label='Účet',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Popis transakce (fulltext)
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Popis obsahuje',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Získání aktuální knihy z kwargs
        book = kwargs.pop('book', None)
        super().__init__(*args, **kwargs)

        if book:
            # Nastavení querysetu na kategorie a účty pouze z aktuální knihy
            self.filters['category'].queryset = Category.objects.filter(book=book)
            self.filters['account'].queryset = Account.objects.filter(book=book)

    class Meta:
        model = Transaction
        fields = ['amount_min', 'amount_max', 'type', 'datestamp__gte', 'datestamp__lte', 'category', 'account',
                  'description']
