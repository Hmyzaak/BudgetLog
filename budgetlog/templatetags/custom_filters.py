from django import template
from django.db.models import Sum, F, DecimalField, Case, When
from django.db.models.functions import Coalesce
from decimal import Decimal

register = template.Library()

# Mapování anglických názvů měsíců na české názvy měsíců v prvním pádě
MONTHS_CS = {
    1: 'Leden', 2: 'Únor', 3: 'Březen', 4: 'Duben', 5: 'Květen', 6: 'Červen',
    7: 'Červenec', 8: 'Srpen', 9: 'Září', 10: 'Říjen', 11: 'Listopad', 12: 'Prosinec'
}


@register.filter(name='format_month_cs')
def format_month_cs(month):
    return MONTHS_CS.get(month, '')


@register.filter
def get_month_total(category, month_index):
    """Vrátí celkový součet transakcí za daný měsíc pro konkrétní kategorii."""
    # Předpokládáme, že month_index je 0-based (0 pro leden, 1 pro únor, ...)
    month = month_index + 1  # Django používá 1-based index měsíců

    # Výpočet celkového součtu transakcí pro kategorii v daném měsíci
    total = category.transactions.filter(
        datestamp__month=month
    ).aggregate(
        total=Coalesce(
            Sum(
                Case(
                    When(type='expense', then=-F('amount')),
                    default=F('amount'),
                    output_field=DecimalField()
                )
            ),
            Decimal('0')
        )
    )['total']

    return total
