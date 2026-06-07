"""URLs raíz. Las rutas de cada app se incluyen en su sprint correspondiente."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),  # Fase 2 (AUTH)
    path("api/accounts/", include("apps.accounts.urls")),  # Fase 3 (ACCOUNTS)
    path("api/transactions/", include("apps.transactions.urls")),  # Fase 4 (TRANSACTIONS)
    path("api/categories/", include("apps.transactions.category_urls")),  # Fase 4 (CATEGORIES)
    path("api/currency/", include("apps.currency.urls")),  # Fase 5 (CURRENCY)
    path("api/dashboard/", include("apps.dashboard.urls")),  # Fase 6 (DASHBOARD)
    path("api/shared/", include("apps.shared.urls")),  # Fase 7 (SHARED)
]
