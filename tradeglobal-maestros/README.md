# Fichas de Registro de Maestros — TradeGlobalChile

Dos fichas mobile-first para captar y dar onboarding a maestros instaladores.

## Stack
Next.js 14 (App Router) + TypeScript + Tailwind. Sin dependencias extra.

## Correr
```bash
npm install
npm run dev    # http://localhost:3000  → redirige a /maestros
```

## Rutas
- **Ficha 1 — Captación liviana:** `/maestros` (la del QR / WhatsApp / Meta Ads).
- **Ficha 2 — Registro completo:** `/maestros/registro` (link privado por WhatsApp).

## Identidad
Navy `#0F2942`, naranjo `#FF6B35`, fondo cálido `#F5F3EF`, tipografía Inter. Definido en `tailwind.config.ts`.

## Validaciones (`lib/validations.ts`)
- **RUT** chileno con dígito verificador (módulo 11) — usado en datos personales y titular bancario.
- **Teléfono** celular `+56 9 XXXX XXXX`.
- **Email** formato estándar.

## 🔌 Conectar el backend (PostgreSQL / Express)
Todo el envío pasa por **`lib/submit.ts`** (`submitCaptacion` y `submitRegistro`). Hoy están en **modo MOCK** (simulan éxito y hacen `console.log`). Para producción:

1. Define la variable de entorno `NEXT_PUBLIC_API_BASE` (ej. `https://api.tradeglobalchile.cl`).
2. En `lib/submit.ts`, **descomenta el bloque "BACKEND (producción)"** de cada función.
   - `submitCaptacion` → `POST /maestros/captacion` (JSON) → inserta en `maestros` (estado lead).
   - `submitRegistro` → `POST /maestros/registro` (**multipart/form-data**, incluye los archivos).
3. **Fallback** sin backend: hay un bloque comentado para enviar a **Tally / Google Sheets** (webhook / Apps Script) — descomenta ese en lugar del backend si lo necesitas antes.

## Documentos (Ficha 2)
Los archivos (cédula requerida; certificado y foto opcionales) se adjuntan como `File` y viajan en el `FormData` (`cedula`, `certificado`, `foto`). El backend debe guardarlos (S3 / disco / bucket).

## Campo de estado (admin)
La Ficha 2 envía `estado: "Pendiente"` en el payload — **no es visible para el maestro**. La gestión Pendiente/Aprobado/Rechazado se hace en el **panel admin del backend** (tabla `maestros`), no en este frontend.
