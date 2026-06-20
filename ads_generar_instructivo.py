"""
Genera ads_instructivo_manual.md con la lista exacta de acciones para hacer
manualmente en la UI de Mercado Ads. Usa los IDs/títulos/cifras reales del Excel.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
XLSX = ROOT / "auditoria_ads_c3_2026-05-24.xlsx"
OUT_MD = ROOT / "ads_instructivo_manual.md"
OUT_PAUSAR_TXT = ROOT / "ads_items_pausar.txt"

CID = 357141159

df_all = pd.read_excel(XLSX, sheet_name="2. Items (por gasto)")
df = df_all[df_all["Campaign ID"] == CID].copy()
sin_clicks_all = pd.read_excel(XLSX, sheet_name="6. Sin clicks 7d")
sin_clicks = sin_clicks_all[sin_clicks_all["Campaign ID"] == CID].copy()
mid_all = pd.read_excel(XLSX, sheet_name="5. Con clicks sin venta")
mid = mid_all[mid_all["Campaign ID"] == CID].copy()

# Filtros para las acciones
ESPEJOS_TOP = ["MLC1754361903", "MLC1754550537"]
CPC_ALTO = "MLC3779856474"
TOP_ROAS = ["MLC1306255939", "MLC1367027081", "MLC3779834584", "MLC3767800412"]
AGREGAR = "MLC3779796948"

espejos = df[df["Item ID"].isin(ESPEJOS_TOP)].sort_values("Cost 7d CLP", ascending=False)
cpc_alto = df[df["Item ID"] == CPC_ALTO]
top_roas = df[df["Item ID"].isin(TOP_ROAS)].sort_values("ROAS (rev/cost)", ascending=False)
sin_clicks_solo_active = sin_clicks[sin_clicks["Status"] == "active"] if "Status" in sin_clicks.columns else sin_clicks
mid_sin_venta = mid[mid["Item ID"].isin(mid["Item ID"])].sort_values("Cost 7d CLP", ascending=False)

# Items pausados (ya están en paused, ignorarlos en limpieza)
ya_pausados = df[df["Status"] == "paused"]

ahorro_total_top3 = espejos["Cost 7d CLP"].sum() + cpc_alto["Cost 7d CLP"].sum()


def row_md(r):
    return f"- `{r['Item ID']}` — {r['Título'][:60]}  \n  Precio ${int(r['Precio']):,} · Clicks 7d: {int(r['Clicks 7d'])} · Cost: ${int(r['Cost 7d CLP']):,} · CPC: ${int(r['CPC promedio']):,}  \n  Permalink: {r['Permalink']}"


md = []
md.append(f"# Instructivo manual — Optimización Mercado Ads C3")
md.append(f"")
md.append(f"**Fecha**: 2026-05-24  ")
md.append(f"**Cuenta**: C3 (NOVAGRIFERIAS3, user_id 1194418785)  ")
md.append(f"**Advertiser**: 79197 (JOSERUBEN2)  ")
md.append(f"**Campaña**: Campaña Mayo (id `357141159`) — período aprendizaje termina **2026-05-28**")
md.append(f"")
md.append(f"---")
md.append(f"")
md.append(f"## Por qué este instructivo es manual y no automatizado")
md.append(f"")
md.append(f"Probé exhaustivamente la API ML Ads con los 4 tokens (`tokens_cuenta1.json`, `tokens_cuenta2.json`, `tokens_cuenta3.json`, `tokens_joseruben2.json`):")
md.append(f"")
md.append(f"| Endpoint | Método | Resultado |")
md.append(f"|---|---|---|")
md.append(f"| `/advertising/advertisers/{{aid}}/product_ads/items` | PUT | **401** \"User does not have permission to write\" |")
md.append(f"| 13 variantes alternativas (POST/PATCH, distintas URLs) | varios | 404 (no existen) |")
md.append(f"")
md.append(f"Verifiqué también con tokens C1 y C2 (sus respectivos advertisers 78985 y 79006) — **también 401**. El bloqueo es sistémico: los 3 usuarios ML están como VIEWER en sus advertisers, no como OWNER/ADMIN. Esto solo se cambia desde la UI por un admin del advertiser. Ver `ads_probar_api_write.py`, `ads_probar_c1_c2.py` y `data/auditoria/ads_probar_api_write_log.json` para detalle.")
md.append(f"")
md.append(f"Para automatizar via Playwright también descubrí que la URL real del panel es **`https://ads.mercadolibre.cl/productAds`** (no la del prompt original). Las sesiones guardadas en `storage_C3.json` no cubren ese subdominio — requiere login fresco en `ads.mercadolibre.cl`. Si querés que prepare un Playwright con login interactivo, decime y lo armo.")
md.append(f"")
md.append(f"---")
md.append(f"")
md.append(f"## ACCIÓN 1 — Seguras hoy (no reinician aprendizaje)")
md.append(f"")
md.append(f"**Ahorro estimado semanal: ${ahorro_total_top3:,.0f} CLP** (solo top 3 items abajo)")
md.append(f"")
md.append(f"### 1A. Pausar 2 espejos LED top-gastadores con 0 ventas")
md.append(f"")
md.append(f"**Tiempo estimado: 3 minutos**")
md.append(f"")
for _, r in espejos.iterrows():
    md.append(row_md(r))
    md.append(f"")
md.append(f"**Cómo**:")
md.append(f"")
md.append(f"1. Abrí Chrome y andá a https://ads.mercadolibre.cl/productAds")
md.append(f"2. Logueate con C3 (NOVAGRIFERIAS3, importadoravicttorino1@gmail.com)")
md.append(f"3. Andá a la campaña **\"Campaña Mayo\"** (id 357141159)")
md.append(f"4. En la lista de items, buscá por ID o título: `MLC1754361903` y `MLC1754550537`")
md.append(f"5. Toggle de estado: activo → pausado")
md.append(f"")
md.append(f"### 1B. Pausar item con CPC desorbitado")
md.append(f"")
md.append(f"**Tiempo estimado: 1 minuto**")
md.append(f"")
for _, r in cpc_alto.iterrows():
    md.append(row_md(r))
    md.append(f"")
md.append(f"**Por qué**: 24 clicks a $361 CPC, 0 ventas. CPC promedio de la campaña es ~$106. Este item está \"comiendo\" presupuesto. Pausar mientras evaluamos si el precio o título tienen problema.")
md.append(f"")
md.append(f"### 1C. Pausar items sin clicks 7d (limpieza masiva)")
md.append(f"")
md.append(f"Hay **{len(sin_clicks_solo_active)} items activos sin un solo click en 7 días**. No están aportando, pero ocupan slot en la campaña y diluyen el aprendizaje.")
md.append(f"")
md.append(f"**Recomendación**: pausar todos.  ")
md.append(f"**Tiempo estimado**: 15-30 min (depende si la UI permite multiselección).")
md.append(f"")
md.append(f"📎 Lista completa de IDs para pausar: archivo `ads_items_pausar.txt` (un Item ID por línea, copy-paste a la UI).")
md.append(f"")
md.append(f"Top 10 de la lista (resto en el .txt):")
md.append(f"")
for _, r in sin_clicks_solo_active.head(10).iterrows():
    md.append(f"- `{r['Item ID']}` — {r['Título'][:55]} (precio ${int(r['Precio']):,})")
md.append(f"")
md.append(f"### 1D. Agregar 1 item nuevo a la campaña")
md.append(f"")
md.append(f"**Tiempo estimado: 2 minutos**")
md.append(f"")
md.append(f"- `{AGREGAR}` — Pack 80x44 Secador Derecho + Llave Monomando")
md.append(f"  - Razón: histórico de ventas en ML pero NO está en la campaña actual")
md.append(f"  - Bid sugerido: **$2.352/click** (puede ajustar la UI automáticamente al agregar)")
md.append(f"")
md.append(f"**Cómo**: en el editor de campaña → \"Agregar productos\" → buscar por ID → confirmar bid.")
md.append(f"")
md.append(f"---")
md.append(f"")
md.append(f"## ACCIÓN 2 — Esperar al 2026-05-28 (post aprendizaje)")
md.append(f"")
md.append(f"⚠️ **NO HACER ANTES DEL 28**. Estos cambios reinician el período de aprendizaje y harían perder la calibración que la campaña ya tiene (ROAS 8.41x sobre target 4.9x).")
md.append(f"")
md.append(f"### 2A. Subir bid +30-50% en top 4 ROAS")
md.append(f"")
md.append(f"Items subutilizados — alto ROAS con pocos clicks. Subiéndoles el bid los hacemos competir más fuerte por impresión.")
md.append(f"")
for _, r in top_roas.iterrows():
    sugerido = "+50%" if r["ROAS (rev/cost)"] > 30 else "+30%"
    md.append(f"- `{r['Item ID']}` — {r['Título'][:60]}  ")
    md.append(f"  ROAS: **{r['ROAS (rev/cost)']:.2f}x** · Clicks 7d: {int(r['Clicks 7d'])} · Cost: ${int(r['Cost 7d CLP']):,} · CPC: ${int(r['CPC promedio']):,}  ")
    md.append(f"  → **Subir bid {sugerido}**")
    md.append(f"")
md.append(f"### 2B. Bajar bid -50% en items con tráfico sin venta")
md.append(f"")
md.append(f"Items que reciben clicks pero no convierten. Bajar bid reduce gasto sin perder presencia.")
md.append(f"")
md.append(f"⚠️ Excluye los que ya pausaste en Acción 1 (2 espejos LED + CPC alto).")
md.append(f"")
restantes_mid = mid_sin_venta[~mid_sin_venta["Item ID"].isin(ESPEJOS_TOP + [CPC_ALTO])]
for _, r in restantes_mid.head(8).iterrows():
    md.append(f"- `{r['Item ID']}` — {r['Título'][:60]}  ")
    md.append(f"  Clicks 7d: {int(r['Clicks 7d'])} · Cost: ${int(r['Cost 7d CLP']):,} · CPC: ${int(r['CPC promedio']):,} · ROAS 0")
    md.append(f"  → **Bajar bid -50%**")
    md.append(f"")
md.append(f"### 2C. Esperar 7 días más sobre items con precio bajado")
md.append(f"")
md.append(f"- `MLC1893675967` (precio bajó de $84.624 a $76.000 el 2026-05-23)  ")
md.append(f"  Esperar a ver si el nuevo precio empieza a convertir antes de tocar el bid.")
md.append(f"")
md.append(f"---")
md.append(f"")
md.append(f"## CHECKLIST POST-EJECUCIÓN")
md.append(f"")
md.append(f"Después de hacer los cambios manuales en la UI, ejecutar:")
md.append(f"")
md.append(f"```")
md.append(f"python auditoria_ads_c3.py")
md.append(f"```")
md.append(f"")
md.append(f"Esto regenera el Excel con las métricas actualizadas. Compará:")
md.append(f"- Items con clicks 7d (debería bajar — ya pausaste los que no aportaban)")
md.append(f"- Cost total 7d (debería bajar)")
md.append(f"- ROAS campaña (debería mantenerse o mejorar)")
md.append(f"")
md.append(f"---")
md.append(f"")
md.append(f"## SI QUERÉS DESBLOQUEAR LA API EN EL FUTURO")
md.append(f"")
md.append(f"Para que C3 pueda escribir via API, hay que cambiar el rol en la plataforma Ads:")
md.append(f"")
md.append(f"1. En `https://ads.mercadolibre.cl/productAds` → Configuración → Usuarios / Equipo")
md.append(f"2. Encontrar `NOVAGRIFERIAS3` y promoverlo de VIEWER a OWNER/ADMIN")
md.append(f"3. Re-generar token (los actuales seguirán con scope correcto)")
md.append(f"4. Probar `python ads_probar_api_write.py` (debería pasar a 200)")
md.append(f"")
md.append(f"Si solo C3 es admin del advertiser pero está marcado como VIEWER, puede ser un bug de la plataforma. Soporte ML: https://www.mercadolibre.cl/ayuda")
md.append(f"")

OUT_MD.write_text("\n".join(md), encoding="utf-8")
print(f"\nGenerado: {OUT_MD}")

# Lista plana de IDs a pausar (para copy-paste)
ids_pausar = list(sin_clicks_solo_active["Item ID"]) + ESPEJOS_TOP + [CPC_ALTO]
OUT_PAUSAR_TXT.write_text("\n".join(ids_pausar), encoding="utf-8")
print(f"Lista IDs pausar ({len(ids_pausar)} items): {OUT_PAUSAR_TXT}")
print(f"\nResumen:")
print(f"  Espejos LED a pausar: 2")
print(f"  CPC alto a pausar:    1")
print(f"  Sin clicks a pausar:  {len(sin_clicks_solo_active)}")
print(f"  Item a agregar:       1 ({AGREGAR})")
print(f"  Total acciones HOY:   {len(ids_pausar)+1}")
print(f"  Ahorro estimado:      ${ahorro_total_top3:,.0f}/sem (solo top 3)")
print(f"\nAcciones post-28-mayo:")
print(f"  Subir bid: 4 items")
print(f"  Bajar bid: {len(restantes_mid)} items")
