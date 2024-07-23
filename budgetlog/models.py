from django.db import models
from django.utils import timezone
from decimal import Decimal


# Create your models here.
class Category(models.Model):
    """Model pro kategorizaci transakcí."""
    name = models.CharField(max_length=200, unique=True, verbose_name="Název",
                            help_text="Uveď název kategorie pro transakce (např. potraviny, doprava, zábava)")
    description = models.TextField(null=True, blank=True, verbose_name="Popis",
                                   help_text="Detailnější popis kategorie pro transakce (volitelný)")
    """null=True umožňuje, aby pole mohlo být v databázi prázdné, a blank=True umožňuje, aby pole mohlo být ponecháno 
        prázdné ve formulářích."""

    def __str__(self):
        """Textová reprezentace modelu Category."""
        return self.name


class Transaction(models.Model):
    """Model reprezentující záznam o finanční transakci."""
    TYPE_CHOICES = (
        ('income', 'Příjem'),
        ('expense', 'Výdaj')
    )
    PERSON_CHOICES = (
        ('kuba', 'Kuba'),
        ('romca', 'Romča')
    )
    # Definuje tuple pro typ transakce, který voláme níže

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Částka",
                                 help_text="Uveď částku transakce v [CZK].")
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name="Kategorie",
                                 help_text="Vyber kategorii pro tuto transakci.")
    """on_delete=models.SET_NULL nastaví hodnotu na NULL při smazání související kategorie, což zajistí, 
    že transakce nebude smazána."""
    datestamp = models.DateField(default=timezone.now, verbose_name="Datum",
                                 help_text="Datum provedení transakce.")
    description = models.TextField(null=True, blank=True, verbose_name="Popis",
                                   help_text="Detailnější popis transakce (volitelný).")
    person = models.CharField(max_length=10, choices=PERSON_CHOICES, verbose_name="Osoba",
                              help_text="Kdo transakci prováděl?")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='expense', verbose_name="Typ",
                            help_text="Je tato transakce výdaj nebo příjem?")

    def __str__(self):
        """Textová reprezentace modelu pro transakci."""
        type_display = dict(self.TYPE_CHOICES).get(self.type, self.type)
        return f"{type_display}: {self.adjusted_amount} CZK {self.datestamp}"

    @property
    def adjusted_amount(self):
        """Vrátí částku s upraveným znaménkem podle typu transakce (výdaj bude záporný)."""
        if self.type == 'expense':
            return -self.amount
        return self.amount
    """
    Django neumožňuje použít adjusted_amount přímo v anotacích a agregacích, protože adjusted_amount je vlastnost (
    property) modelu a ne skutečné pole v databázi. Pokud chceme filtrovat nebo agregovat ve views podle upravených 
    částek, musíme to udělat pomocí amount a přizpůsobit SQL dotaz.
    """