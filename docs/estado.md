---
proyecto: Zenith
tipo: personal-finance-app
estado: activo
fase: MVP-funcional → pulido-y-deploy
ultimo_update: 2026-06-10
stack: Django · DRF · Knox · PostgreSQL · Docker · Railway · React · Vite · TypeScript
---

## Descripción
App de finanzas personales multi-cuenta, multi-moneda (ARS/USD).
Arquitectura orientada a escalar como SaaS multi-tenant. AGPL-3.0.

## Stack técnico
- **Backend:** Django + DRF + Knox (auth) + Argon2 + PostgreSQL
- **Infra:** Docker Compose · Railway (backend live) · Gunicorn + Whitenoise
- **Frontend:** React + TypeScript + Vite + AUSTRAL design system
- **Testing:** pytest-django

## Estado actual
- ✅ 7 apps backend implementadas y funcionales
- ✅ **126/126 tests passing** (3.85s) — confirmado 2026-06-10
- ✅ Backend deployado en Railway
- ✅ Frontend **funcional end-to-end** con datos reales (no mock)
- ✅ AUSTRAL aplicado: dark theme, celeste accent, sidebar
- ✅ Secciones operativas: Dashboard · Cuentas · Transacciones · Tipo de cambio · Gastos compartidos
- ⚠️  Fix pendiente: `amount` min_value en Transaction serializer
- ⚠️  Dashboard: warning "Sin tipo de cambio configurado" cuando no hay TC cargado

## Próximo paso inmediato
Auditar qué necesita pulido en el frontend antes de deploy: UX, edge cases, validaciones visibles.

## Backlog (priorizado)
1. [ ] Fix serializer: `amount` → `min_value=Decimal('0.01')`
2. [ ] Auditar frontend sección por sección: UX, manejo de errores, estados vacíos
3. [ ] Resolver flujo completo Tipo de Cambio (warning en dashboard)
4. [ ] Deploy frontend en Railway
5. [ ] Pulir AUSTRAL: consistencia visual cross-secciones
6. [ ] Documentar API (Swagger / Redoc)

## Decisiones clave (no revertir)
- Auth: Knox tokens + Argon2 — no JWT, no bcrypt
- Ownership: 403-nunca-404 para recursos propios del usuario
- Monetario: siempre `Decimal`, nunca `FloatField`
- Código en español es-AR: modelos, variables, comentarios
- Capa de dominio en `services.py` — lógica fuera de views y serializers

## Fixes pendientes
| Archivo | Fix |
|---|---|
| `apps/transactions/serializers.py` | `amount`: `min_value=0` → `min_value=Decimal('0.01')` |

## Restricciones críticas
- Sin FloatField para valores monetarios
- Sin push a main sin 126 tests verdes

## Blockers
Ninguno.

## Links
- Repo: github.com/[user]/zenith
- Deploy backend: Railway (live)
- Frontend dev: localhost:5173 (Vite)
- Diseño: AUSTRAL v1.4 Final
