"""
Lee el Excel `auditoria_ads_c3_2026-05-24.xlsx` y extrae las listas EXACTAS
para el instructivo manual:
  1. Items a PAUSAR (seguro hoy, no reinicia aprendizaje):
     - 2 espejos LED top-gastadores con 0 ventas
     - 1 item con CPC desorbitado (MLC3779856474)
     - 116 items sin clicks 7d (limpieza)
  2. Items a SUBIR BID +30-50% (post 28-mayo, top 4 ROAS)
  3. Items a BAJAR BID -50% (post 28-mayo, mid sin venta)
  4. Item a AGREGAR (MLC3779796948)
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
XLSX = ROOT / "auditoria_ads_c3_2026-05-24.xlsx"
OUT_JSON = ROOT / "data" / "auditoria" / "ads_instructivo_listas.json"
OUT_MD = ROOT / "ads_instructivo_manual.md"

# Hojas que tiene el Excel
SHEETS = pd.ExcelFile(XLSX).sheet_names
print(f"Hojas: {SHEETS}\n")

# Hoja principal: items por gasto
df_all = pd.read_excel(XLSX, sheet_name="2. Items (por gasto)")
# Filtrar solo Campaña Mayo
df = df_all[df_all["Campaign ID"] == 357141159].copy()
print(f"Items totales en Campaña Mayo: {len(df)}")
print(f"Columnas: {df.columns.tolist()}\n")

# Detectar columna del status (puede tener un nombre)
df_active = df[df["Status"] == "active"].copy() if "Status" in df.columns else df.copy()
print(f"Items active: {len(df_active)}")

# ====== ACCIONES SEGURAS HOY ======

# 1A. Espejos LED top-gastadores con 0 ventas (definidos en prompt)
espejos_targets = ["MLC1754361903", "MLC1754550537"]
espejos = df[df["Item ID"].isin(espejos_targets)].copy()

# 1B. Item con CPC desorbitado
cpc_alto_id = "MLC3779856474"
cpc_alto = df[df["Item ID"] == cpc_alto_id].copy()

# 1C. Sin clicks 7d (de la hoja "6. Sin clicks 7d" si existe, sino calcular)
if "6. Sin clicks 7d" in SHEETS:
    _sc_all = pd.read_excel(XLSX, sheet_name="6. Sin clicks 7d")
    sin_clicks = _sc_all[_sc_all["Campaign ID"] == 357141159].copy()
else:
    sin_clicks = df[df["Clicks 7d"] == 0].copy()
print(f"Items sin clicks 7d: {len(sin_clicks)}")

# ====== ACCIONES POST 28-MAYO ======

# 2. Top 4 ROAS para subir bid (del prompt)
top_roas_ids = ["MLC1306255939", "MLC1367027081", "MLC3779834584", "MLC3767800412"]
top_roas = df[df["Item ID"].isin(top_roas_ids)].copy()

# 3. Bajar bid: mid sin venta (de hoja 5 si existe)
if "5. Con clicks sin venta" in SHEETS:
    _msv_all = pd.read_excel(XLSX, sheet_name="5. Con clicks sin venta")
    mid_sin_venta = _msv_all[_msv_all["Campaign ID"] == 357141159].copy()
else:
    mid_sin_venta = df[(df["Clicks 7d"] >= 5) & (df["Ventas directas (atribuidas)"] == 0) & (df["Cost 7d CLP"] < 700)].copy()

# ====== AGREGAR ======
agregar_id = "MLC3779796948"

# Build instructivo
ahorro_pausa_top = espejos["Cost 7d CLP"].sum() + cpc_alto["Cost 7d CLP"].sum() if not (espejos.empty and cpc_alto.empty) else 0

result = {
    "fecha_analisis": "2026-05-24",
    "ahorro_estimado_semanal_pausar_top3": int(ahorro_pausa_top),

    "1_seguras_hoy": {
        "1a_espejos_top_gastadores": espejos[["Item ID", "Título", "Clicks 7d", "Cost 7d CLP", "Precio", "Permalink"]].to_dict("records") if not espejos.empty else [],
        "1b_cpc_desorbitado": cpc_alto[["Item ID", "Título", "Clicks 7d", "Cost 7d CLP", "CPC promedio", "Precio", "Permalink"]].to_dict("records") if not cpc_alto.empty else [],
        "1c_sin_clicks_7d_count": len(sin_clicks),
        "1c_sin_clicks_7d_top10": sin_clicks.head(10)[["Item ID", "Título", "Precio"]].to_dict("records") if not sin_clicks.empty else [],
        "1d_agregar_item": {
            "item_id": agregar_id,
            "razon": "Históricamente vende, no está en la campaña",
            "bid_sugerido_clp": 2352,
        },
    },

    "2_esperar_28_mayo": {
        "2a_subir_bid_top4_roas": top_roas[["Item ID", "Título", "Clicks 7d", "Cost 7d CLP", "Ventas directas (atribuidas)", "ROAS (rev/cost)"]].to_dict("records") if not top_roas.empty else [],
        "2b_bajar_bid_mid_sin_venta": mid_sin_venta.head(10)[["Item ID", "Título", "Clicks 7d", "Cost 7d CLP"]].to_dict("records") if not mid_sin_venta.empty else [],
        "2c_esperar_precio_bajado": ["MLC1893675967"],
    },
}

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str))
print(f"\nJSON: {OUT_JSON}")
print(f"\n=== RESUMEN ===")
print(f"Espejos top-gastadores: {len(espejos)} items, ${espejos['Cost 7d CLP'].sum():,.0f}/sem")
print(f"CPC desorbitado: {len(cpc_alto)} items, ${cpc_alto['Cost 7d CLP'].sum():,.0f}/sem")
print(f"Sin clicks 7d: {len(sin_clicks)} items (limpieza)")
print(f"Top 4 ROAS para subir bid: {len(top_roas)} items")
print(f"Mid sin venta para bajar bid: {len(mid_sin_venta)} items")
