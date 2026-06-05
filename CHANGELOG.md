# Changelog — Zenith

## [Unreleased]
### Added — Fase 4 (TRANSACTIONS)
- RF-014: modelo Category (income/expense) + seed de 16 categorías del sistema vía data migration
- Modelos Transaction e InstallmentPurchase
- ADR-004: get_transaction_sum_for_account (suma neta para el balance) integrado en el balance de cuentas (detalle/lista y consolidado por moneda)
- RF-009: POST /api/transactions/ (income/expense) y POST /api/transactions/transfer/ (par TRANSFER_OUT/IN vinculado)
- RF-010: POST /api/transactions/installment/ (compra en cuotas, N transacciones mensuales)
- RF-011: GET /api/transactions/ con filtros (account, category, type, date_from/to), paginación de a 20 y aislamiento por usuario
- Seguridad (RS-004): cuenta ajena → 403 (nunca 404); sin token → 401
- 26 tests: 9 unitarios (services + integración ADR-004) + 17 integración (endpoints)

### Dependencies
- python-dateutil agregado a requirements/base.txt (fechas mensuales de cuotas)

## [v0.1.0-auth] — 2026-06-03
### Added
- Modelo User custom (AbstractBaseUser, identidad por email)
- django-knox configurado (TOKEN_TTL=24h, tokens opacos en DB)
- RF-001: registro de usuario con contraseña hasheada (Argon2id)
- RF-002: login con token knox; 401 genérico sin enumeración (RS-002)
- RF-003: logout invalida token, reintento devuelve 401
- 22 tests: 11 unitarios (services) + 9 integración (views)

### Fixed
- argon2-cffi agregado a requirements/base.txt (faltaba desde F1)
- noqa S104 + nosec B104 en ALLOWED_HOSTS development

## [v0.1.0] — 2026-05-27
### Added
- Estructura inicial del proyecto GZSM v1.1
- SRS completo F1 (docs/F1_srs.md)