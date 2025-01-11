"""
WSGI config for budgetlog_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Přidej cestu ke svému projektu
path = '/home/budgetlog/BudgetLog'
if path not in sys.path:
    sys.path.append(path)

# Nastav virtuální prostředí
os.environ['VIRTUAL_ENV'] = '/home/budgetlog/BudgetLog/venv'
sys.prefix = os.environ['VIRTUAL_ENV']

# Nastav Django settings modul
os.environ['DJANGO_SETTINGS_MODULE'] = 'budgetlog_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()