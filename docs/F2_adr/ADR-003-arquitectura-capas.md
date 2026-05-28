# ADR-003: Arquitectura de Capas y Estructura de Directorios

**Estado:** Aceptado  
**Fecha:** Mayo 2026  
**Autor:** Giuliano Zulatto  
**Proyecto:** Zenith  

---

## Contexto

El SRS define 6 módulos funcionales: AUTH, ACCOUNTS, TRANSACTIONS, CATEGORIES, CURRENCY, DASHBOARD, SHARED.
La GZSM §F2.1 exige Clean Architecture: las dependencias apuntan hacia adentro (dominio), la DB y la API son plugins.
El SRS §6.1 menciona React + TypeScript para el frontend, desacoplado del backend.

Restricciones adicionales:
- RNF-007: ningún módulo supera 400 líneas; ninguna función supera 50 líneas.
- RNF-006: cobertura >= 80% en capa de dominio (la lógica de negocio debe ser testeable en aislamiento).
- Desarrollador único: la estructura debe ser comprensible y mantenible sin documentación adicional.

---

## Decisión

**Se adopta Clean Architecture con adaptación pragmática para Django: tres capas explícitas (domain, application, infrastructure/presentation) dentro de la estructura de apps de Django.**

La estructura no usa la organización de directorios estándar de Django (`project/app/models.py`) como capa única. En cambio, cada módulo de dominio se organiza internamente con separación de responsabilidades.

---

## Estructura de directorios

```
zenith/
├── backend/
│   ├── config/                        # Configuración Django (settings, urls raíz, wsgi)
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── apps/                          # Módulos de dominio (apps Django)
│   │   ├── users/                     # Módulo AUTH
│   │   │   ├── models.py              # Entidad User (extiende AbstractBaseUser)
│   │   │   ├── serializers.py         # Contratos de API (entrada/salida)
│   │   │   ├── views.py               # Endpoints (< 50 líneas por vista)
│   │   │   ├── urls.py
│   │   │   ├── services.py            # Lógica de negocio (crear usuario, cambiar pass)
│   │   │   ├── permissions.py         # IsOwner, IsParticipantOfSharedExpense
│   │   │   └── tests/
│   │   │       ├── test_models.py
│   │   │       ├── test_services.py   # Unit tests (sin DB)
│   │   │       └── test_views.py      # Integration tests (APIClient)
│   │   │
│   │   ├── accounts/                  # Módulo ACCOUNTS
│   │   │   ├── models.py              # Account
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py            # get_balance(), archive_account()
│   │   │   └── tests/
│   │   │
│   │   ├── transactions/              # Módulo TRANSACTIONS
│   │   │   ├── models.py              # Transaction, Installment, SharedExpense
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py            # register_transaction(), register_installment()
│   │   │   ├── filters.py             # django-filter: cuenta, categoría, fecha, moneda
│   │   │   └── tests/
│   │   │
│   │   ├── categories/                # Módulo CATEGORIES
│   │   │   ├── models.py              # Category (is_default flag)
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── currency/                  # Módulo CURRENCY
│   │   │   ├── models.py              # ExchangeRate (valor, fecha_vigencia)
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py            # get_rate_for_date(), convert_amount()
│   │   │   └── tests/
│   │   │
│   │   └── dashboard/                 # Módulo DASHBOARD (sin modelos propios)
│   │       ├── serializers.py         # Respuesta del dashboard (output only)
│   │       ├── views.py               # DashboardView (agrega datos de otros módulos)
│   │       ├── urls.py
│   │       ├── services.py            # monthly_summary(), category_breakdown()
│   │       └── tests/
│   │
│   ├── common/                        # Utilidades transversales
│   │   ├── permissions.py             # IsOwnerOrReadOnly, IsParticipantOfSharedExpense
│   │   ├── exceptions.py              # Custom exceptions handler
│   │   ├── pagination.py              # StandardPagination (page_size=20)
│   │   └── utils.py                   # Helpers sin dependencia de Django
│   │
│   ├── manage.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   └── pytest.ini
│
├── frontend/                          # SPA React + TypeScript (repositorio o carpeta)
│   ├── src/
│   │   ├── api/                       # Llamadas a la API REST (axios/fetch)
│   │   ├── components/                # Componentes reutilizables
│   │   ├── pages/                     # Páginas (Dashboard, Accounts, Transactions...)
│   │   ├── hooks/                     # Custom hooks (useAuth, useTransactions...)
│   │   ├── types/                     # TypeScript types/interfaces
│   │   └── utils/
│   └── package.json
│
├── docker-compose.yml                 # Backend + PostgreSQL + (opcional) frontend
├── docker-compose.prod.yml            # Configuración de producción (Railway)
├── .env.example
├── docs/
│   ├── F1_srs.md
│   └── F2_adr/
│       ├── ADR-001-stack-backend.md
│       ├── ADR-002-autenticacion.md
│       ├── ADR-003-arquitectura-capas.md
│       ├── ADR-004-modelo-balance.md
│       └── ADR-005-deploy-frontend.md
└── README.md
```

---

## Separación de responsabilidades por capa

| Capa | Archivos | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| **Dominio** | `models.py`, `services.py` | Entidades y lógica de negocio | Solo Python stdlib + Django ORM abstracto |
| **Aplicación** | `serializers.py`, `permissions.py` | Contratos de entrada/salida, autorización | Dominio |
| **Presentación** | `views.py`, `urls.py`, `filters.py` | HTTP: routing, request/response | Aplicación |
| **Infraestructura** | `config/settings/`, `docker-compose.yml` | DB, env vars, deploy | Todo (capa más externa) |

### Reglas de dependencia (Regla de Dependencia — GZSM §F2.1)

- `services.py` nunca importa desde `views.py` ni `serializers.py`.
- `models.py` nunca importa desde ningún módulo de otra app excepto `common/`.
- `dashboard/services.py` puede importar servicios de otros módulos (es la única excepción justificada: el dashboard agrega datos de todos los módulos).
- Los tests unitarios (`test_services.py`) prueban servicios sin instanciar el servidor HTTP.

---

## Alternativa evaluada y descartada

**Opción descartada: estructura flat estándar de Django** (`models.py` monolítico, toda la lógica en views o en managers de ORM).

Por qué se descarta: con 6 módulos y lógica de negocio no trivial (cálculo de balances con cuotas, conversión histórica de TC, compensación de deudas compartidas), una estructura flat produce archivos de 500+ líneas y lógica de dominio mezclada con lógica HTTP. Testear servicios requeriría instanciar el servidor completo. Viola RNF-007 y dificulta cumplir RNF-006.

---

## Consecuencias positivas

- Cada `services.py` contiene funciones puras o casi-puras testeables sin request HTTP → RNF-006 alcanzable.
- La estructura de directorios revela el dominio (finanzas personales), no el framework ("Screaming Architecture").
- Ningún archivo debería superar 400 líneas si las responsabilidades están correctamente separadas.
- El módulo `dashboard/` no tiene modelos propios: es explícitamente una capa de agregación, no de almacenamiento.

## Consecuencias negativas (deuda técnica aceptada)

- Más archivos por módulo que una app Django estándar. El overhead de navegación es bajo dado el tamaño del proyecto (un desarrollador, IDE con search).
- La separación entre `services.py` y `views.py` requiere disciplina en code review (auto-review en este caso). El criterio es claro: si una función toma un `Request` como parámetro, pertenece a `views.py`, no a `services.py`.

---

## RNF impactados

| RNF | Cómo esta decisión lo satisface |
|---|---|
| RNF-006 (cobertura >= 80% dominio) | `services.py` es testeable en aislamiento. Los unit tests no necesitan HTTP stack. |
| RNF-007 (límites de LOC) | La separación forzada evita que cualquier archivo crezca más allá de su responsabilidad. |
| RNF-005 (aislamiento de datos) | `permissions.py` centraliza la lógica de autorización. No se repite en cada vista. |
