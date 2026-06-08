# ZENITH

**Gestión financiera personal para el contexto argentino.**  
Self-hosteable · Open source · AGPL-3.0

---

## Descripción

Zenith es una aplicación web de finanzas personales diseñada nativamente para Argentina. Soporta múltiples cuentas en ARS y USD, integración con cotizaciones del dólar en tiempo real (dolarapi.com), compras en cuotas, y gestión de gastos compartidos entre dos usuarios.

Desarrollado como proyecto de portfolio aplicando la metodología GZSM v1.1 y Clean Architecture.

---

## Features

- **Cuentas** — efectivo, billetera digital, banco, caja de ahorro en ARS y USD
- **Transacciones** — ingresos, gastos, transferencias entre cuentas propias
- **Cuotas** — compras en N cuotas con monto fijo por cuota
- **Dashboard** — resumen mensual con gráfico de distribución por categoría
- **Tipo de cambio** — cotización en vivo (blue, oficial, tarjeta) vía dolarapi.com con historial
- **Gastos compartidos** — registro de deudas entre dos usuarios con balance neto compensado

---

## Stack

**Backend**
- Python 3.13 · Django 5.2 LTS · Django REST Framework
- django-knox (autenticación por token)
- PostgreSQL 16
- Arquitectura: Clean Architecture estricta (domain → services → serializers → views)

**Frontend**
- React 19 · TypeScript · Vite
- Tailwind CSS con design system AUSTRAL v1.4
- shadcn/ui · TanStack Query · React Router v7 · Axios
- Recharts

**Infraestructura**
- Docker Compose (desarrollo local)
- GitHub Actions (CI: lint → tests → security)
- Railway (backend) · Vercel (frontend)

---

## Setup local

### Requisitos

- Docker Desktop
- Python 3.13
- Node.js 20+

### 1 — Clonar el repositorio

```bash
git clone https://github.com/giuliano-z/Zenith.git
cd Zenith
```

### 2 — Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements/local.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Levantar la base de datos
docker compose up -d db

# Aplicar migraciones
POSTGRES_HOST=localhost POSTGRES_PORT=5433 python manage.py migrate

# Crear usuarios del sistema
POSTGRES_HOST=localhost POSTGRES_PORT=5433 python manage.py shell -c "
from apps.users.models import User
User.objects.create_user(email='usuario1@zenith.app', password='tu_password', name='Usuario 1')
User.objects.create_user(email='usuario2@zenith.app', password='tu_password', name='Usuario 2')
"

# Iniciar servidor
POSTGRES_HOST=localhost POSTGRES_PORT=5433 python manage.py runserver
```

El backend queda disponible en `http://localhost:8000`.

### 3 — Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# VITE_API_URL=http://localhost:8000

# Iniciar servidor de desarrollo
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

---

## API — Endpoints principales

Todos los endpoints requieren autenticación con `Authorization: Token <token>`.

### Auth
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login — devuelve token |
| POST | `/api/auth/logout/` | Logout — invalida token |

### Cuentas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/accounts/` | Listar cuentas con balance real |
| POST | `/api/accounts/` | Crear cuenta |

### Transacciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/transactions/` | Listar con filtros y paginación |
| POST | `/api/transactions/` | Crear ingreso o gasto |
| POST | `/api/transactions/transfer/` | Crear transferencia entre cuentas |
| POST | `/api/transactions/installment/` | Crear compra en cuotas |
| GET | `/api/categories/` | Listar categorías disponibles |

### Dashboard
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/?year=2026&month=6` | Resumen mensual del período |

### Tipo de cambio
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/currency/fetch/` | Cotización en vivo (no guarda) |
| GET | `/api/currency/rates/` | Historial de tasas guardadas |
| POST | `/api/currency/rates/` | Guardar tasa |
| GET | `/api/currency/rates/latest/` | Última tasa vigente |

### Gastos compartidos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/shared/expenses/` | Historial de gastos compartidos |
| POST | `/api/shared/expenses/` | Registrar gasto compartido |
| GET | `/api/shared/balance/` | Balance neto entre usuarios |
| POST | `/api/shared/balance/settle/` | Saldar balance |

---

## Arquitectura

Zenith sigue Clean Architecture estricta. Las dependencias fluyen de afuera hacia adentro: views → serializers → services → domain. El dominio no importa nada de Django ni de infraestructura.

```
backend/apps/<módulo>/
├── models.py           # Capa de datos
├── services.py         # Lógica de negocio (funciones de módulo, sin clases)
├── serializers.py      # Capa de presentación
├── views.py            # Endpoints REST
└── tests/
    ├── test_services.py
    └── test_views.py
```

Módulos con complejidad de agregación cross-módulo usan subpaquete `domain/`:

```
apps/currency/domain/
├── interfaces.py       # ExchangeRateProviderInterface (ABC)
└── services.py         # get_latest_rate, get_rate_for_date

apps/dashboard/domain/
└── services.py         # Agregación pura sin modelo propio
```

Las decisiones arquitectónicas relevantes están documentadas en `docs/F2_adr/`.

---

## Tests

```bash
cd backend
POSTGRES_HOST=localhost POSTGRES_PORT=5433 pytest
```

126 tests · cobertura ≥ 80% en capa de dominio y servicios.

```bash
cd frontend
npm run build   # tsc + vite build
npm run lint    # eslint
```

---

## CI/CD

GitHub Actions ejecuta en cada push y PR:

1. **lint** — ruff
2. **security** — bandit
3. **test** — pytest con PostgreSQL efímero

El deploy a Railway y Vercel se activa manualmente desde la rama `main`.

---

## Design System

Zenith usa **AUSTRAL v1.4**, un design system dark-space con identidad argentina.

- Paleta: cosmos/nebula/orbit como fondos, celeste como acento principal
- Tipografía: Sora (display) · Plus Jakarta Sans (body) · IBM Plex Mono (números)
- Motivos: sol de mayo, franja argentina, estela de lanzamiento

El spec completo está en `CLAUDE.austral.md`.

---

## Licencia

[AGPL-3.0](LICENSE) — Giuliano Zulatto, 2026.

---

*Desarrollado con la metodología GZSM v1.1 · Ingeniería en Software — Universidad Siglo 21*
