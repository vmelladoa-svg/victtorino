# Guía — Backup y restauración de la base del Portal Mayorista (Neon)

Base: `ep-billowing-haze-ac6fvv0c` (sa-east-1). Prod y `.env` local comparten esta base.

## Red de recuperación que YA quedó automática (no depende del plan de Neon)
- **`backup_portal.py`** vuelca todas las tablas a `data/backups/full_<fecha>/` (JSON), conserva los últimos 14.
- **Tarea Windows `TradeBackupPortal`**: corre diario **6:45 AM** (15 min antes del refresco). Probada, resultado 0.
- **Restaurar** desde cualquier respaldo:
  ```
  python restaurar_portal.py data\backups\full_2026-06-22T22-50-38
  ```
  (pide escribir "restaurar"; es transaccional: si algo falla, revierte todo. `--si` para saltar la confirmación.)

Esto cubre el caso del 22/06 (tablas vaciadas): aunque el incidente pase de noche, a la mañana hay una foto del día anterior.

---

## Neon PITR (instant restore) — complemento, lo configuras tú en la consola

> Por qué además del backup: PITR te deja volver a **cualquier segundo** dentro de la ventana (recuperación fina), mientras el backup diario es 1 foto al día. Los dos juntos = cinturón + tirantes.

### Ventanas por plan (2026)
| Plan | Ventana de historial (PITR) | Costo del historial |
|------|------------------------------|---------------------|
| **Free** | hasta **6 horas** (default 6h) | gratis (tope 1 GB de cambios) |
| **Launch** | hasta **7 días** | $0,20 por GB-mes de cambios |
| **Scale** | hasta **30 días** | $0,20 por GB-mes de cambios |

⚠️ El plan Free **ya no da 24h, son 6h** (cambió en 2025). Con 6h, si la base se vacía de noche, PITR no alcanza a salvarte → por eso el backup diario local es la red principal.

### (a) Ver tu plan y ventana actual
1. Entra a **console.neon.tech** → elige el proyecto de esta base (`ep-billowing-haze-...`).
2. Arriba a la derecha o en **Billing** ves el plan (Free / Launch / Scale).
3. **Settings → Instant restore** (antes "Point-in-time restore"): ahí está el slider con la retención actual.

### (b) Subir la ventana a ≥7 días
- Si estás en **Free**: el máximo es 6h. Para 7 días hay que pasar a **Launch**. Con esta base (datos mínimos, pocos cambios al día) el costo del historial es de **centavos al mes** — se factura por GB de *cambios*, no por tiempo.
- Si ya estás en **Launch/Scale**: en **Settings → Instant restore**, mueve el slider a **7 días** (o más) → **Save**. Afecta a todas las branches del proyecto.

### (c) Cómo restaurar con PITR (si algo pasa)
1. Consola → proyecto → **Branches** → **Restore** (o "Time Travel").
2. Eliges el branch y la **fecha/hora exacta** a la que volver (dentro de la ventana).
3. Confirmas. Neon crea el estado restaurado; revisa antes de apuntar prod ahí.

### Recomendación
Para arrancar con comerciantes reales, el **backup diario local (ya activo) basta** como red. Pasar a Launch + 7 días de PITR es un "nice to have" barato que te da recuperación al segundo; hazlo cuando empiece a haber movimiento real de pedidos. Mientras tanto, no es bloqueante.
