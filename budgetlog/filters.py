import django_filters
from django_filters import widgets
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
    datestamp = django_filters.DateFromToRangeFilter(
        field_name='datestamp',
        label='Datum (od-do)',
        widget=django_filters.widgets.RangeWidget(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )

    # Kategorie a účet
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Kategorie',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    account = django_filters.ModelChoiceFilter(
        queryset=Account.objects.all(),
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

    class Meta:
        model = Transaction
        fields = ['amount_min', 'amount_max', 'type', 'datestamp', 'category', 'account', 'description']

