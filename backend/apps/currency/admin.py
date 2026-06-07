"""Admin del módulo CURRENCY: lectura/auditoría del historial de cotizaciones."""
from django.contrib import admin

from apps.currency.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("rate_type", "rate", "effective_date", "source", "created_by", "created_at")
    list_filter = ("rate_type", "source", "effective_date")
    search_fields = ("rate_type",)
    date_hierarchy = "effective_date"
    readonly_fields = ("created_at",)
