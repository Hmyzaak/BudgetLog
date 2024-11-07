from django import template

register = template.Library()

# Mapování anglických názvů měsíců na české názvy měsíců v prvním pádě
MONTHS_CS = {
    1: 'Leden', 2: 'Únor', 3: 'Březen', 4: 'Duben', 5: 'Květen', 6: 'Červen',
    7: 'Červenec', 8: 'Srpen', 9: 'Září', 10: 'Říjen', 11: 'Listopad', 12: 'Prosinec'
}


@register.filter(name='format_month_cs')
def format_month_cs(month):
    """Vrací název měsíce v češtině nebo prázdný řetězec, pokud měsíc není validní."""
    return MONTHS_CS.get(month, '') if isinstance(month, int) and 1 <= month <= 12 else ''


@register.filter
def instanceof(obj, class_obj):
    """Vrátí True, pokud je objekt instance dané třídy nebo jejích podtříd."""
    return isinstance(obj, class_obj)
