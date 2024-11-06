# Standardní knihovny Pythonu
import csv
import json
import random
from datetime import date
from decimal import Decimal
from io import StringIO, TextIOWrapper

# Django importy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import (
    Sum, DecimalField, Q, F, Case, When, Max, Min, Avg, Value, Count
)
from django.db.models.functions import Coalesce
from django.http import (
    HttpResponse, HttpResponseForbidden, JsonResponse, QueryDict, HttpResponseRedirect
)
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.dateformat import format
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

# Třetí strany
from django_filters.views import FilterView

# Lokální aplikace
from budgetlog.models import AppUser, Book
from .filters import TransactionFilter
from .forms import *


# Create your views here.
# Všechny třídy dědí z generických View podle toho, co s daným modelem mají dělat.
class UserViewRegister(CreateView):
    form_class = UserRegistrationForm
    model = AppUser
    template_name = 'budgetlog/user_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form, "title": "Registrace"})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password1')  # Správné heslo z validovaných dat
            user.set_password(password)
            user.save()

            login(request, user)
            return redirect('setup-book')  # Přesměrování na stránku pro vytvoření knihy, kategorií a účtu
        return render(request, self.template_name, {"form": form, "title": "Registrace"})


class UserViewLogin(CreateView):
    form_class = LoginForm
    template_name = 'budgetlog/user_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form, "title": "Přihlášení"})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form. cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('book-list')
        return render(request, self.template_name, {"form": form, "title": "Přihlášení"})


class ProfileView(LoginRequiredMixin, TemplateView):
    """View pro zobrazení uživatelského profilu"""
    template_name = 'budgetlog/profile.html'


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    """View pro změnu hesla"""
    form_class = CustomPasswordChangeForm
    template_name = 'budgetlog/change_password.html'
    success_url = reverse_lazy('profile')  # Po úspěšné změně hesla se přesměruje na profil

    def form_valid(self, form):
        messages.success(self.request, 'Heslo bylo úspěšně změněno.')
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    """View pro smazání uživatelského účtu"""
    model = get_user_model()  # Django automaticky zvolí model uživatele
    template_name = 'budgetlog/delete_account.html'
    success_url = reverse_lazy('login')  # Po smazání přesměrujeme na přihlášení

    def get_object(self, queryset=None):
        return self.request.user  # Vrátí aktuálně přihlášeného uživatele

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Váš účet byl úspěšně smazán.')
        return super().delete(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    email_template_name = 'registration/password_reset_email.txt'  # Textová verze
    html_email_template_name = 'registration/password_reset_email.html'  # HTML verze
    subject_template_name = 'registration/password_reset_subject.txt'  # Předmět v emailu
    success_url = reverse_lazy('password_reset_done')  # Úspěšné přesměrování

    def form_valid(self, form):
        """
        Po validaci formuláře odešle email ve formátu HTML pomocí `EmailMultiAlternatives`.
        """
        user_email = form.cleaned_data['email']
        users = AppUser.objects.filter(email=user_email)

        for user in users:
            # Nastavení kontextu
            context = {
                'email': user.email,
                'domain': self.request.META['HTTP_HOST'],
                'site_name': 'BudgetLog',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if self.request.is_secure() else 'http',
            }

            # Generování předmětu, textové a HTML verze zprávy
            subject = render_to_string(self.subject_template_name, context).strip()
            text_content = render_to_string(self.email_template_name, context)
            html_content = render_to_string(self.html_email_template_name, context)

            # Nastavení emailu s více alternativami
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,  # Textová verze jako hlavní tělo
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")  # Připojení HTML verze
            email.send()

        # Vrácení vlastní odpovědi pro přesměrování po úspěšném odeslání e-mailu
        return HttpResponseRedirect(self.success_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetForm  # Vlastní formulář s českými popisky
    success_url = reverse_lazy('password_reset_complete')  # Kam se přesměruje po úspěšném resetu


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "Nemůžeš se odhlásit, pokud nejsi přihlášený.")
    return redirect('login')


class SetupBookView(LoginRequiredMixin, CreateView):
    template_name = 'budgetlog/setup_book.html'
    context_object_name = 'setup-book'

    def get(self, request):
        # Navrhneme defaultní kategorie
        default_categories = ['Jídlo', 'Bydlení', 'Doprava', 'Zábava']
        return render(request, self.template_name, {'categories': default_categories})

    def post(self, request):
        book_name = request.POST.get('book_name', 'Základní kniha')
        selected_categories = request.POST.getlist('categories')
        custom_categories = request.POST.get('custom_categories')

        if not selected_categories and not custom_categories:
            messages.error(request, 'Musíte vybrat alespoň jednu kategorii.')
            return redirect('setup-book')

        # Vytvoření knihy
        book = Book.objects.create(name=book_name, owner=request.user)
        request.session['current_book_id'] = book.id

        # Funkce pro vytvoření kategorie s náhodnou barvou
        def create_category(category_name, book):
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            Category.objects.create(name=category_name.strip(), color=color, book=book)

        # Vytvoření vybraných kategorií
        if selected_categories:
            for category_name in selected_categories:
                create_category(category_name, book)

        # Vytvoření vlastních kategorií, pokud byly zadány
        if custom_categories:
            custom_category_names = [name.strip() for name in custom_categories.split(',') if name.strip()]
            for category_name in custom_category_names:
                create_category(category_name, book)

        return redirect('transaction-list')  # Po dokončení nastavení přesměrujeme uživatele na seznam transakcí


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['name', 'description']
    template_name = 'budgetlog/object_form.html'
    success_url = reverse_lazy('book-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = self.model._meta.verbose_name
        context['list_url_name'] = f'{self.model._meta.model_name}-list'
        return context


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ['name', 'description']
    template_name = 'budgetlog/object_form.html'
    success_url = reverse_lazy('book-list')

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = self.model._meta.verbose_name
        context['list_url_name'] = f'{self.model._meta.model_name}-list'
        return context


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
        # Jen pokud form existuje a má instanci (Create/Update)
        if hasattr(form, 'instance'):
            form.instance.book = self.get_current_book()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_books'] = Book.objects.filter(owner=self.request.user)
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

    @staticmethod
    def get_additional_context_data(filtered_qs):
        # Výpočet agregátů (např. průměr, max/min částka) a jejich přidání do kontextu
        return {
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
    def calculate_totals(filtered_qs):
        """Výpočet celkových hodnot pro příjem, výdaje a bilanci."""
        total_income = filtered_qs.filter(type='income').aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0'))
        )['total']

        total_expense = filtered_qs.filter(type='expense').aggregate(
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
    template_name = 'budgetlog/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-datestamp']
    filterset_class = TransactionFilter
    paginate_by = 30

    def get_filterset_kwargs(self, filterset_class):
        """Přidává aktuální knihu do filtrů."""
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['book'] = self.get_current_book()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filterset = self.filterset_class(self.request.GET, queryset=self.get_queryset(), book=self.get_current_book())
        context['filter'] = filterset
        request = self.request
        filtered_qs = filterset.qs

        # Získání tagů a kategorií pouze z aktuální knihy
        context['all_tags'] = Tag.objects.filter(book=self.get_current_book())
        context['all_categories'] = Category.objects.filter(book=self.get_current_book())

        # Výpočet souhrnů a přidání do kontextu
        summary_data = self.get_additional_context_data(filtered_qs)
        context.update(summary_data)

        # Paginace
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

    def get(self, request, *args, **kwargs):
        """Zpracuje GET požadavek a rozhodne, zda vrátí JSON nebo HTML."""
        if self.is_ajax():
            # Pokud je požadavek přes AJAX, vrátí JSON odpověď
            filterset = self.filterset_class(self.request.GET, queryset=self.get_queryset(),
                                             book=self.get_current_book())
            all_transaction_ids = list(filterset.qs.values_list('id', flat=True))
            return JsonResponse({'transaction_ids': all_transaction_ids})
        else:
            # Jinak normálně vykreslí stránku s šablonou
            return super().get(request, *args, **kwargs)

    def is_ajax(self):
        return self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class TransactionDetailView(LoginRequiredMixin, BookContextMixin, DeleteView):
    """Umožní uživateli náhled na veškeré informace o transakci."""
    model = Transaction
    template_name = 'budgetlog/transaction_detail.html'
    context_object_name = 'transaction'

    def dispatch(self, request, *args, **kwargs):
        current_book = self.get_current_book()
        transaction = get_object_or_404(Transaction, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class ObjectListView(LoginRequiredMixin, BookContextMixin, ListView):
    template_name = 'budgetlog/object_list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_plural_genitiv'] = self.model.object_plural_genitiv
        context['object_singular_akluzativ'] = self.model.object_singular_akluzativ
        context['add_url_name'] = f'{self.model._meta.model_name}-add'
        context['edit_url_name'] = f'{self.model._meta.model_name}-edit'
        context['delete_url_name'] = f'{self.model._meta.model_name}-delete'
        return context


class BookListView(ObjectListView):
    model = Book
    ordering = ['name']  # Řazení dle atributu name v modelu

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class CategoryListView(ObjectListView):
    """Zobrazí seznam všech kategorií."""
    model = Category
    ordering = ['name']  # Řazení dle atributu name v modelu Category


class TagListView(ObjectListView):
    """Zobrazí seznam všech tagů."""
    model = Tag
    ordering = ['name']  # Řazení dle atributu name v modelu Account


class ObjectFormView(LoginRequiredMixin, BookContextMixin):
    template_name = 'budgetlog/object_form.html'

    def get_success_url_with_filters(self):
        """Vrátí URL na seznam objektů s uloženými filtry."""
        model_name = self.model.__name__.lower()
        base_url = reverse_lazy(f'{model_name}-list')

        # Získáme filtry z requestu (pokud nějaké existují)
        query_params = self.request.GET.copy()
        query_params.pop('csrfmiddlewaretoken', None)

        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

    def get_success_url(self):
        """Vrátí URL na seznam objektů po úspěšné akci s filtry."""
        return self.get_success_url_with_filters()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_singular_akluzativ'] = self.model.object_singular_akluzativ
        context['list_url_name'] = self.get_success_url_with_filters()  # Přidáme uložené filtry do URL
        return context

    def dispatch(self, request, *args, **kwargs):
        # Ověříme, zda tato třída dědí z UpdateView (u CreateView by vyhazovala KeyError)
        if issubclass(self.__class__, UpdateView):
            current_book = self.get_current_book()
            obj = get_object_or_404(self.model, pk=self.kwargs['pk'], book=current_book)
        return super().dispatch(request, *args, **kwargs)


class TransactionCreateView(ObjectFormView, CreateView):
    model = Transaction
    form_class = TransactionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Předáme aktuální knihu do formuláře
        kwargs['book'] = self.get_current_book()  # Funkce z BookContextMixin
        return kwargs


class CategoryCreateView(ObjectFormView, CreateView):
    model = Category
    form_class = CategoryForm


class TagCreateView(ObjectFormView, CreateView):
    model = Tag
    form_class = TagForm


class TransactionUpdateView(ObjectFormView, UpdateView):
    model = Transaction
    form_class = TransactionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Předáme aktuální knihu do formuláře
        kwargs['book'] = self.get_current_book()
        return kwargs


class CategoryUpdateView(ObjectFormView, UpdateView):
    model = Category
    form_class = CategoryForm


class TagUpdateView(ObjectFormView, UpdateView):
    model = Tag
    form_class = TagForm


class GenericDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'budgetlog/object_confirm_delete.html'

    def get_success_url_with_filters(self):
        """Vrátí URL na seznam objektů s uloženými filtry."""
        model_name = self.model.__name__.lower()
        base_url = reverse_lazy(f'{model_name}-list')

        # Získání pouze GET parametrů (např. z URL)
        query_params = self.request.GET.copy()

        # Odebereme CSRF token a další nevhodné parametry
        query_params.pop('csrfmiddlewaretoken', None)

        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

    def get_success_url(self):
        """Vrátí URL na seznam objektů po úspěšné akci s filtry."""
        return self.get_success_url_with_filters()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_singular_akluzativ'] = self.model.object_singular_akluzativ
        context['list_url_name'] = self.get_success_url_with_filters()  # Přidáme uložené filtry do URL
        return context


class BookDeleteView(GenericDeleteView):
    model = Book

    def delete(self, request, *args, **kwargs):
        book = self.get_object()

        # Získat výchozí kategorii pro danou knihu
        default_category = Category.objects.get(book=book, is_default=True)

        # Aktualizovat transakce spojené s touto knihou
        Transaction.objects.filter(category__book=book).update(category=default_category)

        # Pokud je potřeba knihu archivovat nebo smazat
        return super().delete(request, *args, **kwargs)


class TransactionDeleteView(BookContextMixin, GenericDeleteView):
    model = Transaction


class CategoryDeleteView(BookContextMixin, GenericDeleteView):
    model = Category

    def dispatch(self, request, *args, **kwargs):
        category = self.get_object()
        if category.is_default:
            # Zamezit mazání výchozí kategorie
            return HttpResponseForbidden("Tuto kategorii nelze smazat.")
        return super().dispatch(request, *args, **kwargs)


class TagDeleteView(BookContextMixin, GenericDeleteView):
    model = Tag


class MonthDetailView(LoginRequiredMixin, BookContextMixin, TransactionSummaryMixin, TemplateView):
    """Templát pro detailní statistiky daného měsíce."""
    template_name = 'budgetlog/monthly_detail.html'

    def get_context_data(self, year, month, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.filter(book=self.get_current_book(), datestamp__year=year, datestamp__month=month)
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
        transactions = Transaction.objects.filter(book=self.get_current_book(), datestamp__year=year)
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
        transactions = Transaction.objects.filter(book=self.get_current_book(), datestamp__year=year)

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
        transactions = Transaction.objects.filter(book=self.get_current_book())
        months_years = transactions.dates('datestamp', 'month', order='DESC')
        years = transactions.dates('datestamp', 'year', order='DESC')

        context.update({
            'months_years': months_years,
            'years': years,
        })
        return context


class BulkTransactionActionView(LoginRequiredMixin, BookContextMixin, View):
    """Umožňuje provádět hromadné operace na vyfiltrovaných transakcích."""
    filterset_class = TransactionFilter

    def get_filtered_queryset(self, request):
        """Získá vyfiltrované transakce podle aktuálních filtrů."""
        filterset = TransactionFilter(request.GET, queryset=Transaction.objects.filter(book=self.get_current_book()))
        return filterset.qs

    def get_redirect_url_with_filters(self, request):
        """Vrátí URL zpět na stránku s transakcemi s původními filtry."""
        # Vytvoření URL na základě filtrů z requestu
        base_url = reverse('transaction-list')  # 'transaction-list' je URL jméno vaší stránky s transakcemi
        query_params = request.POST.copy()  # Zkopíruje původní POST parametry, které zahrnují i filtry z GET
        query_params.pop('csrfmiddlewaretoken', None)  # Odstraní CSRF token, ten do URL nepatří
        query_params.pop('selected_transactions', None)  # Odstraní vybrané transakce, ty nejsou pro URL potřeba
        if query_params:
            return f"{base_url}?{query_params.urlencode()}"
        return base_url

    def post(self, request, *args, **kwargs):
        # Získání ID aktuální knihy
        print(f"Obsah request.POST požadavku: {request.POST}")
        book = self.get_current_book()

        # Získání seznamu vybraných transakcí
        selected_transactions = request.POST.get('selected_transactions')
        print(f"Získání seznamu vybraných transakcí: {selected_transactions}")

        if not selected_transactions:
            messages.warning(request, "Nevybrali jste žádné transakce.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

        # Převedeme seznam id transakcí z řetězce na seznam integerů
        transaction_ids = [int(tid) for tid in selected_transactions.split(',') if tid]
        transactions = Transaction.objects.filter(id__in=transaction_ids)

        # Zpracování jednotlivých akcí podle toho, co bylo zvoleno za akci
        action = request.POST.get('action')
        if action == 'assign_tag':
            return self.assign_tag(request, transactions, book)
        elif action == 'remove_tag':
            return self.remove_tag(request, transactions, book)
        elif action == 'change_category':
            return self.change_category(request, transactions, book)
        elif action == 'delete':
            return self.delete_transactions(request, transactions)
        elif action == 'export_csv':
            return self.export_transactions_to_csv(request, transactions)
        elif action == 'move_to_book':
            return self.move_transactions_to_book(request, transactions)
        else:
            messages.error(request, "Neplatná akce.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

    def assign_tag(self, request, transactions, book):
        """Přiřadí tag vybraným transakcím."""
        tag_id = request.POST.get('bulk_tag')
        if not tag_id:
            messages.warning(request, "Nevybrali jste žádný tag.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

        tag = get_object_or_404(Tag, id=tag_id, book=book)  # Tag musí být z aktuální knihy
        for transaction in transactions:
            transaction.tags.add(tag)
        messages.success(request, f"{transactions.count()} transakcím byl přiřazen tag: {tag.name}.")
        # Přesměrování na stránku s původními filtry
        return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

    def remove_tag(self, request, transactions, book):
        """Odebere tag z vybraných transakcí."""
        tag_id = request.POST.get('bulk_remove_tag')
        if not tag_id:
            messages.warning(request, "Nevybrali jste žádný tag k odebrání.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

        tag = get_object_or_404(Tag, id=tag_id, book=book)  # Tag musí být z aktuální knihy
        for transaction in transactions:
            transaction.tags.remove(tag)
        messages.success(request, f"{transactions.count()} transakcím byl odebrán tag: {tag.name}.")
        return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

    def change_category(self, request, transactions, book):
        """Změní kategorii vybraných transakcí."""
        category_id = request.POST.get('bulk_category')
        if not category_id:
            messages.warning(request, "Nevybrali jste žádnou kategorii.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

        category = get_object_or_404(Category, id=category_id, book=book)  # Kategorie musí být z aktuální knihy
        transactions.update(category=category)
        messages.success(request, f"Kategorie změněna u {transactions.count()} transakcí na: {category.name}.")
        return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

    def delete_transactions(self, request, transactions):
        """Smaže vybrané transakce."""
        count = transactions.count()
        transactions.delete()
        messages.success(request, f"Smazáno {count} transakcí.")
        return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

    def export_transactions_to_csv(self, request, transactions):
        """Exportuje vybrané transakce do CSV souboru."""
        # Nastavení HTTP odpovědi pro CSV export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        # Použití StringIO pro zápis do paměti
        output = StringIO()
        writer = csv.writer(output)

        # Zápis hlavičky do CSV
        writer.writerow(['ID', 'Datum', 'Kategorie', 'Částka', 'Tagy', 'Popis', 'Typ', 'Kniha'])

        # Záznamy do CSV
        for transaction in transactions:
            writer.writerow([
                transaction.id,
                transaction.datestamp,
                transaction.category.name,
                transaction.adjusted_amount,
                transaction.display_tags(transaction),
                transaction.description,
                transaction.type,
                transaction.book,
            ])

        # Vrácení CSV výstupu ve správném kódování UTF-8
        response.write(output.getvalue().encode('utf-8-sig'))

        return response

    def move_transactions_to_book(self, request, transactions):
        """Přesune vybrané transakce do jiné knihy a zajistí vytvoření chybějících tagů a kategorií."""
        new_book_id = request.POST.get('bulk_book')
        if not new_book_id:
            messages.warning(request, "Nevybrali jste cílovou knihu.")
            return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})

        # Kontrola, zda cílová kniha patří uživateli
        new_book = get_object_or_404(Book, id=new_book_id, owner=request.user)

        # Procházíme každou transakci a zpracováváme tagy a kategorie
        for transaction in transactions:
            # Tagy - Zkontrolujeme, zda tagy existují v nové knize, jinak je vytvoříme s kopiemi atributů
            new_tags = []
            for tag in transaction.tags.all():
                # Zkontrolujeme, zda tag již existuje v nové knize
                new_tag, created = Tag.objects.get_or_create(
                    name=tag.name,
                    book=new_book,
                    defaults={'color': tag.color, 'description': tag.description}
                )
                new_tags.append(new_tag)  # Přidáme nový nebo existující tag do seznamu
            """Pokud v nové knize existuje tag se stejným názvem, zachovává se barva a popisek tagu z nové knihy 
            nikoli tagu z knihy původní."""

            # Nastavíme transakci nové tagy z nové knihy
            transaction.tags.set(new_tags)

            # Kategorie - Zkontrolujeme, zda kategorie existuje v nové knize, jinak ji vytvoříme s kopiemi atributů
            if transaction.category:
                new_category, created = Category.objects.get_or_create(
                    name=transaction.category.name,
                    book=new_book,
                    defaults={'color': transaction.category.color, 'description': transaction.category.description}
                )
                transaction.category = new_category  # Aktualizujeme kategorii na tu z nové knihy

            # Případné označení transakce tagem "přesunuto"
            moved_tag, created = Tag.objects.get_or_create(name="Přesunuto", book=new_book)
            transaction.tags.add(moved_tag)

            # Přesun transakce do nové knihy
            transaction.book = new_book
            transaction.save()

        messages.success(request, f"{transactions.count()} vybrané/ých transakce/í byly přesunuty do knihy: {new_book.name}.")
        return JsonResponse({'redirect_url': self.get_redirect_url_with_filters(request)})
