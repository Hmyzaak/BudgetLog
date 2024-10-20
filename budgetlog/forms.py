from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import *
from budgetlog.templatetags.widgets import ColoredTagWidget


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
        widgets = {'datestamp': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 1})
                   }
        # Upravuje vzhled polí ve formuláři. DateInput s type='date' umožňuje vybrat datum pomocí kalendáře.
        help_texts = {'datestamp': "Zadejte datum provedení, příp. započtení, transakce."}
        # Upravuje pomocný text pro pole datestamp

    def __init__(self, *args, **kwargs):
        # Přidání pop argumentu 'book'
        self.book = kwargs.pop('book', None)  # Získání knihy z kwargs
        super().__init__(*args, **kwargs)  # Volání parent konstruktoru

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


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = ['email']  # Zobrazujeme jen email, hesla jsou již obsažena v UserCreationForm
        labels = {
            'email': 'E-mail',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nastavení textů políček pro heslo
        self.fields['password1'].label = "Nové heslo"
        self.fields['password1'].help_text = (
            "<ul>"
            "<li>Heslo musí obsahovat alespoň 8 znaků.</li>"
            "<li>Heslo nesmí obsahovat pouze číslice.</li>"
            "<li>Heslo nesmí být příliš jednoduché.</li>"
            "<li> Heslo nesmí být příliš podobné ostatním osobním informacím.</li>"
            "</ul>"
        )
        self.fields['password2'].label = "Nové heslo pro potvrzení"
        self.fields['password2'].help_text = "Zadejte nové heslo pro potvrzení."

    # Přidáme vlastní validaci hesla
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Zadaná hesla se neshodují.")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ["email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nastavení textů políček pro email a heslo
        self.fields['email'].label = "E-mail"
        self.fields['password'].label = "Heslo"


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulář pro změnu hesla s přizpůsobenými českými texty."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Přizpůsobení českých textů v polích
        self.fields['old_password'].label = "Staré heslo"
        self.fields['new_password1'].label = "Nové heslo"
        self.fields['new_password1'].help_text = (
            "<ul>"
            "<li>Heslo musí obsahovat alespoň 8 znaků.</li>"
            "<li>Heslo nesmí obsahovat pouze číslice.</li>"
            "<li>Heslo nesmí být příliš jednoduché.</li>"
            "<li> Heslo nesmí být příliš podobné ostatním osobním informacím.</li>"
            "</ul>"
        )
        self.fields['new_password2'].label = "Nové heslo pro potvrzení"
        self.fields['new_password2'].help_text = "Zadejte nové heslo pro potvrzení."
