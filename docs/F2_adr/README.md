# F2 — Arquitectura: Zenith

**Versión:** 1.0 · Mayo 2026  
**Autor:** Giuliano Zulatto  
**Metodología:** GZSM v1.1  
**Estado:** F2 cerrado — Listo para F3·Construcción  

---

## Índice de ADRs

| ADR | Decisión | Estado |
|---|---|---|
| [ADR-001](ADR-001-stack-backend.md) | Stack backend: Django 5.x + DRF | Aceptado |
| [ADR-002](ADR-002-autenticacion.md) | Autenticación: tokens opacos con django-knox | Aceptado |
| [ADR-003](ADR-003-arquitectura-capas.md) | Arquitectura de capas y estructura de directorios | Aceptado |
| [ADR-004](ADR-004-modelo-balance.md) | Modelo de balance: cálculo en tiempo real con índice compuesto | Aceptado |
| [ADR-005](ADR-005-deploy-frontend.md) | Deploy frontend: Vercel | Aceptado |

---

## Stack definitivo

| Componente | Tecnología | Justificación |
|---|---|---|
| **Backend** | Python 3.13 + Django 5.x + DRF | ADR-001 |
| **Autenticación** | django-knox (tokens opacos en DB) | ADR-002 |
| **Base de datos** | PostgreSQL 16 | SRS §6.1 |
| **Frontend** | React + TypeScript + Vite | SRS §6.1 |
| **Deploy backend** | Railway | SRS §6.1 + RNF-010 |
| **Deploy frontend** | Vercel | ADR-005 |
| **Containerización** | Docker + docker-compose | RNF-008 |
| **CI/CD** | GitHub Actions | GZSM §F3.3 |
| **Testing backend** | pytest-django + coverage.py | RNF-006 |
| **Linting backend** | ruff | RNF-007 |
| **Seguridad** | bandit + pip-audit | RS-001, RS-005 |
| **CORS** | django-cors-headers | ADR-005 |
| **Filtros API** | django-filter | ADR-003 |

---

## Diagrama de componentes (C4 Nivel 2)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ZENITH — Sistema                              │
│                                                                        │
│  ┌─────────────────────┐          ┌──────────────────────────────┐   │
│  │    FRONTEND (SPA)   │          │       BACKEND (API REST)      │   │
│  │  React + TypeScript  │          │    Django 5.x + DRF          │   │
│  │  Vercel (CDN)        │          │    Railway                    │   │
│  │                      │          │                               │   │
│  │  ┌─────────────┐    │  HTTPS   │  ┌─────────────────────────┐ │   │
│  │  │ pages/      │    │  REST    │  │  config/                │ │   │
│  │  │ components/ │◄───┼──────────┼──│  urls.py + settings/    │ │   │
│  │  │ hooks/      │    │  JSON    │  └──────────┬──────────────┘ │   │
│  │  │ api/        │    │          │             │                 │   │
│  │  └─────────────┘    │          │  ┌──────────▼──────────────┐ │   │
│  └─────────────────────┘          │  │  apps/                  │ │   │
│                                    │  │  ├── users/             │ │   │
│                                    │  │  ├── accounts/          │ │   │
│                                    │  │  ├── transactions/      │ │   │
│                                    │  │  ├── categories/        │ │   │
│                                    │  │  ├── currency/          │ │   │
│                                    │  │  ├── dashboard/         │ │   │
│                                    │  │  └── common/            │ │   │
│                                    │  └──────────┬──────────────┘ │   │
│                                    │             │                 │   │
│                                    │  ┌──────────▼──────────────┐ │   │
│                                    │  │  Knox Token Store        │ │   │
│                                    │  │  (tokens hasheados en DB)│ │   │
│                                    │  └──────────┬──────────────┘ │   │
│                                    └─────────────┼────────────────┘   │
│                                                  │                     │
│                                    ┌─────────────▼──────────┐         │
│                                    │   PostgreSQL 16          │         │
│                                    │   Railway / Docker       │         │
│                                    │                          │         │
│                                    │  Tables:                 │         │
│                                    │  • users_user            │         │
│                                    │  • knox_authtoken        │         │
│                                    │  • accounts_account      │         │
│                                    │  • transactions_tx       │         │
│                                    │  • transactions_install. │         │
│                                    │  • categories_category   │         │
│                                    │  • currency_exchangerate │         │
│                                    │  • shared_sharedexpense  │         │
│                                    └──────────────────────────┘         │
└──────────────────────────────────────────────────────────────────────┘

DEPLOY LOCAL (desarrollo):
  docker-compose up → PostgreSQL + Django backend en localhost:8000
  npm run dev       → React frontend en localhost:5173

DEPLOY PRODUCCIÓN:
  Railway           → Django backend (auto-deploy desde GitHub main)
  Vercel            → React frontend (auto-deploy desde GitHub main)
  Railway           → PostgreSQL (servicio gestionado)
```

---

## Flujo de autenticación (ADR-002)

```
Cliente (React)          Backend (Django + Knox)        PostgreSQL
     │                          │                            │
     │── POST /api/auth/login ──►│                            │
     │   {email, password}       │── SELECT user WHERE ──────►│
     │                           │   email=? (hash check)     │
     │                           │◄── user found ─────────────│
     │                           │── INSERT knox_authtoken ──►│
     │◄── {token: "abc123..."} ──│◄── OK ─────────────────────│
     │                           │                            │
     │── GET /api/accounts/ ─────►│                            │
     │   Authorization: Token abc│── SELECT authtoken ────────►│
     │                           │   WHERE token_hash=hash()  │
     │                           │◄── token valid, user=G ────│
     │◄── [{account data}] ──────│                            │
     │                           │                            │
     │── POST /api/auth/logout ──►│                            │
     │   Authorization: Token abc│── DELETE authtoken ─────────►│
     │◄── 200 OK ────────────────│◄── OK ─────────────────────│
     │                           │                            │
     │── GET /api/accounts/ ─────►│                            │
     │   Authorization: Token abc│── SELECT authtoken ────────►│
     │                           │◄── 0 rows (token deleted) ─│
     │◄── 401 Unauthorized ──────│                            │
```

---

## Verificación criterio de salida F2 (GZSM §F2.5)

| Criterio | Estado |
|---|---|
| ☑ Cada decisión técnica significativa tiene un ADR escrito. | ADR-001 a ADR-005 |
| ☑ El stack está justificado contra los RNF de F1, no por preferencia. | ADR-001: tabla Django vs FastAPI vs RNF. ADR-004: cálculo de balance vs RNF-001. |
| ☑ La arquitectura de capas está definida. El dominio no importa nada de la infraestructura. | ADR-003: tabla de dependencias permitidas por capa. |
| ☑ Los diagramas de componentes reflejan los módulos principales y sus dependencias. | Diagrama C4 Nivel 2 en este documento. |
| ☑ Sabés qué tecnologías podés cambiar en el futuro sin tocar la lógica de negocio. | DB: el ORM abstrae la DB (PostgreSQL reemplazable). Auth: Knox reemplazable por JWT en F4. Frontend: Vercel reemplazable por Netlify/Railway sin cambios de código. |

**Estado: F2 CERRADO — Listo para iniciar F3·Construcción.**

---

## Deuda técnica registrada (para F4)

| Item | Descripción | Condición de revisión |
|---|---|---|
| DT-001 | Balance materializado | Si el dataset supera 50.000 transacciones o el P95 supera 400ms en métricas GQM de F4. |
| DT-002 | JWT con refresh tokens | Si el sistema escala a múltiples instancias de backend o usuarios externos. |
| DT-003 | Admin de Django sin configurar | Se habilita solo si se necesita panel administrativo en versiones futuras. |

---

*Próximo paso: PT-04 → F3·Construcción — Sprint 1: AUTH + ACCOUNTS + TRANSACTIONS (RF Must Have).*

*GZSM v1.1 · Giuliano Zulatto · Ingeniería en Software — Universidad Siglo 21*
