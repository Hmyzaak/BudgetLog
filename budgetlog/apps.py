from django.apps import AppConfig


class BudgetlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgetlog'

    def ready(self):
        # Import signálů pro registraci při spuštění aplikace
        import budgetlog.signals
