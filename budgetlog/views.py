from django.db.models import Sum, DecimalField, Q, F, Case, When, Max, Min, Avg, Value, Count
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
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
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


# Create your views here.
# Všechny třídy dědí z generických View podle toho, co s daným modelem mají dělat.
class ProjectCreateView(CreateView):
    form_class = ProjectForm
    template_name = 'budgetlog/project_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            emails = form.cleaned_data['users'].split(',')
            for email in emails:
                user = AppUser.objects.get(email=email.strip())
                project.users.add(user)
            return redirect('project-list')
        return render(request, self.template_name, {'form': form})


class ProjectListView(ListView):
    template_name = 'budgetlog/project_list.html'

    def get(self, request):
        projects = Project.objects.filter(users=request.user)
        return render(request, self.template_name, {'projects': projects})


class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id', None)
        context['project_id'] = project_id
        return context


class TransactionListView(BaseView, FilterView, ListView):
    """Umožňuje vytvořit a držet data pro filtrování v seznamu transakcí a umožňuje stránkování v těchto seznamech"""
    model = Transaction
    filterset_class = TransactionFilter
    template_name = 'budgetlog/transaction_list.html'
    context_object_name = 'transactions'
    # nastavuje název proměnné, která bude použita v šabloně pro přístup k seznamu transakcí: Výchozí název proměnné
    # by byl object_list
    paginate_by = 30  # Počet transakcí na stránku
    ordering = ['-datestamp']  # Řazení transakcí podle data od nejnovějších

    def get_queryset(self):
        # Získání aktuálního projektu na základě URL parametru
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)

        # Filtrování transakcí podle projektu
        queryset = super().get_queryset().filter(project=project)

        # Použití filtru
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)

        context['project'] = project
        context['transactions'] = self.get_queryset() # Upravit?

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


class TransactionCreateView(BaseView, CreateView):
    """Umožní uživateli vytvořit novou transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'

    def form_valid(self, form):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        transaction = form.save(commit=False)
        transaction.project = project
        transaction.save()
        return redirect('transaction-list', project_id=project.id)


class TransactionDetailView(BaseView, DeleteView):
    """Umožní uživateli náhled na veškeré informace o transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_detail.html'
    context_object_name = 'transaction'

    def get_object(self, queryset=None):
        transaction = super().get_object(queryset)
        project = transaction.project
        if self.request.user not in project.users.all():
            raise Http404("Nemáte přístup k této transakci.")
        return transaction


class TransactionUpdateView(BaseView, UpdateView):
    """Umožní uživateli upravit existující transakci."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgetlog/transaction_form.html'

    def get_object(self, queryset=None):
        transaction = super().get_object(queryset)
        project = transaction.project
        if self.request.user not in project.users.all():
            raise Http404("Nemáte přístup k této transakci.")
        return transaction

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.save()
        return redirect('transaction-list', project_id=transaction.project.id)


class TransactionDeleteView(BaseView, DeleteView):
    """Umožní uživateli smazat transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')

    def get_object(self, queryset=None):
        transaction = super().get_object(queryset)
        project = transaction.project
        if self.request.user not in project.users.all():
            raise Http404("Nemáte přístup k této transakci.")
        return transaction

    def get_success_url(self):
        transaction = self.get_object()
        return reverse_lazy('transaction-list', kwargs={'project_id': transaction.project.id})


class CategoryListView(BaseView, ListView):
    """Zobrazí seznam všech kategorií."""
    model = Category
    template_name = 'budgetlog/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']  # Řazení dle atributu name v modelu Category

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        return Category.objects.filter(project=project)


class CategoryCreateView(BaseView, CreateView):
    """Umožní uživateli vytvořit novou kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'

    def form_valid(self, form):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        category = form.save(commit=False)
        category.project = project
        category.save()
        return redirect('category-list', project_id=project.id)


class CategoryUpdateView(BaseView, UpdateView):
    """Umožní uživateli upravit existující kategorii."""
    model = Category
    form_class = CategoryForm
    template_name = 'budgetlog/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(BaseView, DeleteView):
    """Umožní uživateli smazat kategorii."""
    model = Category
    template_name = 'budgetlog/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


class AccountListView(BaseView, ListView):
    """Zobrazí seznam všech účtů."""
    model = Account
    template_name = 'budgetlog/account_list.html'
    context_object_name = 'accounts'
    ordering = ['name']  # Řazení dle atributu name v modelu Account

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        return Account.objects.filter(project=project)


class AccountCreateView(BaseView, CreateView):
    """Umožní uživateli vytvořit nový účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'

    def form_valid(self, form):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        account = form.save(commit=False)
        account.project = project
        account.save()
        return redirect('account-list', project_id=project.id)


class AccountUpdateView(BaseView, UpdateView):
    """Umožní uživateli upravit existující účet."""
    model = Account
    form_class = AccountForm
    template_name = 'budgetlog/account_form.html'
    success_url = reverse_lazy('account-list')


class AccountDeleteView(BaseView, DeleteView):
    """Umožní uživateli smazat účet."""
    model = Account
    template_name = 'budgetlog/account_confirm_delete.html'
    success_url = reverse_lazy('account-list')


class DashboardView(BaseView, TemplateView):
    """Templát pro stránku se souhrnnými přehledy."""
    template_name = 'budgetlog/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id, users=self.request.user)
        transactions = Transaction.objects.filter(project=project)
        months_years = transactions.dates('datestamp', 'month', order='DESC')
        years = transactions.dates('datestamp', 'year', order='DESC')

        context.update({
            'project_id': project_id,
            'project': project,
            'months_years': months_years,
            'years': years,
        })

        return context


class MonthDetailView(BaseView, TemplateView):
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


class YearDetailView(BaseView, TemplateView):
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

