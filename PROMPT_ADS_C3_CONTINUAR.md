# Prompt para continuar — Optimización Mercado Ads C3

> **Cómo usar este prompt**: copialo entero y pegalo en una nueva sesión de Claude Code apuntando al directorio `C:\Users\dell\victtorino`. Si lo usás en Claude.ai web (sin tools), Claude solo podrá generar plan/scripts pero no ejecutar — preferí Claude Code.

---

## CONTEXTO

Soy Victor, dueño de 3 cuentas MercadoLibre Chile (rubro griferías/baño/cocina):
- **C1**: PREMIUMGRIFERIAS1 (user_id 483903060)
- **C2**: VICTTORINOOFICIAL2 (user_id 483904870)
- **C3**: NOVAGRIFERIAS3 (user_id 1194418785)

El 2026-05-23 ejecutamos una auditoría integral. Aplicamos 47 cambios via API:
- 24 upgrades gold_special → gold_pro (logs en `data/auditoria/upgrade_listing_*.json`)
- 2 sync atributos SAFE (`data/auditoria/sync_atributos_*.json`)
- 14 fotos cross-cuenta (`data/auditoria/fotos_cross_*.json`)
- 7 bajadas precio -10% en items con tráfico sin venta (`data/auditoria/bajar_precio_*.json`)
- 1 cambio de título via Playwright (piloto, `data/auditoria/titulos_playwright_*.json`)

**Tarea Windows** `VicttorinoSeguimientoML` registrada para correr el pipeline de seguimiento (re-snapshot + comparativa) en D+7 (2026-05-30), D+14 (2026-06-06), D+28 (2026-06-20).

**Baseline inmutable** en `data/auditoria/seguimiento_baseline_2026-05-23.json` con 87 items intervenidos + 30 control.

Plan de seguimiento en `plan_seguimiento_2026-05-23.md`.

---

## ESTADO ACTUAL DE MERCADO ADS C3 (medido 2026-05-24)

**Advertiser**: id 79197, nombre publicitario "JOSERUBEN2", visible desde token C3.

### 2 campañas:
1. **"Campaña Mayo"** (id `357141159`) — ACTIVA
   - Creada 2026-04-30 (24 días)
   - Estrategia: PROFITABILITY
   - ACOS target: 20.41% | ROAS target: 4.9x
   - Presupuesto: $20.000 CLP/día
   - **Período de aprendizaje termina 2026-05-28** ← NO TOCAR antes de esta fecha
   - 154 items totales

2. **"Campaña Mercado Libre"** (id `354999960`) — PAUSADA desde 2026-03-09

### Performance 7 días (2026-05-17 a 2026-05-24) de Campaña Mayo:
- 154 items totales | 38 con clicks | 9 con ventas directas
- Clicks: 732
- Cost: $77.705 CLP (real, post-dedup)
- Ventas directas atribuidas: 9 items, 18 unidades
- Revenue directo: $653.465 CLP
- **ROAS real: 8.41x** ✅ (sobre target 4.9x)
- **ACOS real: 11.9%** ✅ (bajo target 20.41%)

Excel completo: `auditoria_ads_c3_2026-05-24.xlsx` (6 hojas)

---

## EL PROBLEMA QUE NECESITO RESOLVER

Quiero optimizar la campaña para mejorar aún más el ROAS. Acciones identificadas:

### 🟢 SEGURAS HOY (no reinician aprendizaje):
1. **Pausar 2 espejos LED top-gastadores con 0 ventas** (ahorra $21.872 CLP/semana):
   - `MLC1754361903` — Espejo Rectangular 3 Luces LED — 92 clicks, $12.572 gastado, 0 vtas, precio $81.990
   - `MLC1754550537` — Espejo 50x70 LED Blanco — 62 clicks, $9.300 gastado, 0 vtas, precio $52.290
2. **Pausar item con CPC desorbitado**: `MLC3779856474` — Pack Lavaplatos 80x44 Sec Izq + Llave — 24 clicks, $8.683 gastado ($361 CPC!), 0 vtas
3. **Pausar 116 items sin clicks 7d** (limpieza, mejora salud de la campaña). Lista completa en el Excel hoja "6. Sin clicks 7d".
4. **Agregar 1 item nuevo** que históricamente vende pero no está en la campaña:
   - `MLC3779796948` — Pack 80x44 Secador Derecho + Llave Monomando — bid sugerido $2.352/click

### 🟡 ESPERAR POST-28-MAYO (reinician aprendizaje, mejor con período cumplido):
1. **Subir bid +30-50% en top 4 ROAS**:
   - `MLC1306255939` — Lavaplatos 80x44 Sec Izquierdo — ROAS 57.08x con solo 17 clicks (subutilizado!)
   - `MLC1367027081` — Lavaplatos 100x44 Inox Izq — ROAS 18.89x
   - `MLC3779834584` — Pack 37x32 + Llave Lavacopa — ROAS 18.22x
   - `MLC3767800412` — Lavaplatos Sobreponer 150x50 — ROAS 17.87x
2. **Bajar bid -50% en items mid-performance**: 5 items con clicks moderados y 0 ventas (cost <$700/u). Lista en hoja "5. Con clicks sin venta" del Excel.
3. **Esperar 7 días más** a los 2 items que YA tienen precio bajado el 2026-05-23 (probando si nuevo precio convierte):
   - `MLC1893675967` (precio bajado de $84.624 a $76.000)
   - El otro item (revisar logs en `data/auditoria/bajar_precio_*.json`)

---

## EL BLOQUEO TÉCNICO YA DESCUBIERTO

Probé ejecutar las acciones via API ML pero el token C3 retorna:
```
401: "User does not have permission to write."
"com.mercadolibre.ads_search_pads_core.api.exceptions.UnauthorizedException"
```

**Causa**: el OAuth scope sí incluye `urn:ml:mktp:ads:/read-write`, pero el USER NOVAGRIFERIAS3 está como **VIEWER** del advertiser 79197 dentro de la plataforma Ads de ML (rol de plataforma ≠ scope OAuth).

Generamos un token nuevo con scope explícito `ads_write` (`tokens_joseruben2.json`) y dio el mismo error — confirma que es problema de rol de usuario, no de scope.

**Endpoints API confirmados**:
- `GET /advertising/advertisers/{aid}/product_ads/campaigns` ✓ funciona (lectura)
- `GET /advertising/advertisers/{aid}/product_ads/items?campaign_id=X` ✓ funciona (lectura, con métricas: clicks, cost, direct_units_quantity, organic_units_quantity, sov)
- `PUT /advertising/advertisers/{aid}/product_ads/items` ✗ 401 (sin permiso write)

---

## LO QUE NECESITO QUE HAGAS

Investigá y ejecutá la mejor opción de las siguientes (en orden de preferencia):

### Opción A: Encontrar otro camino vía API
- Probar variantes de URL/body que sí permitan write con scope actual
- Probar si existe `POST` (en vez de `PUT`) para cambio de status
- Probar endpoint de `keywords` o `ad_groups` si existe
- Tokens disponibles: `tokens_cuenta1.json`, `tokens_cuenta2.json`, `tokens_cuenta3.json`, `tokens_joseruben2.json` (todos del mismo CLIENT_ID `3959231945649654`)

### Opción B: Via Playwright (UI web)
A veces la UI permite cosas que la API rechaza. Probar:
- Abrir Chrome con storage `data/auditoria/playwright_storage/storage_C3.json` (sesión válida de C3)
- Navegar a la UI real de Mercado Ads (NO usar `https://www.mercadolibre.cl/ads/product-ads/campaigns/{id}` — da 404; usar `https://www.mercadolibre.cl/ads/` y dejar que ML rutee)
- Identificar el editor de campaña (probablemente requiere encontrar URL real explorando la SPA)
- Intentar pausar via UI el item `MLC3779856474` como piloto
- Si funciona → escalar a los 116 items sin clicks + 2 espejos top-gastadores + agregar MLC3779796948
- Si no funciona → confirma falta de permiso UI

Script existente de Playwright para Ads: `ads_piloto_pausar.py` (tiene login flow + Chrome maximizado + storage). Adaptarlo para navegar a la URL correcta del editor.

Script de exploración de URLs: `ads_descubrir_url.py` (abre Chrome, monitorea URLs cada 3s mientras vos navegás manualmente).

### Opción C: Si nada funciona, dejame un instructivo claro
Para hacer manualmente en Seller Center con tiempo estimado por acción.

---

## REGLAS DEL JUEGO (importantes)

1. **NO toques nada que reinicie el aprendizaje hasta el 28-mayo**. La campaña está performando bien (ROAS 8.41x sobre target 4.9x). El aprendizaje se reinicia con: cambios de bid, cambios de estrategia, cambios de presupuesto >20%, modificación masiva de items.
2. **Agregar items y pausar items individuales no reinicia el aprendizaje** (generalmente). Eso es lo "seguro hoy".
3. **Dry-run primero, ejecutar después**. Antes de cualquier PUT/POST, mostrame qué se enviaría y pedime confirmación.
4. **Log JSON de cada acción** en `data/auditoria/ads_modificaciones_<fecha>.json` con pre/post de cada item.
5. **Si la acción afecta dinero (cambios de bid, presupuesto)**: SIEMPRE pedir confirmación explícita antes de ejecutar.
6. **Si la acción es solo limpieza (pausar items sin clicks)**: podés ejecutar autónomamente y reportar al final.
7. **Verificar post-cambio**: cada item modificado, hacer GET después para confirmar que el cambio quedó aplicado.

---

## ARCHIVOS CLAVE A LEER PRIMERO

```
auditoria_ads_c3_2026-05-24.xlsx          ← métricas reales de los 154 items
data/auditoria/seguimiento_baseline_2026-05-23.json  ← items intervenidos + baseline
auditoria_ads_c3.py                       ← script que generó el Excel (sirve para re-correr)
get_token_joseruben.py                    ← OAuth flow si necesitás generar otro token
ads_piloto_pausar.py                      ← skeleton Playwright (necesita ajuste de URL real)
ads_descubrir_url.py                      ← inspector de URLs ML Ads
plan_seguimiento_2026-05-23.md            ← cronograma completo del seguimiento
```

---

## OUTPUT ESPERADO DE TU SESIÓN

1. **Reporte de qué funcionó**: ¿API? ¿UI? ¿Nada?
2. **Lista de items pausados/modificados** con timestamp + verificación post
3. **Log JSON** consolidado de las acciones aplicadas
4. **Si esperás al 28**: confirmación explícita de qué quedó para esa fecha
5. **Si algo bloquea**: instructivo manual claro para hacerlo en Seller Center

---

## PRINCIPIOS DE COLABORACIÓN CONMIGO

- Avanzá autónomo en lo que no toque dinero o no sea visible a terceros
- Pedí confirmación antes de: cambios de precio/bid, pausar items que SÍ venden, modificar configuración de campaña
- Si hay duda, errar al lado conservador (NO ejecutar)
- Después del 28-mayo, podemos hacer los cambios "riesgosos" (re-calibrar bids)
- Soy ingeniero/dueño, no me hace falta explicación básica de ML Ads — andá al grano

¡Gracias!
