"""URLs raíz. Las rutas de cada app se incluyen en su sprint correspondiente."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),  # Fase 2 (AUTH)
    path("api/accounts/", include("apps.accounts.urls")),  # Fase 3 (ACCOUNTS)
    path("api/transactions/", include("apps.transactions.urls")),  # Fase 4 (TRANSACTIONS)
    path("api/currency/", include("apps.currency.urls")),  # Fase 5 (CURRENCY)
]
