"""
Detecta issues estructurales del catálogo en las 3 cuentas:

1. Duplicados intra-cuenta (mismo título normalizado misma cuenta)
2. SKUs en >=2 cuentas (canibalización potencial entre nuestras cuentas)
3. Categorías débiles (health bajo en agregado)
4. AUTO-CANIBALIZACIÓN catálogo: mismo catalog_product_id en >=2 cuentas
   → competimos contra NOSOTROS MISMOS en el mismo producto del catálogo central
5. ITEMS EN CATÁLOGO sin buy box → perdiendo contra TERCEROS (152 items detectados, 0 ganando!)
6. Items mal categorizados (heurística)
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
OUT = ROOT / f"consultor_issues_{date.today().isoformat()}.xlsx"


def normalize(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    df["NormTitle"] = df["Título"].apply(normalize)
    enrich = json.loads(ENRICHMENT.read_text(encoding="utf-8"))

    # Agregar campos enrichment al df
    df["catalog_listing"] = df["ItemID"].map(lambda i: bool(enrich.get(i, {}).get("catalog_listing")))
    df["catalog_product_id"] = df["ItemID"].map(lambda i: enrich.get(i, {}).get("catalog_product_id"))
    df["buy_box_winner"] = df["ItemID"].map(lambda i: bool(enrich.get(i, {}).get("buy_box_winner")))
    df["family_name"] = df["ItemID"].map(lambda i: enrich.get(i, {}).get("family_name"))

    print(f"Total items: {len(df)}")
    print(f"  En catálogo central: {df['catalog_listing'].sum()}")
    print(f"  Con catalog_product_id: {df['catalog_product_id'].notna().sum()}")
    print(f"  Buy box winner: {df['buy_box_winner'].sum()}")

    # ============ 1. Duplicados intra-cuenta ============
    print("\n=== 1. Duplicados intra-cuenta ===")
    dup_intra = []
    for cuenta in ("C1", "C2", "C3"):
        sub = df[df["Cuenta"] == cuenta]
        for norm, g in sub.groupby("NormTitle"):
            if len(g) >= 2 and norm:
                for _, r in g.iterrows():
                    dup_intra.append({
                        "Cuenta": cuenta, "ItemID": r["ItemID"],
                        "Título": r["Título"], "Total duplicados": len(g),
                        "Precio": int(r["Precio"]), "Stock": int(r["Stock"]),
                        "Visitas30d": int(r["Visitas30d"]), "Vendidos180d": int(r["Vendidos180d"]),
                        "Health": int(r["HealthCalc"]),
                        "Recomendación": "Consolidar: mantener mejor performer, pausar el resto",
                        "Permalink": r["Permalink"],
                    })
    print(f"  Items duplicados intra-cuenta: {len(dup_intra)}")

    # ============ 2. SKUs compartidos entre cuentas ============
    print("\n=== 2. SKUs compartidos entre nuestras cuentas ===")
    compartidos = []
    for norm, g in df.groupby("NormTitle"):
        if not norm: continue
        cuentas = sorted(g["Cuenta"].unique())
        if len(cuentas) >= 2:
            sales = g.groupby("Cuenta")["Vendidos180d"].sum().to_dict()
            visits = g.groupby("Cuenta")["Visitas30d"].sum().to_dict()
            top = max(sales.values()) if sales else 0
            for _, r in g.iterrows():
                gap = top - r["Vendidos180d"]
                compartidos.append({
                    "Producto": (r["Título"] or "")[:55],
                    "Cuenta": r["Cuenta"], "ItemID": r["ItemID"],
                    "Cuentas con este SKU": ",".join(cuentas),
                    "Vendidos 180d esta": int(r["Vendidos180d"]),
                    "Top entre cuentas": int(top), "Brecha vs top": gap,
                    "Precio": int(r["Precio"]), "Visitas30d": int(r["Visitas30d"]),
                    "Health": int(r["HealthCalc"]), "Listing": r["ListingType"],
                    "Permalink": r["Permalink"],
                })
    print(f"  Casos: {len(compartidos)}")

    # ============ 3. AUTO-CANIBALIZACIÓN CATÁLOGO ============
    # Mismo catalog_product_id en >=2 cuentas = competimos contra nosotros mismos
    print("\n=== 3. AUTO-CANIBALIZACIÓN catálogo central (clave) ===")
    auto_canib = []
    by_cpid = df[df["catalog_product_id"].notna()].groupby("catalog_product_id")
    for cpid, g in by_cpid:
        if g["Cuenta"].nunique() >= 2:
            cuentas_lista = sorted(g["Cuenta"].unique())
            best_seller = g.sort_values("Vendidos180d", ascending=False).iloc[0]
            # Filas por cada item compitiendo
            for _, r in g.iterrows():
                es_ganador = r["ItemID"] == best_seller["ItemID"]
                auto_canib.append({
                    "Catalog Product ID": cpid,
                    "Producto": (r["Título"] or "")[:55],
                    "Cuenta": r["Cuenta"],
                    "ItemID": r["ItemID"],
                    "Cuentas compitiendo": ",".join(cuentas_lista),
                    "Precio": int(r["Precio"]),
                    "Listing": r["ListingType"],
                    "Stock": int(r["Stock"]),
                    "Visitas30d": int(r["Visitas30d"]),
                    "Vendidos180d": int(r["Vendidos180d"]),
                    "Buy Box?": "✓" if r["buy_box_winner"] else "—",
                    "¿Es el mejor de los nuestros?": "★ SÍ" if es_ganador else "no",
                    "Recomendación": (
                        "MANTENER (es nuestro best seller en este producto)" if es_ganador
                        else "PAUSAR/REDIRIGIR → no canibalizar al ganador"
                    ),
                    "Permalink": r["Permalink"],
                })
    print(f"  Auto-canibalización: {len(set(r['Catalog Product ID'] for r in auto_canib))} catalog_product_ids, {len(auto_canib)} items afectados")

    # ============ 4. COMPETENCIA EN CATÁLOGO vs TERCEROS ============
    # Items con catalog_listing=True donde NO somos buy box → perdemos contra externos
    print("\n=== 4. Compitiendo en catálogo contra TERCEROS ===")
    cat_externos = []
    en_catalogo = df[df["catalog_listing"] == True]
    for _, r in en_catalogo.iterrows():
        # ¿Este catalog_product_id solo aparece en una cuenta nuestra?
        cpid = r["catalog_product_id"]
        otras = df[df["catalog_product_id"] == cpid]
        nuestras_cuentas = otras["Cuenta"].nunique() if cpid else 1
        es_solo_nuestro = nuestras_cuentas == 1

        cat_externos.append({
            "Cuenta": r["Cuenta"], "ItemID": r["ItemID"],
            "Catalog Product ID": cpid or "—",
            "Producto": (r["Título"] or "")[:55],
            "Precio": int(r["Precio"]),
            "Listing": r["ListingType"],
            "Stock": int(r["Stock"]),
            "Visitas30d": int(r["Visitas30d"]),
            "Vendidos180d": int(r["Vendidos180d"]),
            "Health": int(r["HealthCalc"]),
            "Buy Box?": "✓ GANANDO" if r["buy_box_winner"] else "✗ PERDIENDO",
            "Solo nuestra cuenta en este catalog?": "Sí" if es_solo_nuestro else f"No, en {nuestras_cuentas} cuentas",
            "Razón probable pérdida": (
                "—" if r["buy_box_winner"]
                else "Precio o reputación de competencia" if r["Vendidos180d"] >= 1
                else "Posicionamiento bajo o ficha incompleta"
            ),
            "Acción para ganar buy box": (
                "Mantener" if r["buy_box_winner"]
                else "Bajar precio 5-10% + verificar envío rápido + completar atributos"
            ),
            "Permalink": r["Permalink"],
        })
    print(f"  Items en catálogo: {len(cat_externos)} | Ganando buy box: {sum(1 for x in cat_externos if 'GANANDO' in x['Buy Box?'])}")

    # ============ 5. Resumen estratégico catálogo ============
    estrat_resumen = pd.DataFrame([
        {"Métrica": "Items totales activos", "Valor": int(len(df))},
        {"Métrica": "Items en catálogo central (compiten contra externos)", "Valor": int(df['catalog_listing'].sum())},
        {"Métrica": "Items con catalog_product_id (vinculados)", "Valor": int(df['catalog_product_id'].notna().sum())},
        {"Métrica": "Items GANANDO buy box", "Valor": int(df['buy_box_winner'].sum())},
        {"Métrica": "Items PERDIENDO buy box (en catálogo, sin ganarlo)", "Valor": int(((df['catalog_listing']==True)&(df['buy_box_winner']==False)).sum())},
        {"Métrica": "Auto-canibalización: catalog_product_id en >=2 cuentas", "Valor": int(len(set(r['Catalog Product ID'] for r in auto_canib)))},
        {"Métrica": "Items en auto-canibalización", "Valor": int(len(auto_canib))},
        {"Métrica": "SKUs (título) compartidos entre cuentas", "Valor": int(len(set(r['Producto'] for r in compartidos)))},
        {"Métrica": "Items afectados por compartir título", "Valor": int(len(compartidos))},
    ])

    # ============ 6. Categorías ============
    cat_stats = df.groupby("Categoría").agg(
        Items=("ItemID", "count"),
        Health_avg=("HealthCalc", "mean"),
        Visitas_avg=("Visitas30d", "mean"),
        Vendidos_total=("Vendidos180d", "sum"),
        Sin_visitas=("Visitas30d", lambda x: (x == 0).sum()),
    ).round(1).reset_index()
    cat_stats["% Sin visitas"] = (cat_stats["Sin_visitas"] / cat_stats["Items"] * 100).round(1)
    cat_debiles = cat_stats[(cat_stats["Items"] >= 3) & (cat_stats["Health_avg"] < 50)].sort_values("Health_avg")
    print(f"  Categorías débiles: {len(cat_debiles)}")

    # Excel
    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        estrat_resumen.to_excel(writer, sheet_name="0. Resumen estratégico", index=False)
        pd.DataFrame(dup_intra).to_excel(writer, sheet_name="1. Duplicados intra-cuenta", index=False)
        pd.DataFrame(compartidos).to_excel(writer, sheet_name="2. SKUs compartidos", index=False)
        pd.DataFrame(auto_canib).sort_values("Catalog Product ID").to_excel(writer, sheet_name="3. AUTO-CANIBALIZACIÓN", index=False)
        pd.DataFrame(cat_externos).sort_values(["Buy Box?","Visitas30d"], ascending=[True,False]).to_excel(writer, sheet_name="4. Competencia vs TERCEROS", index=False)
        cat_stats.to_excel(writer, sheet_name="5. Stats categorías", index=False)
        cat_debiles.to_excel(writer, sheet_name="6. Categorías débiles", index=False)

    print(f"\nOK {OUT}")


if __name__ == "__main__":
    main()
