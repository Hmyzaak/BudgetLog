from django import template

register = template.Library()


@register.filter
def get_month_total(category, month):
    try:
        return getattr(category, f'month_{month}', 0)
    except AttributeError:
        return 0

