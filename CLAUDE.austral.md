# AUSTRAL Design System — Instrucciones para Claude Code

Sistema de diseño base para todos los proyectos de Giuliano Zulatto.
Lee este archivo antes de generar cualquier componente visual.

---

## Stack tecnológico

- **Frontend:** React + TypeScript + Vite
- **Estilos:** Tailwind CSS (con tema AUSTRAL configurado)
- **Componentes:** shadcn/ui (style: New York)
- **Iconos:** Lucide React
- **Animaciones:** Framer Motion
- **Fuentes:** @fontsource/sora · @fontsource/plus-jakarta-sans · @fontsource/ibm-plex-mono

---

## Paleta — NUNCA hardcodear hex, siempre usar clases Tailwind

### Fondos (de más oscuro a más claro)
```
bg-void      #06080F   → el vacío absoluto
bg-cosmos    #0C0F1A   → background principal de cada página
bg-nebula    #12162A   → cards, paneles, contenedores
bg-orbit     #1A1F33   → superficies elevadas, modales
bg-horizon   #252B42   → bordes, separadores
```

### Texto
```
text-star    #EDF0F8   → texto principal (headings, body)
text-moon    #A6B3CC   → texto secundario
text-dusk    #56637A   → texto muted, labels, placeholders
```

### Acentos
```
text-celeste / bg-celeste         #4AAEEE   → acento principal
text-celeste-bright / bg-celeste-bright     #7DCEF8   → hover, highlight
bg-celeste-dim                    #0E2A42   → bg de badges activos
text-steel / bg-steel             #B8C8D8   → acento secundario, iconos
text-sol / bg-sol                 #D4A837   → Sol de Mayo, SOLO decorativo
```

### Funcionales
```
text-ok / bg-ok      #3DAF7A   → success, positivo
text-error / bg-error #E05252  → error, destructivo
text-warn / bg-warn   #E09A3D  → warning, atención
```

---

## Tipografía

```
font-display   → Sora          → headings, wordmarks, títulos
font-body      → Plus Jakarta  → body text, labels, UI (default)
font-mono      → IBM Plex Mono → código, datos técnicos, labels mono
```

### Pesos por uso
- Headings principales: `font-display font-extrabold` (800)
- Subtítulos: `font-display font-bold` (700) o `font-semibold` (600)
- Body: `font-body font-normal` (400) o `font-medium` (500)
- Labels: `font-body font-semibold` (600)
- Mono: `font-mono font-normal` (400)

### Escala de texto
```
text-xs   → 12px  → labels técnicos, mono uppercase
text-sm   → 14px  → body secundario, descripciones
text-base → 16px  → body principal
text-xl   → 20px  → subtítulos
text-2xl  → 24px  → sección headings
text-4xl  → 36px  → page headings
text-7xl  → 72px  → display / hero
```

---

## Componentes base — Patterns estándar

### Card default (sobre cosmos)
```tsx
<div className="bg-nebula border border-horizon rounded-lg p-6 
                transition-colors duration-150
                hover:border-celeste/40">
```

### Card elevada (destacada)
```tsx
<div className="bg-orbit border border-horizon/70 rounded-lg p-6">
```

### Card activa / featured
```tsx
<div className="bg-nebula border border-celeste rounded-lg p-6 
                shadow-celeste">
```

### Botón primario
```tsx
<button className="bg-celeste text-void font-body font-bold 
                   rounded-lg px-5 py-2.5 text-sm
                   hover:bg-celeste-bright 
                   transition-colors duration-150">
```

### Botón secundario
```tsx
<button className="bg-transparent text-celeste border border-celeste 
                   font-body font-semibold rounded-lg px-5 py-2.5 text-sm
                   hover:bg-celeste-dim
                   transition-colors duration-150">
```

### Botón ghost
```tsx
<button className="bg-transparent text-moon border border-horizon 
                   font-body font-semibold rounded-lg px-5 py-2.5 text-sm
                   hover:bg-orbit hover:text-star hover:border-horizon/70
                   transition-all duration-150">
```

### Input
```tsx
<input className="bg-orbit border border-horizon rounded-lg px-3 py-2.5 
                  text-sm font-body text-star
                  placeholder:text-dusk
                  focus:outline-none focus:border-celeste 
                  focus:ring-2 focus:ring-celeste/15
                  transition-all duration-150" />
```

### Badge activo
```tsx
<span className="bg-celeste-dim text-celeste-bright border border-celeste/25 
                 rounded-full px-3 py-1 text-xs font-semibold">
```

### Divisor franja argentina
```tsx
<div className="h-px flex overflow-hidden opacity-50">
  <div className="flex-1 bg-celeste" />
  <div className="flex-1 bg-star" />
  <div className="flex-1 bg-celeste" />
</div>
```

---

## Reglas de diseño — SIEMPRE respetar

1. **Dark mode only** — este sistema no tiene light mode
2. **Border-radius lg (12px)** en casi todos los contenedores
3. **Transiciones: 150ms ease-out** para hover/focus rápidos; 250ms para entrances
4. **Celeste es el único acento cromático** — no introducir otros colores de acento
5. **Sol (#D4A837) solo decorativo** — nunca en texto funcional ni iconografía operativa
6. **Máximo 2 motivos argentinos por vista** — no acumularlos
7. **Nunca hardcodear hex** — siempre usar las clases Tailwind del sistema
8. **Framer Motion para animaciones** — no CSS @keyframes salvo en casos muy simples

---

## Motivos argentinos disponibles

Solo usar 1–2 por proyecto/vista:
- **Sol de Mayo** → splash screens, loaders, watermarks
- **Cruz del Sur** → hero backgrounds, iconografía de navegación
- **Franja argentina** → divisores de secciones importantes (celeste/blanco/celeste)
- **Estela de lanzamiento** → línea vertical celeste en heroes/banners
- **Silueta de Argentina** → about pages, footer, portfolio personal
- **Escudo nacional** → solo contextos de máxima formalidad
- **Mate** → onboarding, about, identidad informal
- **Laureles** → achievement badges, reconocimientos
- **Obelisco** → proyectos BA-focused, identidad urbana

---

## Convención de naming de proyectos

Término astronómico en español. Excepción si lleva nombre del cliente.

Existentes: **Lino** (ERP cliente), **Zenith** (finance), **Orbit** (venture ideation)  
Reservados: Apogeo, Meridiano, Eclíptica, Cenit, Crux, Austral (marca personal)

---

## Marca personal

**AUSTRAL** — `austral.dev` — @gzulatto  
*Systems from the South*

---

*AUSTRAL Design System v1.4 · Giuliano Zulatto · 2026*
