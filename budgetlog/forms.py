# Django importy
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

# Lokální aplikace
from budgetlog.models import Transaction, Category, Tag, AppUser


class ColoredTagWidget(CheckboxSelectMultiple):
    """Vlastní widget pro výběr tagů s barvami, kde jsou tagy zobrazeny vedle sebe."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        self.tag_colors = {tag.pk: tag.color for tag in Tag.objects.all()}  # Načtení všech tagů s barvou

        # Načtení barvy tagu dynamicky podle ID
        try:
            tag_color = self.tag_colors.get(value, "#000000")
        except Tag.DoesNotExist:
            tag_color = "#000000"  # Defaultní barva, pokud tag není nalezen

        # Přidání stylu a labelu s barvou
        option['attrs']['style'] = 'flex: 1 1 auto; margin: 5px;'
        option['label'] = mark_safe(
            f'<span style="background-color: {tag_color}; color: white; padding: 2px 5px; '
            f'border-radius: 5px; display: inline-block;">{label}</span>'
        )
        return option


class TransactionForm(forms.ModelForm):
    """Formulář pro přidání a úpravu transakcí."""

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=ColoredTagWidget,
        required=False,
        label="Tagy"
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'category', 'datestamp', 'description', 'tags']
        widgets = {'datestamp': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                   'description': forms.Textarea(attrs={'rows': 1})
                   }
        # Upravuje vzhled polí ve formuláři. DateInput s type='date' umožňuje vybrat datum pomocí kalendáře.
        help_texts = {'datestamp': "Zadejte datum provedení, příp. započtení, transakce."}
        # Upravuje pomocný text pro pole datestamp

    def __init__(self, *args, **kwargs):
        self.book = kwargs.pop('book', None)  # Získání knihy z kwargs
        super().__init__(*args, **kwargs)

        # Aktualizace querysetů pro category a account pouze pro aktuální knihu
        if self.book:
            self.fields['category'].queryset = Category.objects.filter(book=self.book)
            self.fields['tags'].queryset = Tag.objects.filter(book=self.book)
        else:
            self.fields['category'].queryset = Category.objects.none()
            self.fields['tags'].queryset = Tag.objects.none()


class TransactionFilterForm(forms.Form):
    """Formulář pro filtrování transakcí (ne editaci)."""

    amount_min = forms.DecimalField(required=False, label='Částka (min)',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    amount_max = forms.DecimalField(required=False, label='Částka (max)',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    datestamp__gte = forms.DateField(required=False, label='Datum (od)',
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    datestamp__lte = forms.DateField(required=False, label='Datum (do)',
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Transaction
        fields = ['amount_min', 'amount_max', 'type', 'datestamp__gte', 'datestamp__lte', 'category', 'tags', 'description']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': ColoredTagWidget(attrs={'class': 'form-check-input'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    """Formulář pro přidání a úpravu kategorií transakcí."""

    class Meta:
        model = Category
        fields = ['name', 'color', 'description']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 1})
        }


class TagForm(forms.ModelForm):
    """Formulář pro přidání a úpravu tagů pro transakce."""

    class Meta:
        model = Tag
        fields = ['name', 'color', 'description']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 1})
        }


# Společná třída pro české texty heslových polí
class PasswordFieldTextsMixin:
    @staticmethod
    def get_password_help_text():
        return (
            "<ul>"
            "<li>Heslo musí obsahovat alespoň 8 znaků.</li>"
            "<li>Heslo nesmí obsahovat pouze číslice.</li>"
            "<li>Heslo nesmí být příliš jednoduché.</li>"
            "<li>Heslo nesmí být příliš podobné ostatním osobním informacím.</li>"
            "</ul>"
        )


class UserRegistrationForm(PasswordFieldTextsMixin, UserCreationForm):
    """Formulář pro registraci uživatele s vlastní validací hesla."""

    email = forms.EmailField(label="E-mail", error_messages={
        'invalid': gettext_lazy("Zadejte platnou e-mailovou adresu.")  # Překlad chybové hlášky do češtiny
    })

    class Meta:
        model = AppUser
        fields = ['email']  # Zobrazujeme jen email, hesla jsou již obsažena v UserCreationForm
        labels = {'email': 'E-mail'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nastavení textů políček pro heslo
        self.fields['password1'].label = "Nové heslo"
        self.fields['password1'].help_text = self.get_password_help_text()
        self.fields['password2'].label = "Nové heslo pro potvrzení"
        self.fields['password2'].help_text = "Zadejte nové heslo pro potvrzení."

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Zadaná hesla se neshodují.")
        return password2


class LoginForm(forms.Form):
    email = forms.CharField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Heslo")


class CustomPasswordChangeForm(PasswordFieldTextsMixin, PasswordChangeForm):
    """Formulář pro změnu hesla s přizpůsobenými českými texty."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "Staré heslo"
        self.fields['new_password1'].label = "Nové heslo"
        self.fields['new_password1'].help_text = self.get_password_help_text()
        self.fields['new_password2'].label = "Nové heslo pro potvrzení"
        self.fields['new_password2'].help_text = "Zadejte nové heslo pro potvrzení."


class CustomPasswordResetForm(PasswordFieldTextsMixin, SetPasswordForm):
    """Formulář pro reset hesla s přizpůsobenými českými texty."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].label = "Nové heslo"
        self.fields['new_password1'].help_text = self.get_password_help_text()
        self.fields['new_password2'].label = "Nové heslo pro potvrzení"
        self.fields['new_password2'].help_text = "Zadejte nové heslo pro potvrzení."
