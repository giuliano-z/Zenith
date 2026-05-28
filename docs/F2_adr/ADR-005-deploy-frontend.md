# ADR-005: Deploy Frontend — Railway Static vs Vercel vs Netlify

**Estado:** Aceptado  
**Fecha:** Mayo 2026  
**Autor:** Giuliano Zulatto  
**Proyecto:** Zenith  

---

## Contexto

El SRS define una SPA en React + TypeScript como frontend, desacoplada del backend (API REST en Django).
El §6.1 menciona tres opciones para el deploy del frontend: Railway Static, Vercel o Netlify.
RNF-010 exige que el deploy sea documentable en < 10 pasos y que solo variables de entorno distingan entornos.
El backend se deploya en Railway (ADR-001 confirma el stack Django + Railway).

El frontend es una SPA: un bundle estático (HTML + JS + CSS) que se sirve desde un CDN. No tiene servidor propio.
La única variable de entorno necesaria es `VITE_API_URL` (o equivalente): la URL del backend en Railway.

---

## Decisión

**El frontend se deploya en Vercel.**

El backend continúa en Railway (decisión previa, fuera del alcance de este ADR).

---

## Alternativas evaluadas

### Opción A — Vercel (elegida)

Vercel es el deploy target natural para proyectos React + Vite. La integración es:
1. Conectar el repositorio GitHub.
2. Vercel detecta el framework (Vite/React) automáticamente.
3. Configurar `VITE_API_URL` como variable de entorno en el dashboard de Vercel.
4. Cada push a `main` deploya automáticamente.

Ventajas:
- CDN global con edge locations: el bundle JS se sirve rápido independientemente de la ubicación del usuario. Para un portfolio técnico con evaluadores internacionales, esto importa.
- Preview deployments automáticos por PR: cada rama tiene su propia URL de preview. Útil para validar UI antes de mergear a main.
- Free tier generoso: sin costo para el MVP y para portfolio.
- HTTPS automático con certificado SSL.
- El dominio de Vercel (`.vercel.app`) es reconocible y profesional para un portfolio.
- Integración con GitHub Actions: el pipeline CI puede correr linting/tests del frontend antes de que Vercel deploya.

Desventajas:
- Un servicio externo adicional (además de Railway). El sistema tiene dependencia en dos plataformas.
- La variable `VITE_API_URL` debe estar configurada correctamente o el frontend no puede hablar con el backend. Este es el único punto de configuración crítico.

### Opción B — Railway Static

Railway permite servir archivos estáticos como un servicio adicional en el mismo proyecto que el backend.

Por qué se descarta:
- Railway Static no tiene CDN global nativo de la misma forma que Vercel. La latencia de serve del bundle JS depende de la región del servidor Railway.
- No hay preview deployments automáticos por PR en Railway Static.
- La ventaja de "todo en Railway" es la simplicidad operacional (un solo dashboard). Pero dado que Vercel tiene integración con GitHub igualmente simple, el beneficio no justifica sacrificar CDN y preview deployments.
- Para un portfolio técnico, tener frontend en Vercel y backend en Railway es un stack común y reconocible que muestra conocimiento de las plataformas modernas.

### Opción C — Netlify

Netlify es funcionalmente equivalente a Vercel para este caso de uso. Ambos tienen CDN global, preview deployments, HTTPS automático y free tier.

Por qué se descarta frente a Vercel:
- Vercel es el creador de Next.js y tiene integración más profunda con el ecosistema React/Vite.
- La DX (Developer Experience) de Vercel para proyectos React es marginalmente mejor (detección automática de framework, configuración de build sin tocar `netlify.toml`).
- Es una decisión de preferencia marginal: si el autor tuviera experiencia previa con Netlify, sería igualmente válido.

---

## Configuración mínima

```yaml
# vercel.json (en la raíz del directorio frontend/)
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

El rewrite `/(.*) → /index.html` es necesario para que React Router maneje las rutas del lado del cliente correctamente. Sin esto, un refresh en `/dashboard` devuelve 404.

Variable de entorno requerida en Vercel:
```
VITE_API_URL=https://zenith-backend.up.railway.app
```

---

## Consecuencias positivas

- Deploy automático en cada push a `main`: el flujo de trabajo es `git push → CI verde → Vercel deploya automáticamente`.
- Preview deployments: validar UI en producción-like environment antes de mergear.
- CORS: el backend Django debe configurar `CORS_ALLOWED_ORIGINS` con el dominio de Vercel. Esta configuración va en `config/settings/production.py` y en las variables de entorno de Railway.
- El dominio final del portfolio será algo como `zenith.vercel.app` para el frontend y `zenith-api.up.railway.app` para el backend: URLs claras y distinguibles.

## Consecuencias negativas (deuda técnica aceptada)

- CORS debe configurarse explícitamente en el backend. El package `django-cors-headers` se agrega como dependencia en `requirements/base.txt`. La configuración incorrecta de CORS es el error #1 en setups frontend/backend separados: se documenta en el README con instrucciones explícitas.
- Dos plataformas de deploy en vez de una. En caso de incidente, hay dos dashboards distintos a revisar. Con 2 usuarios y uso personal, el overhead operacional es despreciable.

---

## RNF impactados

| RNF | Cómo esta decisión lo satisface |
|---|---|
| RNF-008 (Docker Compose) | El backend + DB van en Docker Compose. El frontend en desarrollo también puede levantarse con `npm run dev` sin Docker (o con un servicio adicional en docker-compose para desarrollo). |
| RNF-010 (deploy documentable en < 10 pasos) | Vercel: 5 pasos (cuenta, conectar repo, variable de entorno, dominio, listo). Railway backend: ya documentado. Total: < 10 pasos combinados. |
| RS-003 (HTTPS obligatorio) | Vercel provee HTTPS con certificado SSL automático. El backend en Railway también. |
