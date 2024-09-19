from django.db.models import Sum, DecimalField, Q, F, Case, When, Max, Min, Avg, Value, Count
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.utils.dateformat import format
from decimal import Decimal
from datetime import date
from .models import *
from .filters import TransactionFilter
from .forms import *
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import Http404


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
            return redirect('transaction-add')
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
                return redirect('transaction-add')
        return render(request, self.template_name, {"form": form})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "Nemůžeš se odhlásit, pokud nejsi přihlášený.")
    return redirect('login')


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


class SelectBookView(LoginRequiredMixin, TemplateView):
    template_name = 'budgetlog/select_book.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.filter(owner=request.user)
        if not books:
            # Pokud uživatel nemá žádné knihy, přesměrujeme ho na vytvoření nové
            return redirect('book-create')
        return render(request, self.template_name, {'books': books})

    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        if book_id:
            book = get_object_or_404(Book, id=book_id, owner=request.user)
            request.session['current_book_id'] = book.id
            return redirect('dashboard')
        else:
            messages.error(request, "Prosím, vyberte knihu.")
            return self.get(request)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_book'] = self.get_current_book()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        current_book = self.get_current_book()
        if current_book:
            queryset = queryset.filter(book=current_book)
        return queryset


class TransactionListView(BookContextMixin, FilterView, ListView, LoginRequiredMixin):
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

        # Přidání maximální částky do kontextu
        max_amount = Transaction.objects.aggregate(Max('amount'))['amount__max']
        context['max_amount'] = max_amount

        # Načtení aktuálních hodnot z GET parametrů, pokud jsou k dispozici
        min_amount = self.request.GET.get('amount_min', 0)
        max_amount = self.request.GET.get('amount_max', max_amount)

        context['amount_min'] = min_amount
        context['amount_max'] = max_amount

        average_amount = filtered_qs.aggregate(
            avg_amount=Avg(
                Case(
                    When(type='expense', then=F('amount') * Value(-1)),
                    default=F('amount'),
                    output_field=DecimalField()
                )
            )
        )['avg_amount'] or 0
        context['average_amount'] = average_amount

        # Výpočet nejvyšší částky
        max_transaction_amount = filtered_qs.aggregate(
            max_amount=Max(
                Case(
                    When(type='expense', then=F('amount') * Value(-1)),
                    default=F('amount'),
                    output_field=DecimalField()
                )
            )
        )['max_amount'] or 0
        context['max_transaction_amount'] = max_transaction_amount

        # Výpočet nejnižší částky
        min_transaction_amount = filtered_qs.aggregate(
            min_amount=Min(
                Case(
                    When(type='expense', then=F('amount') * Value(-1)),
                    default=F('amount'),
                    output_field=DecimalField()
                )
            )
        )['min_amount'] or 0
        context['min_transaction_amount'] = min_transaction_amount

        # Výpočet bilance (suma příjmů - suma výdajů)
        balance = filtered_qs.aggregate(
            total_balance=Sum(
                Case(
                    When(type='expense', then=F('amount') * Value(-1)),
                    default=F('amount'),
                    output_field=DecimalField()
                )
            )
        )['total_balance'] or 0
        context['balance'] = balance

        # Počet filtrovaných transakcí
        transaction_count = filtered_qs.aggregate(count=Count('id'))['count']
        context['transaction_count'] = transaction_count

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs


class TransactionCreateView(CreateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli vytvořit novou transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')
    # Po vytvoření transakce přesměruje uživatele na 'transaction-list', tzn. "transaction/"

    def form_valid(self, form):
        form.instance.book = self.get_current_book()  # Přiřadíme aktuální knihu transakci
        return super().form_valid(form)


class TransactionDetailView(DeleteView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli náhled na veškeré informace o transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_detail.html'
    context_object_name = 'transaction'


class TransactionUpdateView(UpdateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli upravit existující transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'
    success_url = reverse_lazy('transaction-list')


class TransactionDeleteView(DeleteView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli smazat transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')


class CategoryListView(ListView, LoginRequiredMixin, BookContextMixin):
    """Zobrazí seznam všech kategorií."""
    model = Category
    template_name = 'budgetlog/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']  # Řazení dle atributu name v modelu Category


class CategoryCreateView(CreateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli vytvořit novou kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(UpdateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli upravit existující kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(DeleteView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli smazat kategorii."""
    model = Category
    template_name = 'budgetlog/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


class AccountListView(ListView, LoginRequiredMixin, BookContextMixin):
    """Zobrazí seznam všech účtů."""
    model = Account
    template_name = 'budgetlog/account_list.html'
    context_object_name = 'accounts'
    ordering = ['name']  # Řazení dle atributu name v modelu Account


class AccountCreateView(CreateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli vytvořit nový účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountUpdateView(UpdateView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli upravit existující účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountDeleteView(DeleteView, LoginRequiredMixin, BookContextMixin):
    """Umožní uživateli smazat účet."""
    model = Account
    template_name = 'budgetlog/account_confirm_delete.html'
    success_url = reverse_lazy('account-list')


class DashboardView(TemplateView, LoginRequiredMixin, BookContextMixin):
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


class MonthDetailView(TemplateView, LoginRequiredMixin, BookContextMixin):
    """Templát pro detailní statistiky daného měsíce."""
    template_name = 'budgetlog/monthly_detail.html'

    def get_context_data(self, year, month, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.filter(
            datestamp__year=year,
            datestamp__month=month
        ).order_by('-datestamp')  # Seřazení dle data, nejnovější nahoře

        # Výpočet celkových měsíčních příjmů a výdajů
        total_income = transactions.filter(type='income').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_expense = transactions.filter(type='expense').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_balance = total_income - total_expense

        # Konverze Decimal na float (kvůli snadné práci v šabloně)
        total_income = float(total_income)
        total_expense = float(total_expense)
        total_balance = float(total_balance)

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
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'category_summaries': category_summaries,
        })
        return context


class YearDetailView(TemplateView, LoginRequiredMixin, BookContextMixin):
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

        # Data potřebná pro výpočet průměrných měsíčních hodnot v daném roce
        # Získání aktuálního roku a měsíce
        current_year = date.today().year
        current_month = date.today().month

        # Pokud se zpracovává aktuální rok, použijeme aktuální měsíc jako počet měsíců
        if year == current_year:
            month_count = current_month
        else:
            # Pokud se zpracovává jiný než aktuální rok, použijeme 12 měsíců
            month_count = 12

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
                ) / month_count,
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
