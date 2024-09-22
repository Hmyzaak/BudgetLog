from django.db.models import Sum, DecimalField, Q, F, Case, When, Max, Min, Avg, Value, Count
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django.utils.dateformat import format
from decimal import Decimal
from datetime import date
from .filters import TransactionFilter
from .forms import *
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


# Create your views here.
# Všechny třídy dědí z generických View podle toho, co s daným modelem mají dělat.
class UserViewRegister(CreateView):
    form_class = UserForm
    model = AppUser
    template_name = 'budgetlog/user_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()

            # Po uložení uživatele mu vytvoříme knihu
            book = Book.objects.create(name="Moje kniha", owner=user)
            request.session['current_book_id'] = book.id  # Nastavíme novou knihu jako aktuální

            login(request, user)
            return redirect('book-list')
        return render(request, self.template_name, {"form": form})


class UserViewLogin(CreateView):
    form_class = LoginForm
    template_name = 'budgetlog/user_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form. cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('book-list')
        return render(request, self.template_name, {"form": form})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "Nemůžeš se odhlásit, pokud nejsi přihlášený.")
    return redirect('login')


class BookContextMixin:
    """Mixin, který poskytne aktuální knihu uživatele v pohledech."""

    def get_current_book(self):
        """Vrátí aktuální knihu uživatele na základě session nebo výběru."""
        current_book_id = self.request.session.get('current_book_id', None)
        if current_book_id:
            try:
                return Book.objects.get(id=current_book_id, owner=self.request.user)
            except Book.DoesNotExist:
                return None
        return None

    def form_valid(self, form):
        form.instance.book = self.get_current_book()  # Přiřadíme aktuální knihu transakci
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_book'] = self.get_current_book()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        current_book = self.get_current_book()
        if current_book:
            queryset = queryset.filter(book=current_book)
        else:
            queryset = queryset.none()  # Pokud není aktuální kniha, nevrátit nic
        return queryset


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'budgetlog/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['name', 'description']
    template_name = 'budgetlog/book_form.html'
    success_url = reverse_lazy('book-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['name', 'description']
    template_name = 'budgetlog/book_form.html'
    success_url = reverse_lazy('book-list')

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'budgetlog/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class SelectBookView(LoginRequiredMixin, View):
    """View pro zpracování výběru knihy uživatelem."""

    @staticmethod
    def get(request, *args, **kwargs):
        # Získání ID knihy z URL
        book_id = kwargs.get('book_id')
        if book_id:
            # Ověření, že kniha patří uživateli
            book = get_object_or_404(Book, id=book_id, owner=request.user)
            # Nastavení aktivní knihy v session
            request.session['current_book_id'] = book.id
            # Přesměrování na stránku s transakcemi nebo jinou stránku po výběru knihy
            return redirect('transaction-list')  # Nebo jiný název URL pro zobrazení transakcí
        else:
            messages.error(request, "Kniha nebyla nalezena.")
            return redirect('book-list')


class TransactionSummaryMixin:
    def get_transactions(self, year=None, month=None):
        """Získá transakce podle roku, měsíce a aktuální knihy."""
        current_book = self.get_current_book()
        if not current_book:
            messages.error(self.request, "Musíte si vybrat knihu.")
            return redirect('book-list')

        queryset = Transaction.objects.filter(book=current_book)
        if year:
            queryset = queryset.filter(datestamp__year=year)
        if month:
            queryset = queryset.filter(datestamp__month=month)

        return queryset.order_by('-datestamp')

    @staticmethod
    def get_additional_context_data(filtered_qs):
        # Výpočet agregátů (např. průměr, max/min částka) a jejich přidání do kontextu
        return {
            'max_amount': Transaction.objects.aggregate(Max('amount'))['amount__max'],
            'average_amount': filtered_qs.aggregate(
                avg_amount=Avg(
                    Case(
                        When(type='expense', then=F('amount') * Value(-1)),
                        default=F('amount'),
                        output_field=DecimalField()
                    )
                )
            )['avg_amount'] or 0,
            'max_transaction_amount': filtered_qs.aggregate(
                max_amount=Max(
                    Case(
                        When(type='expense', then=F('amount') * Value(-1)),
                        default=F('amount'),
                        output_field=DecimalField()
                    )
                )
            )['max_amount'] or 0,
            'min_transaction_amount': filtered_qs.aggregate(
                min_amount=Min(
                    Case(
                        When(type='expense', then=F('amount') * Value(-1)),
                        default=F('amount'),
                        output_field=DecimalField()
                    )
                )
            )['min_amount'] or 0,
            'balance': filtered_qs.aggregate(
                total_balance=Sum(
                    Case(
                        When(type='expense', then=F('amount') * Value(-1)),
                        default=F('amount'),
                        output_field=DecimalField()
                    )
                )
            )['total_balance'] or 0,
            'transaction_count': filtered_qs.aggregate(count=Count('id'))['count']
        }

    @staticmethod
    def calculate_totals(transactions):
        """Výpočet celkových hodnot pro příjem, výdaje a bilanci."""
        total_income = transactions.filter(type='income').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_expense = transactions.filter(type='expense').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_balance = total_income - total_expense
        return float(total_income), float(total_expense), float(total_balance)

    def get_category_summaries(self, transactions, year=None, month=None):
        """Získá souhrny kategorií pro daný rok a měsíc."""
        current_book = self.get_current_book()
        category_summaries = Category.objects.filter(book=current_book).annotate(
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

        return category_summaries


class TransactionListView(LoginRequiredMixin, BookContextMixin, TransactionSummaryMixin, FilterView, ListView):
    """Umožňuje vytvořit a držet data pro filtrování v seznamu transakcí a umožňuje stránkování v těchto seznamech."""
    model = Transaction
    filterset_class = TransactionFilter
    template_name = 'budgetlog/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 30
    ordering = ['-datestamp']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filterset = self.filterset_class(self.request.GET,
                                         queryset=self.get_queryset(),
                                         book=self.get_current_book())
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
        # Přidání dalších dat do kontextu (např. bilance, max/min částky atd.)
        context.update(self.get_additional_context_data(filtered_qs))

        return context


class TransactionCreateView(BookContextMixin, LoginRequiredMixin, CreateView):
    """Umožní uživateli vytvořit novou transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')
    # Po vytvoření transakce přesměruje uživatele na 'transaction-list', tzn. "transaction/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Předáme aktuální knihu do formuláře
        kwargs['book'] = self.get_current_book()  # Funkce z BookContextMixin
        return kwargs


class TransactionDetailView(LoginRequiredMixin, BookContextMixin, DeleteView):
    """Umožní uživateli náhled na veškeré informace o transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_detail.html'
    context_object_name = 'transaction'

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        transaction = get_object_or_404(Transaction, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class TransactionUpdateView(LoginRequiredMixin, BookContextMixin, UpdateView):
    """Umožní uživateli upravit existující transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        transaction = get_object_or_404(Transaction, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class TransactionDeleteView(LoginRequiredMixin, BookContextMixin, DeleteView):
    """Umožní uživateli smazat transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        transaction = get_object_or_404(Transaction, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, BookContextMixin, ListView):
    """Zobrazí seznam všech kategorií."""
    model = Category
    template_name = 'budgetlog/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']  # Řazení dle atributu name v modelu Category


class CategoryCreateView(LoginRequiredMixin, BookContextMixin, CreateView):
    """Umožní uživateli vytvořit novou kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(LoginRequiredMixin, BookContextMixin, UpdateView):
    """Umožní uživateli upravit existující kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        category = get_object_or_404(Category, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class CategoryDeleteView(LoginRequiredMixin, BookContextMixin, DeleteView):
    """Umožní uživateli smazat kategorii."""
    model = Category
    template_name = 'budgetlog/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        category = get_object_or_404(Category, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class AccountListView(LoginRequiredMixin, BookContextMixin, ListView):
    """Zobrazí seznam všech účtů."""
    model = Account
    template_name = 'budgetlog/account_list.html'
    context_object_name = 'accounts'
    ordering = ['name']  # Řazení dle atributu name v modelu Account


class AccountCreateView(LoginRequiredMixin, BookContextMixin, CreateView):
    """Umožní uživateli vytvořit nový účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountUpdateView(LoginRequiredMixin, BookContextMixin, UpdateView):
    """Umožní uživateli upravit existující účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        account = get_object_or_404(Account, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class AccountDeleteView(LoginRequiredMixin, BookContextMixin, DeleteView):
    """Umožní uživateli smazat účet."""
    model = Account
    template_name = 'budgetlog/account_confirm_delete.html'
    success_url = reverse_lazy('account-list')

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        account = get_object_or_404(Account, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class MonthDetailView(LoginRequiredMixin, BookContextMixin, TransactionSummaryMixin, TemplateView):
    """Templát pro detailní statistiky daného měsíce."""
    template_name = 'budgetlog/monthly_detail.html'

    def get_context_data(self, year, month, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_transactions(year=year, month=month)
        total_income, total_expense, total_balance = self.calculate_totals(transactions)
        category_summaries = self.get_category_summaries(transactions, year=year, month=month)

        context.update({
            'year': year,
            'month': month,
            'transactions': transactions,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'category_summaries': category_summaries,
        })
        return context


class YearDetailView(LoginRequiredMixin, BookContextMixin, TransactionSummaryMixin, TemplateView):
    """Templát pro zobrazení statistik transakcí u vybraného roku."""
    template_name = 'budgetlog/yearly_detail.html'

    def get_context_data(self, year, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_transactions(year=year)
        total_income, total_expense, total_balance = self.calculate_totals(transactions)
        months, category_summaries, monthly_balances = self.get_yearly_category_summaries(year)

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

    def get_yearly_category_summaries(self, year):
        """Získá souhrny kategorií a měsíční bilance pro daný rok."""
        current_book = self.get_current_book()
        transactions = self.get_transactions(year=year)

        # Pokud se zpracovává aktuální rok, použijeme aktuální měsíc jako počet měsíců, jinak hodnotu 12
        month_count = date.today().month if year == date.today().year else 12
        # Agregace transakcí podle kategorií za celý rok
        category_summaries = Category.objects.filter(book=current_book).annotate(
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
                ) / month_count,
                Decimal('0')
            )
        ).order_by('-total')

        # Výpočet součtu a průměrné hodnoty transakcí pro každou kategorii
        months = transactions.dates('datestamp', 'month', order='ASC')
        # Výpočet bilance pro každou kategorii každého měsíce v daném roce
        monthly_balances = {category.name: {} for category in category_summaries}
        for month in months:
            month_balances = Category.objects.filter(book=current_book).annotate(
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

            # Konverze Decimal na float (kvůli JSON serializaci)
            for balance in month_balances:
                monthly_balances[balance.name][month] = float(balance.monthly_total)

        return months, category_summaries, monthly_balances


class DashboardView(LoginRequiredMixin, BookContextMixin, TransactionSummaryMixin, TemplateView):
    """Templát pro stránku se souhrnnými přehledy."""
    template_name = 'budgetlog/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_transactions()
        months_years = transactions.dates('datestamp', 'month', order='DESC')
        years = transactions.dates('datestamp', 'year', order='DESC')

        context.update({
            'months_years': months_years,
            'years': years,
        })
        return context
