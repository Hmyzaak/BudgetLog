from django.shortcuts import redirect


def index_handler(request):
    return redirect("dashboard")
# Přesměrování z localhost:8000/ na localhost:8000/dashboard/
