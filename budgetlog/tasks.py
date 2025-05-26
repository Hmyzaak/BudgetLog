from budgetlog.models import RecurringTransaction, Transaction
from django.utils.timezone import now


def generate_transactions_from_recurring():
    today = now().date()

    recurring = RecurringTransaction.objects.filter(
        is_active=True,
        start_date__lte=today
    ).filter(
        end_date__isnull=True
    ) | RecurringTransaction.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    )

    for rt in recurring:
        if rt.should_generate_on(today):
            # Ověříme, zda již dnes nebyla transakce vygenerována
            already_exists = Transaction.objects.filter(
                datestamp=today
            ).exists()

            if not already_exists:
                transaction = Transaction.objects.create(
                    book=rt.book,
                    amount=rt.amount,
                    category=rt.category,
                    datestamp=today,
                    description=f'Automaticky vygenerováno z opakované transakce #{rt.name}:\n{rt.description}',
                    type=rt.type,
                )
                transaction.tags.set(rt.tags.all())

"""
import time

def print_hello(name):
    print(f"Zdravím, {name}! Task běží.")
    time.sleep(5)
    print(f"Task {name} dokončen.")
    return f"Ahoj, {name}"
"""