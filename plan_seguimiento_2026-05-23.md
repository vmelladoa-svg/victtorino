# Plan de Seguimiento — Optimización ML 2026-05-23

Baseline: **2026-05-23** · Próximos hitos: **D+7 (2026-05-30)**, **D+14 (2026-06-06)**, **D+28 (2026-06-20)**

## 1. Cronograma

### 2026-05-23 — BASELINE (hoy)
- **Acción**: Cambios aplicados: 24 upgrades gold_pro + 2 sync attrs + 14 fotos + 1 título + 7 bajadas precio. Baseline JSON capturado.
- **Responsable**: Claude (ya hecho)
- **Estado**: ✓ Hecho

### 2026-05-23 — Activar Mercado Ads C3
- **Acción**: Crear campaña 10 SKUs en Seller Center con bids individuales del instructivo
- **Responsable**: Victor (manual)
- **Estado**: ⏳ Pendiente

### 2026-05-26 — D+3 — Check rápido Ads
- **Acción**: Sólo Mercado Ads: confirmar que la campaña recibe impresiones (>500/día) y clicks (>10/día)
- **Responsable**: Victor en Seller Center
- **Estado**: ⏳

### 2026-05-30 — D+7 — Primer check
- **Acción**: Correr: auditoria_ml.py + fix_visitas_snapshots.py + analisis_auditoria_ml.py + seguimiento_comparar.py
- **Responsable**: Claude (ejecutar)
- **Estado**: ⏳

### 2026-06-06 — D+14 — Check principal
- **Acción**: Re-correr scripts. Decisión: escalar / mantener / revertir. Reporte ejecutivo.
- **Responsable**: Claude + Victor
- **Estado**: ⏳

### 2026-06-20 — D+28 — Cierre y plan v2
- **Acción**: Análisis final 30d post. Decisión sobre los 'muertos' (republicar / pausar). Plan próximas acciones.
- **Responsable**: Claude + Victor
- **Estado**: ⏳

## 2. KPIs y metas por cohorte

| Cohorte | KPI | Baseline | Meta D+14 | Meta D+28 | Si falla |
|---|---|---|---|---|---|
| upgrade_listing (24) | Visitas 30d | 157 total | +50% (~235 visitas) | +100% (~315 visitas) | Re-evaluar listing_type vs categoría / atributos |
| upgrade_listing (24) | Ventas 30d | estimar 4-5 | 8-10 | 12-15 | Revisar precio competencia + categoría |
| bajada_precio (7) | Conversión (Vendidos/Visitas) | 0% | >1% (al menos 5-10 ventas) | >3% | Investigar competencia, calidad ficha, fotos |
| bajada_precio (7) | Ventas absolutas | 0 | 3-5 ventas | 10+ ventas | Probar otra bajada de 5% más o pausar |
| fotos_cross (14) | Health avg | 37.6 | >50 | >60 | Completar atributos faltantes en estos items |
| sync_atributos (2) | Visitas 30d | 6 | 20+ | 50+ | Sync atributos RISKY (FINISH, dimensiones) si Victor valida físicamente |
| titulo_playwright (1) | Visitas 30d | 0 | >10 (señal de revivir) | >25 | No escalar a más cambios de título. Considerar republicar. |
| ads_top10 (10) | ROAS (Revenue/Gasto Ads) | N/A (sin Ads) | >3x | 5-8x | Bajar bids o eliminar SKUs no rentables. Pausar campaña si ROAS < 2x |
| ads_top10 (10) | Ventas atribuidas semanales | N/A | 10-25/sem total | 20-50/sem | Revisar segmentación y bid |
| control (30) | Visitas 30d | 393 | ~393 (sin cambio esperado) | ~393 | Grupo control no debería moverse mucho — si sube similar a intervenidos, atribución es ruido (no nuestros cambios) |

## 3. Criterios de decisión D+14

### ÉXITO TOTAL — todas las cohortes intervenidas suben +30%+ vs control
- **Lectura**: La estrategia funciona. Escalar.
- **Acción**: 1. Aplicar upgrade gold_pro a items ROI+ pendientes (los que excluimos por margen). 2. Bajar precio a otros 5-10 items con tráfico bajo. 3. Mantener Ads.

### ÉXITO PARCIAL — Ads + bajada precio suben pero upgrade no se mueve
- **Lectura**: Upgrade solo no alcanza. El precio + visibilidad pagada son los drivers.
- **Acción**: 1. Mantener Ads. 2. Escalar bajada precio a más items. 3. Para items sin movimiento, considerar republicar o pausar.

### Ads funciona, resto no
- **Lectura**: El algoritmo orgánico es resistente. Solo presencia pagada mueve la aguja.
- **Acción**: 1. Re-balancear inversión a Ads. 2. Pausar items 'muertos' orgánicamente. 3. Plan estratégico de catálogo (menos items pero mejor curados).

### Nada se mueve significativamente
- **Lectura**: Cambios fueron muy chicos para mover el algoritmo, O existe bloqueo estructural (catálogo, categoría, reputación).
- **Acción**: 1. Diagnóstico profundo de 5 items mejorados: por qué siguen invisibles. 2. Considerar republicar como reset. 3. Revisar reputación general de cuenta.

### Algunos items se MUEVEN HACIA ABAJO (regresión)
- **Lectura**: Cambios fueron contraproducentes (raro pero posible).
- **Acción**: 1. Identificar cuáles. 2. Revertir el cambio específico via API. 3. Análisis de causa raíz.

## 4. Comandos a ejecutar en D+7 / D+14 / D+28

```bash
# Re-snapshot completo (3 cuentas)
python auditoria_ml.py

# Fix visitas (endpoint multi-item de ML acepta solo 1 ID por call)
python fix_visitas_snapshots.py

# Re-construir dataframe
python analisis_auditoria_ml.py

# Comparar baseline vs hoy → genera seguimiento_diff_<fecha>.xlsx
python seguimiento_comparar.py

# Opcional: regenerar dashboard ejecutivo con datos frescos
python generar_dashboard_auditoria.py
python generar_informe_ejecutivo.py
```

## 5. Archivos clave de la sesión

- `data/auditoria/seguimiento_baseline_2026-05-23.json` — baseline inmutable (NO modificar)
- `data/auditoria/analisis.pkl` — dataframe consolidado (se regenera con cada análisis)
- `data/auditoria/snapshot_c1/c2/c3.json` — snapshots crudos por cuenta
- `data/auditoria/upgrade_listing_*.json` — logs de upgrades aplicados
- `data/auditoria/bajar_precio_*.json` — log bajada precios
- `data/auditoria/sync_atributos_*.json` — log sync atributos
- `data/auditoria/fotos_cross_*.json` — log cambios de fotos
- `data/auditoria/titulos_playwright_*.json` — log cambios de título
- `instructivo_mercado_ads_c3.xlsx` + `.md` — guía para activar Ads