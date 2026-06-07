/**
 * AUSTRAL Design System — tokens completos.
 * Derivado de CLAUDE.austral.md (v1.4). Dark mode only.
 * NUNCA hardcodear hex en componentes: usar estas clases.
 */
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Fondos (de más oscuro a más claro)
        void: '#06080F',
        cosmos: '#0C0F1A',
        nebula: '#12162A',
        orbit: '#1A1F33',
        horizon: '#252B42',
        // Texto
        star: '#EDF0F8',
        moon: '#A6B3CC',
        dusk: '#56637A',
        // Acentos
        celeste: {
          DEFAULT: '#4AAEEE',
          bright: '#7DCEF8',
          dim: '#0E2A42',
        },
        steel: '#B8C8D8',
        sol: '#D4A837',
        // Funcionales
        ok: '#3DAF7A',
        error: '#E05252',
        warn: '#E09A3D',
      },
      fontFamily: {
        display: ['Sora', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }], // 12px
        sm: ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        base: ['1rem', { lineHeight: '1.5rem' }], // 16px
        xl: ['1.25rem', { lineHeight: '1.75rem' }], // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }], // 24px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
        '7xl': ['4.5rem', { lineHeight: '1' }], // 72px
      },
      borderRadius: {
        lg: '0.75rem', // 12px — radio estándar AUSTRAL
      },
      boxShadow: {
        celeste: '0 0 0 1px rgba(74, 174, 238, 0.25), 0 8px 24px -8px rgba(74, 174, 238, 0.35)',
      },
    },
  },
  plugins: [],
}
