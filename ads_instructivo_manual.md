# Instructivo manual — Optimización Mercado Ads C3

**Fecha**: 2026-05-24  
**Cuenta**: C3 (NOVAGRIFERIAS3, user_id 1194418785)  
**Advertiser**: 79197 (JOSERUBEN2)  
**Campaña**: Campaña Mayo (id `357141159`) — período aprendizaje termina **2026-05-28**

---

## Por qué este instructivo es manual y no automatizado

Probé exhaustivamente la API ML Ads con los 4 tokens (`tokens_cuenta1.json`, `tokens_cuenta2.json`, `tokens_cuenta3.json`, `tokens_joseruben2.json`):

| Endpoint | Método | Resultado |
|---|---|---|
| `/advertising/advertisers/{aid}/product_ads/items` | PUT | **401** "User does not have permission to write" |
| 13 variantes alternativas (POST/PATCH, distintas URLs) | varios | 404 (no existen) |

Verifiqué también con tokens C1 y C2 (sus respectivos advertisers 78985 y 79006) — **también 401**. El bloqueo es sistémico: los 3 usuarios ML están como VIEWER en sus advertisers, no como OWNER/ADMIN. Esto solo se cambia desde la UI por un admin del advertiser. Ver `ads_probar_api_write.py`, `ads_probar_c1_c2.py` y `data/auditoria/ads_probar_api_write_log.json` para detalle.

Para automatizar via Playwright también descubrí que la URL real del panel es **`https://ads.mercadolibre.cl/productAds`** (no la del prompt original). Las sesiones guardadas en `storage_C3.json` no cubren ese subdominio — requiere login fresco en `ads.mercadolibre.cl`. Si querés que prepare un Playwright con login interactivo, decime y lo armo.

---

## ACCIÓN 1 — Seguras hoy (no reinician aprendizaje)

**Ahorro estimado semanal: $30,555 CLP** (solo top 3 items abajo)

### 1A. Pausar 2 espejos LED top-gastadores con 0 ventas

**Tiempo estimado: 3 minutos**

- `MLC1754361903` — Espejo Rectangular Moderno 3 Luces Led Fría-calida Blanco  
  Precio $81,990 · Clicks 7d: 92 · Cost: $12,572 · CPC: $136  
  Permalink: https://articulo.mercadolibre.cl/MLC-1754361903-espejo-rectangular-moderno-3-luces-led-fria-calida-blanco-_JM

- `MLC1754550537` — Espejo 50x70 Rectangular Led Blanco  
  Precio $52,290 · Clicks 7d: 62 · Cost: $9,300 · CPC: $150  
  Permalink: https://articulo.mercadolibre.cl/MLC-1754550537-espejo-50x70-rectangular-led-blanco-_JM

**Cómo**:

1. Abrí Chrome y andá a https://ads.mercadolibre.cl/productAds
2. Logueate con C3 (NOVAGRIFERIAS3, importadoravicttorino1@gmail.com)
3. Andá a la campaña **"Campaña Mayo"** (id 357141159)
4. En la lista de items, buscá por ID o título: `MLC1754361903` y `MLC1754550537`
5. Toggle de estado: activo → pausado

### 1B. Pausar item con CPC desorbitado

**Tiempo estimado: 1 minuto**

- `MLC3779856474` — Pack Lavaplatos 80x44 Sec Izquierdo + Llave Monomando Inox P  
  Precio $84,816 · Clicks 7d: 24 · Cost: $8,683 · CPC: $361  
  Permalink: https://articulo.mercadolibre.cl/MLC-3779856474-pack-lavaplatos-80x44-sec-izquierdo-llave-monomando-inox-plateado-_JM

**Por qué**: 24 clicks a $361 CPC, 0 ventas. CPC promedio de la campaña es ~$106. Este item está "comiendo" presupuesto. Pausar mientras evaluamos si el precio o título tienen problema.

### 1C. Pausar items sin clicks 7d (limpieza masiva)

Hay **75 items activos sin un solo click en 7 días**. No están aportando, pero ocupan slot en la campaña y diluyen el aprendizaje.

**Recomendación**: pausar todos.  
**Tiempo estimado**: 15-30 min (depende si la UI permite multiselección).

📎 Lista completa de IDs para pausar: archivo `ads_items_pausar.txt` (un Item ID por línea, copy-paste a la UI).

Top 10 de la lista (resto en el .txt):

- `MLC3767961162` — Mezcladora De Baño Victtorino Monocomando De Acero Inox (precio $40,480)
- `MLC3724867792` — Válvula Lateral Para Wc Eficiente Y Durable (precio $6,290)
- `MLC3724811170` — Sifón De Desague Plástico 1 1/2 - 1 1/4 Grifería Blanco (precio $5,090)
- `MLC3723668148` — Monomando Ducha Notte Negro (precio $37,490)
- `MLC3723394010` — Kit Wc Anclaje Antifuga Admisión Blanco (precio $12,490)
- `MLC3723363252` — Monomando Tina Ducha Notte Negro Cromado (precio $52,664)
- `MLC3723362812` — Mango De Ducha Conster Línea Baño Plateado (precio $6,090)
- `MLC3723351584` — Plato Ducha Redondo Abs 20 Cm - Artículo Para Baño Plat (precio $8,390)
- `MLC3723349706` — Llave Monomando Lavatorio Moderno Alto Inoxidable Plate (precio $38,690)
- `MLC3723331844` — Llave De Paso  Para Gas Hi-he-12 2 Vías (precio $7,700)

### 1D. Agregar 1 item nuevo a la campaña

**Tiempo estimado: 2 minutos**

- `MLC3779796948` — Pack 80x44 Secador Derecho + Llave Monomando
  - Razón: histórico de ventas en ML pero NO está en la campaña actual
  - Bid sugerido: **$2.352/click** (puede ajustar la UI automáticamente al agregar)

**Cómo**: en el editor de campaña → "Agregar productos" → buscar por ID → confirmar bid.

---

## ACCIÓN 2 — Esperar al 2026-05-28 (post aprendizaje)

⚠️ **NO HACER ANTES DEL 28**. Estos cambios reinician el período de aprendizaje y harían perder la calibración que la campaña ya tiene (ROAS 8.41x sobre target 4.9x).

### 2A. Subir bid +30-50% en top 4 ROAS

Items subutilizados — alto ROAS con pocos clicks. Subiéndoles el bid los hacemos competir más fuerte por impresión.

- `MLC1306255939` — Lavaplatos Empotrado Simple 80x44 Secador Izquierdo Plate  
  ROAS: **57.08x** · Clicks 7d: 17 · Cost: $1,261 · CPC: $74  
  → **Subir bid +50%**

- `MLC1367027081` — Lavaplatos Empotrados Simple 100x44 Inox Izquierdo-191432514  
  ROAS: **18.89x** · Clicks 7d: 13 · Cost: $1,926 · CPC: $148  
  → **Subir bid +30%**

- `MLC3779834584` — Pack Lavaplatos 37x32 + Llave Lavacopa Inox Plateado  
  ROAS: **18.22x** · Clicks 7d: 40 · Cost: $4,214 · CPC: $105  
  → **Subir bid +30%**

- `MLC3767800412` — Lavaplatos Para Sobreponer 150x50 Cm 2 Bachas 2 Secadores Pl  
  ROAS: **17.87x** · Clicks 7d: 53 · Cost: $4,643 · CPC: $87  
  → **Subir bid +30%**

### 2B. Bajar bid -50% en items con tráfico sin venta

Items que reciben clicks pero no convierten. Bajar bid reduce gasto sin perder presencia.

⚠️ Excluye los que ya pausaste en Acción 1 (2 espejos LED + CPC alto).

- `MLC1893675967` — Pack Lavaplatos 100x44 Sec Derecho + Llave Monomando Inox Pl  
  Clicks 7d: 22 · Cost: $4,647 · CPC: $211 · ROAS 0
  → **Bajar bid -50%**

- `MLC1374063337` — Lavaplatos Doble Sobreponer 120x50 Inoxidable Izquierdo Plat  
  Clicks 7d: 33 · Cost: $2,269 · CPC: $68 · ROAS 0
  → **Bajar bid -50%**

- `MLC3335955534` — Espejo 45x60 Rectangular Led Blanco  
  Clicks 7d: 9 · Cost: $624 · CPC: $69 · ROAS 0
  → **Bajar bid -50%**

- `MLC3141164182` — Espejo Circular Con 3 Luces Led 60 Cm Baño Vestidor Negro  
  Clicks 7d: 15 · Cost: $550 · CPC: $36 · ROAS 0
  → **Bajar bid -50%**

- `MLC1754490675` — Espejo 60x90 Rectangular Con Ondas Blanco  
  Clicks 7d: 7 · Cost: $313 · CPC: $44 · ROAS 0
  → **Bajar bid -50%**

### 2C. Esperar 7 días más sobre items con precio bajado

- `MLC1893675967` (precio bajó de $84.624 a $76.000 el 2026-05-23)  
  Esperar a ver si el nuevo precio empieza a convertir antes de tocar el bid.

---

## CHECKLIST POST-EJECUCIÓN

Después de hacer los cambios manuales en la UI, ejecutar:

```
python auditoria_ads_c3.py
```

Esto regenera el Excel con las métricas actualizadas. Compará:
- Items con clicks 7d (debería bajar — ya pausaste los que no aportaban)
- Cost total 7d (debería bajar)
- ROAS campaña (debería mantenerse o mejorar)

---

## SI QUERÉS DESBLOQUEAR LA API EN EL FUTURO

Para que C3 pueda escribir via API, hay que cambiar el rol en la plataforma Ads:

1. En `https://ads.mercadolibre.cl/productAds` → Configuración → Usuarios / Equipo
2. Encontrar `NOVAGRIFERIAS3` y promoverlo de VIEWER a OWNER/ADMIN
3. Re-generar token (los actuales seguirán con scope correcto)
4. Probar `python ads_probar_api_write.py` (debería pasar a 200)

Si solo C3 es admin del advertiser pero está marcado como VIEWER, puede ser un bug de la plataforma. Soporte ML: https://www.mercadolibre.cl/ayuda
