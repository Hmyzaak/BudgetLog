from django.shortcuts import render
from django.db.models import Sum, DecimalField, Q, F, Case, When, Value
from django.db.models.functions import Coalesce

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from decimal import Decimal
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm


# Create your views here.
# Všechny třídy dědí z generických View podle toho, co s daným modelem mají dělat.
class TransactionListView(ListView):
    """Zobrazí seznam všech transakcí."""
    model = Transaction
    template_name = 'budgetlog/transaction_list.html'
    context_object_name = 'transactions'
    # nastavuje název proměnné, která bude použita v šabloně pro přístup k seznamu transakcí: Výchozí název proměnné
    # by byl object_list


class TransactionCreateView(CreateView):
    """Umožní uživateli vytvořit novou transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')
    # Po vytvoření nsakce přesměruje uživatele na 'transaction-list', tzn. "transaction/"


class TransactionDetailView(DeleteView):
    """Umožní uživateli náhled na veškeré informace o transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_detail.html'
    context_object_name = 'transaction'


class TransactionUpdateView(UpdateView):
    """Umožní uživateli upravit existující transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')


class TransactionDeleteView(DeleteView):
    """Umožní uživateli smazat transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')


class CategoryListView(ListView):
    """Zobrazí seznam všech kategorií."""
    model = Category
    template_name = 'budgetlog/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(CreateView):
    """Umožní uživateli vytvořit novou kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(UpdateView):
    """Umožní uživateli upravit existující kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(DeleteView):
    """Umožní uživateli smazat kategorii."""
    model = Category
    template_name = 'budgetlog/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


def dashboard_view(request):
    # Logika pro získání měsíců a roků s transakcemi
    transactions = Transaction.objects.all()
    months_years = transactions.dates('datestamp', 'month', order='DESC')

    # Výpočet bilance pro každý měsíc
    """
    output_field=DecimalField(): Zajistí, že výstup agregace je DecimalField.
    Decimal('0'): Výchozí hodnota jako Decimal, aby byla kompatibilní s typem amount.
    income or Decimal('0'): Zajišťuje, že pokud income je None, použije se Decimal('0').
    """
    month_balance = {}
    for date in months_years:
        income = transactions.filter(
            datestamp__year=date.year,
            datestamp__month=date.month,
            type='income'
        ).aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        expense = transactions.filter(
            datestamp__year=date.year,
            datestamp__month=date.month,
            type='expense'
        ).aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        balance = (income or Decimal('0')) - (expense or Decimal('0'))
        month_balance[date] = balance

    # Získání seznamů roků
    years = transactions.dates('datestamp', 'year', order='DESC')

    context = {
        'months_years': months_years,
        'month_balance': month_balance,
        'years': years,
        # Příp. přidání dalších dat potřebných pro zobrazení grafů
    }
    return render(request, 'budgetlog/dashboard.html', context)


def month_detail_view(request, year, month):
    transactions = Transaction.objects.filter(
        datestamp__year=year,
        datestamp__month=month
    ).order_by('-datestamp')  # Seřazení dle data, nejnovější nahoře

    # Výpočet součtu transakcí pro každou kategorii
    """
    Q je objekt v Django, který se používá k vytváření složitějších dotazů pomocí ORM (Object-Relational Mapping). 
    Umožňuje kombinovat podmínky pomocí logických operátorů (AND, OR) a pracovat s podmínkami, které nejsou možné 
    pomocí standardních filtrů. Je nezbytné importovat Q z django.db.models, aby bylo možné jej použít v dotazech.
    F zase používáme pro referenci na pole modelu (transaction__amount) v agregaci při použití Case, When a then.
    """
    category_summaries = Category.objects.annotate(
        total=Coalesce(
            Sum(
                Case(
                    When(transaction__type='expense', then=-F('transaction__amount')),
                    default=F('transaction__amount'),
                    output_field=DecimalField()
                ),
                filter=Q(transaction__datestamp__year=year, transaction__datestamp__month=month),
                output_field=DecimalField()
            ),
            Decimal('0')  # Coalesce zajistí, že pokud není žádná transakce, použije se hodnota 0
        )
    ).order_by('-total')  # Seřazení podle součtu, největší nahoře

    context = {
        'year': year,
        'month': month,
        'transactions': transactions,
        'category_summaries': category_summaries,
    }
    return render(request, 'budgetlog/monthly_detail.html', context)
