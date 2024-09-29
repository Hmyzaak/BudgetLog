from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe

from budgetlog.models import *


class ColoredTagWidget(CheckboxSelectMultiple):
    """Vlastní widget pro výběr tagů, kde se tagy zobrazují vedle sebe a mají vlastní barvu."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Načteme instanci tagu a přidáme barvu
        if hasattr(value, 'value'):
            value = value.value
        tag = Tag.objects.get(pk=value)

        # Vytvoříme obalovací styl pro celý tag (checkbox + label)
        option['attrs']['style'] = f'display: inline-block; margin-right: 10px;'

        # Stylujeme samotný label
        option['label'] = mark_safe(f'<span style="background-color: {tag.color}; color: white; padding: 2px 5px; '
                                    f'border-radius: 5px; display: inline-block;">{label}</span>')

        return option
