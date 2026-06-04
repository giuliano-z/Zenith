# Changelog — Zenith

## [Unreleased]

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