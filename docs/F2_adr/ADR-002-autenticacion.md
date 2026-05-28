# ADR-002: Estrategia de Autenticación — JWT Stateless vs Tokens en DB

**Estado:** Aceptado  
**Fecha:** Mayo 2026  
**Autor:** Giuliano Zulatto  
**Proyecto:** Zenith  

---

## Contexto

El SRS requiere:
- RF-002: Login emite un token de acceso válido.
- RF-003: Logout invalida el token activo (cualquier request posterior con ese token devuelve 401).
- RS-002: Los tokens expiran en máximo 24 horas.
- RNF-004: Toda ruta protegida requiere token válido; sin token o con token expirado → HTTP 401.

El punto crítico es **RF-003**: el logout debe invalidar el token de forma que no pueda reutilizarse.
Esto crea una tensión directa con JWT stateless puro.

---

## Decisión

**Se elige tokens opacos almacenados en base de datos (Knox o implementación propia sobre DRF TokenAuthentication), con expiración configurada en 24 horas.**

No se usa JWT stateless para el MVP.

---

## Alternativas evaluadas

### Opción A — JWT Stateless puro (descartada)

JWT stateless significa que el servidor no guarda estado de sesión. El token se valida criptográficamente contra el `SECRET_KEY`.

Por qué se descarta:
- **RF-003 es incompatible con JWT stateless puro.** Un JWT firmado es válido hasta su expiración natural. Para "invalidarlo" en logout, el servidor necesita una blocklist (lista negra de tokens revocados), que es exactamente una base de datos de estado de sesión. Si se agrega blocklist, se pierde la ventaja de stateless y se agrega complejidad sin beneficio.
- Con 2 usuarios y sin necesidad de escalar a múltiples instancias en el MVP, la ventaja de stateless (no ir a DB por sesión) es irrelevante.
- Una blocklist JWT requiere TTL management adicional (limpiar tokens expirados de la blocklist). Complejidad no justificada.

Cuándo tendría sentido: sistema con múltiples instancias de backend sin sesión compartida, o refresh token + access token de corta vida (5 minutos). En ese patrón, el access token expira rápido y el logout invalida el refresh token en DB. Válido para F4 si escala.

### Opción B — Tokens opacos en DB con `django-knox` (elegida)

`django-knox` genera tokens opacos criptográficamente seguros (HMAC-SHA512), los almacena hasheados en PostgreSQL con fecha de expiración, y provee:
- `LoginView`: crea y devuelve token.
- `LogoutView`: invalida el token actual.
- Expiración configurable (`TOKEN_TTL` en settings).
- El token en DB está hasheado (similar a contraseña): incluso con acceso a la DB, no se puede reutilizar el hash como token.

Por qué cubre todos los requerimientos:
- RF-003: Logout borra la fila del token en DB. Request posterior con ese token → 401. ✅
- RS-002: `TOKEN_TTL = timedelta(hours=24)`. ✅
- RNF-004: `IsAuthenticated` de DRF + Knox verifica el token en cada request. ✅
- Sin complejidad de blocklist ni TTL management: Knox lo maneja internamente con `TokenAuthentication`.

### Opción C — DRF TokenAuthentication nativo (descartada por funcionalidad incompleta)

El `Token` model nativo de DRF no tiene expiración incorporada. Requeriría implementar manualmente la expiración con un campo `created` y un middleware que calcule si el token tiene más de 24 horas. Knox resuelve esto de forma probada y sin código custom.

---

## Consecuencias positivas

- Logout funcional desde el día 1, sin blocklist ni complejidad adicional.
- La expiración de 24 horas se configura en una línea en `settings.py`.
- El token almacenado en DB es hasheado: el almacenamiento de tokens es tan seguro como el de contraseñas.
- Knox es una librería madura, bien mantenida y compatible con DRF.
- La implementación de login/logout se reduce a heredar las vistas de Knox y configurar `TOKEN_TTL`.

## Consecuencias negativas (deuda técnica aceptada)

- Cada request autenticado hace una query a PostgreSQL para verificar el token. Con 2 usuarios y carga normal, el overhead es < 5ms y no compromete RNF-001.
- Si en F4 se escala a múltiples instancias de backend, se necesitará evaluar JWT con refresh tokens o compartir la sesión de Knox via Redis. Esta decisión se registra como deuda técnica de F4.
- Knox agrega una dependencia más al proyecto. El riesgo de mantenimiento es bajo: es una librería ampliamente usada en el ecosistema Django.

---

## RNF impactados

| RNF/RS | Cómo esta decisión lo satisface |
|---|---|
| RNF-004 (auth en rutas protegidas) | Knox + `IsAuthenticated` en cada ViewSet. Token inválido o ausente → 401 automático. |
| RS-002 (autenticación rota) | Token expirado en DB + logout real + sin "recordar contraseña". |
| RS-003 (exposición de datos sensibles) | El token se almacena hasheado en DB. Nunca en texto plano ni en logs. |
| RF-003 (logout funcional) | `knox.LogoutView` elimina la fila del token. Invalidación inmediata y definitiva. |
