# ADR-001: Stack Backend — Django + DRF vs FastAPI

**Estado:** Aceptado  
**Fecha:** Mayo 2026  
**Autor:** Giuliano Zulatto  
**Proyecto:** Zenith  

---

## Contexto

El SRS de Zenith define un backend que expone una API REST para una SPA en React + TypeScript.
El dominio es financiero: cuentas, transacciones, cuotas, gastos compartidos y tipos de cambio.
Las restricciones relevantes para esta decisión son:

- Desarrollador único con experiencia probada en Django/PostgreSQL (Lino Saludable, ERP en producción).
- MVP en 6–8 semanas de trabajo focalizado.
- RNF-001: < 500ms P95 bajo 2 usuarios concurrentes, dataset de 5.000 transacciones.
- RNF-006: cobertura >= 80% en capa de dominio.
- RS-001 a RS-006: seguridad OWASP desde el diseño.
- Atributo más crítico: aislamiento de datos entre usuarios (RNF-005).
- No hay asincronía crítica en el MVP: sin websockets, sin background jobs, sin I/O concurrente masivo.

---

## Decisión

**Se elige Django 5.x + Django REST Framework (DRF) como stack backend.**

---

## Alternativas evaluadas

### Opción A — Django 5.x + DRF (elegida)

Django es un framework de "baterías incluidas" con ORM maduro, sistema de migraciones, admin panel y ecosistema de testing (pytest-django) que el autor ya domina en producción.

Ventajas concretas para Zenith:
- El ORM de Django con `select_related` / `prefetch_related` resuelve consultas complejas (transacciones + cuotas + categorías) sin N+1 y sin escribir SQL manual.
- Las migraciones automáticas reducen riesgo de error en cambios de esquema.
- DRF tiene `IsAuthenticated` y ownership checks que se integran naturalmente con el aislamiento de datos requerido por RNF-005.
- `pytest-django` + `APIClient` permiten escribir tests de integración contra endpoints reales sin overhead de configuración.
- Cero curva de aprendizaje: el autor ya deployó un ERP completo con este stack.

Desventajas aceptadas:
- Overhead de Django para una API pequeña (2 usuarios, 5.000 transacciones max en MVP): irrelevante dado que RNF-001 pide 500ms, no 50ms.
- El admin panel de Django no se usa en el MVP (los usuarios se crean por script de setup), pero tampoco agrega complejidad al no configurarlo.

### Opción B — FastAPI + SQLModel/Alembic

FastAPI es más rápido en benchmarks de throughput puro y tiene validación automática con Pydantic.

Por qué se descarta para Zenith:
- La ventaja de rendimiento de FastAPI sobre Django es medible recién a partir de cientos de requests/segundo concurrentes. Con 2 usuarios y RNF-001 en 500ms, Django supera el umbral sin optimización.
- Requiere configurar manualmente ORM (SQLModel o SQLAlchemy), migraciones (Alembic), y testing (httpx + pytest). Eso es 1–2 semanas de setup en las que no se construye lógica de negocio.
- Sin experiencia previa del autor en este stack en producción: introduce riesgo en el camino crítico del MVP.
- La asincronía de FastAPI no aporta valor: Zenith no tiene endpoints con I/O concurrente pesado en el MVP.

**Resumen de la tabla GZSM §F2.3:**

| Criterio | Django (Zenith) | FastAPI |
|---|---|---|
| Dominio | Lógica de negocio densa (cuotas, TC histórico, shared balance) | ✗ Más apto para microservicios |
| Admin | No crítico, pero disponible | Requiere construir desde cero |
| Validación | DRF Serializers cubren los casos | Pydantic es más estricto pero requiere setup |
| Asincronía | No crítica para el MVP | Ventaja real solo con I/O concurrente masivo |
| ORM | Relaciones complejas, señales, migrations automáticas | Control manual |
| Experiencia del autor | ✅ Producción real (Lino Saludable) | ✗ Sin experiencia en prod |

---

## Consecuencias positivas

- Velocidad de desarrollo máxima desde el día 1: el autor no necesita aprender herramientas nuevas.
- ORM de Django maneja correctamente las consultas de balance (transacciones + cuotas por fecha de vencimiento) con prefetch y anotaciones.
- El sistema de permisos de DRF (`IsAuthenticated` + object-level permissions) es el mecanismo natural para implementar RNF-005.
- El pipeline CI/CD (GitHub Actions + pytest-django) es un patrón ya conocido del autor.

## Consecuencias negativas (deuda técnica aceptada)

- Si en F4 se requiere alta concurrencia (> 100 req/s) o endpoints async, se necesitará evaluar migración a FastAPI o agregar Celery para background tasks. Esta decisión se registra como deuda técnica potencial de F4.
- El admin panel de Django queda disponible pero sin configuración en el MVP. No es un riesgo de seguridad si no se expone públicamente (variable de entorno controla su activación).

---

## RNF impactados

| RNF | Cómo esta decisión lo satisface |
|---|---|
| RNF-001 (< 500ms P95) | Django + ORM optimizado con select_related supera el umbral para 5.000 transacciones y 2 usuarios. |
| RNF-003 (bcrypt/Argon2id) | Django tiene `make_password` / `check_password` con Argon2 como backend configurable desde `settings.py`. |
| RNF-005 (aislamiento de datos) | DRF object-level permissions + queryset filtering por `request.user` es el patrón idiomático de Django. |
| RNF-006 (cobertura >= 80%) | pytest-django + coverage.py es el stack de testing estándar del autor, sin fricción de setup. |
| RS-001 (SQL injection) | Django ORM parametriza todas las queries por defecto. `bandit` verifica ausencia de raw SQL sin parámetros. |
