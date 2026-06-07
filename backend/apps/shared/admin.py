"""Admin del módulo SHARED: auditoría de gastos compartidos y saldos."""
from django.contrib import admin

from apps.shared.models import SharedExpense, SharedSettlement


@admin.register(SharedExpense)
class SharedExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "total_amount",
        "currency",
        "payer",
        "debtor",
        "debtor_amount",
        "is_settled",
        "date",
    )
    list_filter = ("is_settled", "currency", "date")
    search_fields = ("description",)
    date_hierarchy = "date"
    readonly_fields = ("created_at",)


@admin.register(SharedSettlement)
class SharedSettlementAdmin(admin.ModelAdmin):
    list_display = ("net_amount", "creditor", "debtor", "settled_by", "settled_at")
    list_filter = ("settled_at",)
    readonly_fields = ("settled_at",)
