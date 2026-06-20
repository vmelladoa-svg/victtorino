"""
Reclasifica G3 con criterio GLOBAL (3 cuentas):

- Cada item se agrupa con sus "hermanos" según:
   * Mismo catalog_product_id, O
   * Mismo SKU (seller_custom_field), O
   * Mismo título normalizado
- Para el grupo (producto agregado), se suman: visitas 30d, ventas 180d, ventas históricas

Reclasificación:
  G3-VERDADERO  = el PRODUCTO no tiene actividad en NINGUNA cuenta
                  (visitas 30d = 0 EN TODAS, ventas 180d = 0 EN TODAS,
                   ventas históricas = 0 EN TODAS)
  G3-CANIBALIZADO = la publicación local está muerta pero su hermano
                    en otra cuenta SÍ tiene actividad/ventas

Output: reclasificacion_g3_global_<fecha>.xlsx
"""
import json
import pickle
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
ENRICHMENT = ROOT / "data" / "auditoria" / "catalog_enrichment_2026-05-24.json"
OUT = ROOT / f"reclasificacion_g3_global_{date.today().isoformat()}.xlsx"


def clasif(r):
    v = r["Visitas30d"]; s = r["Vendidos180d"]
    if s >= 3 or (s >= 1 and v >= 20): return "G1"
    if (1 <= s <= 2 and v < 20) or (v >= 10 and s == 0): return "G2"
    return "G3"


def normalize(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    snapshots = data["snapshots"]
    enrich = json.loads(ENRICHMENT.read_text(encoding="utf-8"))

    # Enriquecer
    df["NormTitle"] = df["Título"].apply(normalize)
    df["CatalogPID"] = df["ItemID"].map(lambda i: enrich.get(i, {}).get("catalog_product_id"))
    df["Grupo_local"] = df.apply(clasif, axis=1)

    # SKU desde snapshot crudo
    sku_map = {}
    sold_hist_map = {}
    for c in ("C1", "C2", "C3"):
        for it in snapshots[c]["items"]:
            if it.get("status") == "active":
                sku = (it.get("seller_custom_field") or "").strip().upper()
                sku_map[it["id"]] = sku
                sold_hist_map[it["id"]] = it.get("sold_quantity", 0) or 0
    df["SKU"] = df["ItemID"].map(sku_map)
    df["SoldHistorico"] = df["ItemID"].map(sold_hist_map)

    # ===== Agrupar por PRODUCTO (catalog_pid, SKU o título) =====
    # Asignar product_group_id: el más estable es catalog_pid, después SKU, después norm_title
    def product_key(r):
        if r["CatalogPID"]: return f"cpid:{r['CatalogPID']}"
        if r["SKU"]: return f"sku:{r['SKU']}"
        if r["NormTitle"]: return f"tit:{r['NormTitle']}"
        return f"id:{r['ItemID']}"
    df["ProductKey"] = df.apply(product_key, axis=1)

    # Métricas agregadas por producto
    agregados = df.groupby("ProductKey").agg(
        Items_en_grupo=("ItemID", "count"),
        Cuentas=("Cuenta", lambda x: ",".join(sorted(set(x)))),
        Visitas30d_total=("Visitas30d", "sum"),
        Vendidos180d_total=("Vendidos180d", "sum"),
        SoldHistorico_total=("SoldHistorico", "sum"),
        Stock_total=("Stock", "sum"),
    ).reset_index()

    df = df.merge(agregados, on="ProductKey", how="left")

    # ===== Reclasificación =====
    def reclasif(r):
        if r["Grupo_local"] != "G3":
            return r["Grupo_local"]  # no toco G1/G2
        # G3 local. Chequear si el producto (grupo) tiene actividad en ALGUNA cuenta
        if (r["Visitas30d_total"] == 0 and r["Vendidos180d_total"] == 0
                and r["SoldHistorico_total"] == 0):
            return "G3-VERDADERO"
        return "G3-CANIBALIZADO"

    df["Grupo_global"] = df.apply(reclasif, axis=1)

    # Stats
    print(f"Total items activos: {len(df)}")
    print(f"\nDistribución por Grupo_global:")
    print(df["Grupo_global"].value_counts())
    print(f"\nG3-VERDADERO: items donde el PRODUCTO no se mueve en NINGUNA cuenta")
    print(f"G3-CANIBALIZADO: items locales muertos pero hay hermano vendiendo")

    # Detalle por cuenta
    print(f"\nDistribución por cuenta:")
    for c in ("C1", "C2", "C3"):
        sub = df[df["Cuenta"] == c]
        for g in ("G1", "G2", "G3-VERDADERO", "G3-CANIBALIZADO"):
            n = int((sub["Grupo_global"] == g).sum())
            print(f"  {c} - {g}: {n}")
        print()

    # ===== Excel =====
    cols = ["Cuenta", "ItemID", "Título", "Grupo_local", "Grupo_global",
            "ProductKey", "Items_en_grupo", "Cuentas",
            "Visitas30d", "Vendidos180d", "SoldHistorico",
            "Visitas30d_total", "Vendidos180d_total", "SoldHistorico_total",
            "Stock", "Stock_total", "Precio", "ListingType", "HealthCalc",
            "Permalink"]
    df_out = df[cols].sort_values(["Cuenta", "Grupo_global", "SoldHistorico_total"],
                                  ascending=[True, True, False])

    # G3-VERDADERO subset (estos sí se pueden republicar sin canibalizar)
    g3v = df[df["Grupo_global"] == "G3-VERDADERO"].copy()
    g3v_stock_alto = g3v[g3v["Stock"] >= 5].sort_values("Stock", ascending=False)
    g3v_stock_bajo = g3v[g3v["Stock"] < 5]

    # G3-CANIBALIZADO subset (PAUSAR, no republicar)
    g3c = df[df["Grupo_global"] == "G3-CANIBALIZADO"].copy()
    # Para cada g3-canibalizado, identificar quién es el "ganador" en su grupo
    rows_canib = []
    for pk, grupo in df.groupby("ProductKey"):
        muertos = grupo[grupo["Grupo_global"] == "G3-CANIBALIZADO"]
        if muertos.empty: continue
        # El ganador es el que más vendió (180d primero, luego histórico)
        ganador = grupo.sort_values(["Vendidos180d", "SoldHistorico"], ascending=False).iloc[0]
        for _, m in muertos.iterrows():
            rows_canib.append({
                "Cuenta": m["Cuenta"], "ItemID": m["ItemID"],
                "Título": m["Título"], "Stock": int(m["Stock"]),
                "Precio": int(m["Precio"]),
                "Ganador Cuenta": ganador["Cuenta"], "Ganador ItemID": ganador["ItemID"],
                "Ganador vendió 180d": int(ganador["Vendidos180d"]),
                "Ganador histórico": int(ganador["SoldHistorico"]),
                "Producto compartido en": grupo["Cuenta"].nunique(),
                "Accion sugerida": "PAUSAR — concentrar tráfico en ganador",
                "Permalink": m["Permalink"],
            })
    df_canib = pd.DataFrame(rows_canib).sort_values(["Ganador histórico"], ascending=False)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        # Hoja 0: resumen
        resumen = df.groupby(["Cuenta", "Grupo_global"]).size().unstack(fill_value=0).reset_index()
        resumen.to_excel(writer, sheet_name="0. Resumen por cuenta", index=False)
        df_out.to_excel(writer, sheet_name="1. Todas reclasificadas", index=False)
        g3v_stock_alto.to_excel(writer, sheet_name="2. G3-VERDADERO stock≥5", index=False)
        g3v_stock_bajo.to_excel(writer, sheet_name="3. G3-VERDADERO stock<5", index=False)
        df_canib.to_excel(writer, sheet_name="4. G3-CANIBALIZADO (pausar)", index=False)

    print(f"\nOK Excel: {OUT}")
    print(f"\n=== Recomendaciones derivadas ===")
    print(f"G3-VERDADERO con stock ≥5 → candidatos REALES a republicar: {len(g3v_stock_alto)}")
    print(f"G3-VERDADERO con stock <5 → candidatos a PAUSAR: {len(g3v_stock_bajo)}")
    print(f"G3-CANIBALIZADO (cualquier stock) → PAUSAR para concentrar en ganador: {len(g3c)}")


if __name__ == "__main__":
    main()
