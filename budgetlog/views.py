from django.db.models import Sum, DecimalField, Q, F, Case, When
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django_filters.views import FilterView
from decimal import Decimal
from .models import Transaction, Category, Account
from .filters import TransactionFilter
from .forms import TransactionForm, CategoryForm, AccountForm

import json
import random
from django.utils.dateformat import format


# Create your views here.
# Všechny třídy dědí z generických View podle toho, co s daným modelem mají dělat.
class TransactionListView(FilterView, ListView):
    """Umožňuje vytvořit a držet data pro filtrování v seznamu transakcí a umožňuje stránkování v těchto seznamech"""
    model = Transaction
    filterset_class = TransactionFilter
    template_name = 'budgetlog/transaction_list.html'
    context_object_name = 'transactions'
    # nastavuje název proměnné, která bude použita v šabloně pro přístup k seznamu transakcí: Výchozí název proměnné
    # by byl object_list
    paginate_by = 30  # Počet transakcí na stránku
    ordering = ['-datestamp']  # Řazení transakcí podle data od nejnovějších

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filterset = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context['filter'] = filterset
        filtered_qs = filterset.qs

        paginator = Paginator(filtered_qs, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)

        context['transactions'] = transactions
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs


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
    ordering = ['name']  # Řazení dle atributu name v modelu Category


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


class AccountListView(ListView):
    """Zobrazí seznam všech účtů."""
    model = Account
    template_name = 'budgetlog/account_list.html'
    context_object_name = 'accounts'
    ordering = ['name']  # Řazení dle atributu name v modelu Account


class AccountCreateView(CreateView):
    """Umožní uživateli vytvořit nový účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountUpdateView(UpdateView):
    """Umožní uživateli upravit existující účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountDeleteView(DeleteView):
    """Umožní uživateli smazat účet."""
    model = Account
    template_name = 'budgetlog/account_confirm_delete.html'
    success_url = reverse_lazy('account-list')


class DashboardView(TemplateView):
    """Templát pro stránku se souhrnnými přehledy."""
    template_name = 'budgetlog/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.all()
        months_years = transactions.dates('datestamp', 'month', order='DESC')
        years = transactions.dates('datestamp', 'year', order='DESC')

        context.update({
            'months_years': months_years,
            'years': years,
        })

        return context


class MonthDetailView(TemplateView):
    """Templát pro detailní statistiky daného měsíce."""
    template_name = 'budgetlog/monthly_detail.html'

    def get_context_data(self, year, month, **kwargs):
        context = super().get_context_data(**kwargs)
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
        Coalesce zajistí, že pokud není žádná transakce, použije se hodnota 0.
        output_field=DecimalField(): Zajistí, že výstup agregace je DecimalField.
        Decimal('0'): Výchozí hodnota jako Decimal, aby byla kompatibilní s typem amount.
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
                Decimal('0')
            )
        ).order_by('-total')

        context.update({
            'year': year,
            'month': month,
            'transactions': transactions,
            'category_summaries': category_summaries,
        })
        return context


class YearDetailView(TemplateView):
    """Templát pro zobrazení statistik transakcí u vybraného roku."""
    template_name = 'budgetlog/yearly_detail.html'

    def get_context_data(self, year, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.filter(
            datestamp__year=year
        ).order_by('-datestamp')

        # Výpočet celkových ročních příjmů a výdajů
        total_income = transactions.filter(type='income').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_expense = transactions.filter(type='expense').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_balance = total_income - total_expense

        # Výpočet součtu a průměrné hodnoty transakcí pro každou kategorii
        months = transactions.dates('datestamp', 'month', order='ASC')
        category_summaries = Category.objects.annotate(
            total=Coalesce(
                Sum(
                    Case(
                        When(transaction__type='expense', then=-F('transaction__amount')),
                        default=F('transaction__amount'),
                        output_field=DecimalField()
                    ),
                    filter=Q(transaction__datestamp__year=year),
                    output_field=DecimalField()
                ),
                Decimal('0')
            )
        ).annotate(
            monthly_average=Coalesce(
                Sum(
                    Case(
                        When(transaction__type='expense', then=-F('transaction__amount')),
                        default=F('transaction__amount'),
                        output_field=DecimalField()
                    ),
                    filter=Q(transaction__datestamp__year=year),
                    output_field=DecimalField()
                ) / 12,  # Využití hodnoty 12 pro výpočet průměrné hodnoty, ale neuvažuje se zde, že v aktuálně probíhajícím roce, pro který se také používá tento výpočet, ještě nemusí být všech 12 měsíců, tzn. vypočtená hodnota tedy bude výrazně nižší než by měla reálně být
                Decimal('0')
            )
        ).order_by('-total')

        # Výpočet bilance pro každou kategorii každého měsíce v daném roce
        monthly_balances = {category.name: {} for category in category_summaries}
        for month in months:
            month_balances = Category.objects.annotate(
                monthly_total=Coalesce(
                    Sum(
                        Case(
                            When(transaction__type='expense', then=-F('transaction__amount')),
                            default=F('transaction__amount'),
                            output_field=DecimalField()
                        ),
                        filter=Q(transaction__datestamp__year=year, transaction__datestamp__month=month.month),
                        output_field=DecimalField()
                    ),
                    Decimal('0')
                )
            ).order_by('-monthly_total')

            for balance in month_balances:
                monthly_balances[balance.name][month] = float(balance.monthly_total)  # Konverze Decimal na float (kvůli JSON serializaci)

        # Generování JSON dat pro graf
        category_data = []
        for category in category_summaries:
            category_data.append({
                'name': category.name,
                'color': category.color
            })
        monthly_data = {}
        for category in category_summaries:
            monthly_data[category.name] = [monthly_balances[category.name].get(month, 0) for month in months]

        # Konverze Decimal na float (kvůli JSON serializaci)
        total_income = float(total_income)
        total_expense = float(total_expense)
        total_balance = float(total_balance)

        context.update({
            'year': year,
            'category_summaries': category_summaries,
            'months': months,
            'monthly_balances': monthly_balances,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'categories_json': json.dumps(category_data),
            'months_json': json.dumps([format(month, 'F') for month in months]),
            'monthly_data_json': json.dumps(monthly_data),
        })
        return context
