"""URLs raíz. Las rutas de cada app se incluyen en su sprint correspondiente."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),  # Fase 2 (AUTH)
    path("api/accounts/", include("apps.accounts.urls")),  # Fase 3 (ACCOUNTS)
]
