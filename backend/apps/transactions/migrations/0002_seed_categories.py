"""Data migration: categorías del sistema (RF-014).

Siembra las categorías default (is_default=True, user=None) comunes a todos los
usuarios. No es un fixture: es RunPython para que el estado quede versionado y sea
reversible. La reversa borra exactamente lo sembrado (default del sistema), sin tocar
categorías que un usuario haya creado.
"""
from django.db import migrations

INCOME_CATEGORIES = [
    "Sueldo",
    "Freelance",
    "Alquiler cobrado",
    "Transferencia recibida",
    "Otros ingresos",
]

EXPENSE_CATEGORIES = [
    "Alimentación",
    "Transporte",
    "Vivienda",
    "Salud",
    "Educación",
    "Entretenimiento",
    "Ropa y calzado",
    "Servicios",
    "Suscripciones",
    "Salidas y restaurantes",
    "Otros gastos",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    for name in INCOME_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            user=None,
            defaults={"category_type": "income", "is_default": True},
        )
    for name in EXPENSE_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            user=None,
            defaults={"category_type": "expense", "is_default": True},
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    Category.objects.filter(
        user=None,
        is_default=True,
        name__in=INCOME_CATEGORIES + EXPENSE_CATEGORIES,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
