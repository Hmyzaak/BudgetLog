from django.apps import AppConfig


class BudgetlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgetlog'

    def ready(self):
        import budgetlog.signals  # Registrace signálů
