# Rotación de secretos — Portal Mayorista

## Hecho 2026-06-22 (autónomo, prod)
- ✅ **AUTH_SECRET** rotado en Vercel (prod) + `.env` local. Cerró sesiones viejas.
- ✅ **ADMIN_PASSWORD** rotado. Nueva clave admin: **`3GswRDjerXbtfk74kSxM`**
  (email `victor@comercialsolutions.cl`). **Guárdala en tu gestor de contraseñas.**
  Verificado en vivo: la nueva entra, la vieja ya no.

## Pendiente — clave de Neon (la más crítica, necesita la consola)
Es la que pudo causar el vaciado del 22/06. Pasos:

1. **console.neon.tech** → proyecto de la base `ep-billowing-haze-ac6fvv0c`.
2. **Roles** (o **Settings → Database/Roles**) → rol `neondb_owner` → **Reset password**.
3. Neon te muestra la **nueva cadena de conexión** (`postgresql://neondb_owner:NUEVA@...`).
   Cópiala completa. ⚠️ Se muestra una sola vez.
4. Pásamela y yo:
   - actualizo `DATABASE_URL` en **Vercel** (prod) y en `.env` local,
   - redeployo,
   - verifico que el portal y los scripts (refresco/backup) sigan conectando.

   (O si prefieres hacerlo tú: `DATABASE_URL` va en Vercel → Settings → Environment
   Variables, y en `portal-mayorista/.env`. Deben quedar idénticas.)

> Mientras tanto, el backup diario (`TradeBackupPortal`) ya te cubre ante otro vaciado.
