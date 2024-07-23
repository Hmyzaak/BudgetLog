from django.shortcuts import redirect


def index_handler(request):
    return redirect("transaction-list")
# Přesměrování z localhost:8000/ na localhost:8000/transactions/
