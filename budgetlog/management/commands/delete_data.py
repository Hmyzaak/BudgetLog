from budgetlog.models import Category, Transaction

# Smažte všechny transakce
Transaction.objects.all().delete()

# Smažte všechny kategorie
Category.objects.all().delete()
