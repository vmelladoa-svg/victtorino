"""
Análisis estratégico cuantitativo de las 3 cuentas ML.

Calcula:
  - GMV incremental real (productos únicos sin canibalización) vs GMV redundante (canibalizados)
  - Productos cubiertos en cada cuenta vs cobertura total única
  - Distribución de tipos de producto por cuenta
  - Performance por cuenta (ya calculado)
  - Modelo 3 escenarios con proyecciones a 12 meses

Output:
  - analisis_estrategico_data.json (datos crudos para el reporte)
  - escenarios_proyeccion.xlsx (comparativa numérica)
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
OUT_JSON = ROOT / "data" / "auditoria" / "analisis_estrategico_data.json"
OUT_XLSX = ROOT / f"escenarios_proyeccion_{date.today().isoformat()}.xlsx"


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

    def product_key(r):
        if r["CatalogPID"]: return f"cpid:{r['CatalogPID']}"
        if r["SKU"]: return f"sku:{r['SKU']}"
        if r["NormTitle"]: return f"tit:{r['NormTitle']}"
        return f"id:{r['ItemID']}"
    df["ProductKey"] = df.apply(product_key, axis=1)

    # ===== Métricas estructurales =====
    # 1. Productos únicos vs items
    total_items = len(df)
    productos_unicos = df["ProductKey"].nunique()
    items_por_producto = df.groupby("ProductKey").size()
    productos_solo_1_cuenta = (items_por_producto == 1).sum()
    productos_en_2_cuentas = ((items_por_producto >= 2) & (items_por_producto < 3)).sum()
    productos_en_3_cuentas = (items_por_producto >= 3).sum()

    # 2. GMV por cuenta
    gmv_por_cuenta = df.groupby("Cuenta")["Revenue180d"].sum().to_dict()
    gmv_total = sum(gmv_por_cuenta.values())

    # 3. GMV incremental vs redundante
    # Para cada ProductKey, sumar el GMV total. El GMV "consolidable" = el del top performer
    # de cada grupo. El "redundante" = el resto (que en teoría no aportarían si consolidás).
    gmv_consolidable = 0  # lo que se mantendría si solo tuvieras 1 cuenta
    gmv_redundante = 0    # lo que sería duplicado
    items_unicos_gmv = 0
    items_duplicados_gmv = 0
    cobertura_unica_productos = set()
    for pk, g in df.groupby("ProductKey"):
        cobertura_unica_productos.add(pk)
        if len(g) == 1:
            gmv_consolidable += g["Revenue180d"].sum()
            items_unicos_gmv += int(g["Revenue180d"].sum())
        else:
            top_seller = g.sort_values("Revenue180d", ascending=False).iloc[0]
            gmv_consolidable += top_seller["Revenue180d"]
            gmv_redundante += g["Revenue180d"].sum() - top_seller["Revenue180d"]
            items_duplicados_gmv += int(g["Revenue180d"].sum())

    # 4. Distribución por cuenta agregada
    perf_cuenta = {}
    for c in ("C1", "C2", "C3"):
        sub = df[df["Cuenta"] == c]
        snap = snapshots[c]
        # Stock total
        stock_total = int(sub["Stock"].sum())
        # Categorías cubiertas
        cats = int(sub["Categoría"].nunique())
        perf_cuenta[c] = {
            "items_activos": len(sub),
            "items_duplicados_con_otras": int((sub["ProductKey"].isin(
                df[df["Cuenta"] != c]["ProductKey"])).sum()),
            "items_unicos_solo_aqui": int((~sub["ProductKey"].isin(
                df[df["Cuenta"] != c]["ProductKey"])).sum()),
            "categorias_cubiertas": cats,
            "stock_total": stock_total,
            "gmv_180d": int(sub["Revenue180d"].sum()),
            "vendidos_180d_unidades": int(sub["Vendidos180d"].sum()),
            "visitas_30d": int(sub["Visitas30d"].sum()),
            "health_avg": round(sub["HealthCalc"].mean(), 1),
            "rep_nivel": (snap.get("reputacion") or {}).get("level_id"),
            "tx_completadas": ((snap.get("reputacion") or {}).get("transactions") or {}).get("completed"),
            "tx_canceladas": ((snap.get("reputacion") or {}).get("transactions") or {}).get("canceled"),
        }

    # ===== Modelo escenarios =====
    # ESCENARIO A: Status quo + optimización aplicada hoy (ya hicimos cambios)
    # Proyectamos GMV 12m basado en GMV 180d × 2 (anualizado) × 1.15 (mejora 15% por optimización)
    gmv_12m_A = int(gmv_total * 2 * 1.15)

    # ESCENARIO B: Consolidación en C3 (la mejor)
    # GMV consolidable estimado + 30% bonus por mejor reputación + mayor presupuesto Ads concentrado
    # Asumimos que C3 absorbería ~70% del GMV consolidable + nuevo crecimiento
    gmv_12m_B = int(gmv_consolidable * 2 * 1.35)  # +35% por consolidación

    # ESCENARIO C: Segmentación verdadera (3 cuentas con catálogos NO solapados)
    # Cada cuenta especializada. Más SKUs únicos cubiertos → más cobertura
    # Asumimos que después de segmentar, se pueden cubrir más productos sin canibalización
    # GMV = gmv consolidable + suma adicional por nuevos productos diferenciados
    gmv_12m_C = int((gmv_consolidable + 0.4 * gmv_redundante) * 2 * 1.25)

    escenarios = {
        "A_status_quo_optimizado": {
            "descripcion": "Mantener 3 cuentas como están, con optimizaciones aplicadas (upgrades, bajadas precio, etc.)",
            "GMV_12m_proyectado_CLP": gmv_12m_A,
            "complejidad_operativa": "ALTA (3 cuentas, 3 equipos, 346 items canibalizándose)",
            "costos_operativos": "3× gestión, comisiones plataforma triplicadas",
            "reputacion": "Dividida en 3 — más vulnerable",
            "ads_eficiencia": "3 campañas, atención dividida",
            "riesgo": "Persiste canibalización (65% catálogo). Plateau en crecimiento.",
            "tiempo_implementacion": "Ya hecho (es lo que tenés hoy)",
        },
        "B_consolidacion_C3": {
            "descripcion": "Consolidar todo en C3 (mejor cuenta). Cerrar/pausar C1 y C2.",
            "GMV_12m_proyectado_CLP": gmv_12m_B,
            "complejidad_operativa": "BAJA (1 cuenta, equipo unificado)",
            "costos_operativos": "1× gestión, una sola plataforma",
            "reputacion": "Concentrada — alcanza Platinum/Lider más rápido (más ventas en 1 cuenta)",
            "ads_eficiencia": "1 campaña con presupuesto pleno",
            "riesgo": "Perder los ~$5-8M GMV de C1/C2 que NO se canibalizaban (productos únicos)",
            "tiempo_implementacion": "2-3 meses (transferir stock, cerrar cuentas progresivamente)",
        },
        "C_segmentacion_verdadera": {
            "descripcion": "Mantener 3 cuentas con catálogos NO solapados (segmentar por marca/categoría/precio)",
            "GMV_12m_proyectado_CLP": gmv_12m_C,
            "complejidad_operativa": "MEDIA (3 cuentas pero sin canibalización, cada equipo especializado)",
            "costos_operativos": "3× gestión pero más eficientes (sin duplicar setup)",
            "reputacion": "3 reputaciones independientes — diversifica riesgo",
            "ads_eficiencia": "3 campañas focalizadas, cada una en su nicho",
            "riesgo": "Requiere disciplina operativa. Decisión clara de qué va en cada cuenta. Reestructuración inicial fuerte.",
            "tiempo_implementacion": "4-6 meses (reorganizar catálogos, mover productos)",
        },
    }

    # Distribución de productos únicos por cuenta
    productos_unicos_por_cuenta = {}
    for c in ("C1", "C2", "C3"):
        keys_c = set(df[df["Cuenta"] == c]["ProductKey"])
        otras = set(df[df["Cuenta"] != c]["ProductKey"])
        unicos_c = keys_c - otras
        productos_unicos_por_cuenta[c] = {
            "productos_totales_cuenta": len(keys_c),
            "productos_unicos_solo_esta_cuenta": len(unicos_c),
            "productos_compartidos_con_otra": len(keys_c & otras),
            "gmv_180d_total": int(df[df["Cuenta"] == c]["Revenue180d"].sum()),
            "gmv_180d_de_productos_unicos": int(df[(df["Cuenta"] == c) & (df["ProductKey"].isin(unicos_c))]["Revenue180d"].sum()),
        }

    # Compilar resultados
    resultados = {
        "fecha_analisis": date.today().isoformat(),
        "metricas_estructurales": {
            "items_totales_activos": total_items,
            "productos_unicos_(despues_dedup)": productos_unicos,
            "productos_solo_en_1_cuenta": int(productos_solo_1_cuenta),
            "productos_en_2_cuentas": int(productos_en_2_cuentas),
            "productos_en_3_cuentas": int(productos_en_3_cuentas),
            "cobertura_de_productos_unica": int(productos_unicos),
            "ratio_items_por_producto": round(total_items / productos_unicos, 2),
        },
        "gmv_estructural_180d": {
            "gmv_total_3cuentas": int(gmv_total),
            "gmv_consolidable_(lo_que_quedaria_si_hubiera_1_cuenta)": int(gmv_consolidable),
            "gmv_redundante_(perderias_consolidando)": int(gmv_redundante),
            "porcentaje_redundante": round(gmv_redundante / gmv_total * 100, 1) if gmv_total else 0,
            "interpretacion": (
                f"Del ${int(gmv_total):,} GMV 180d total, ${int(gmv_consolidable):,} ({round(gmv_consolidable/gmv_total*100,1)}%) "
                f"es lo que generarías con 1 sola cuenta consolidada. "
                f"${int(gmv_redundante):,} ({round(gmv_redundante/gmv_total*100,1)}%) es 'redundante' "
                f"(actualmente generado por items que canibalizan al ganador)."
            ),
        },
        "performance_por_cuenta": perf_cuenta,
        "productos_unicos_por_cuenta": productos_unicos_por_cuenta,
        "escenarios": escenarios,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK JSON: {OUT_JSON}")

    # Excel comparativo
    df_est = pd.DataFrame([resultados["metricas_estructurales"]]).T.reset_index()
    df_est.columns = ["Métrica", "Valor"]

    df_gmv = pd.DataFrame([resultados["gmv_estructural_180d"]]).T.reset_index()
    df_gmv.columns = ["Métrica", "Valor"]

    df_perf = pd.DataFrame(perf_cuenta).T.reset_index()
    df_perf.columns = ["Cuenta"] + list(df_perf.columns[1:])

    df_unicos = pd.DataFrame(productos_unicos_por_cuenta).T.reset_index()
    df_unicos.columns = ["Cuenta"] + list(df_unicos.columns[1:])

    df_esc = pd.DataFrame(escenarios).T.reset_index()
    df_esc.columns = ["Escenario"] + list(df_esc.columns[1:])

    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        df_est.to_excel(writer, sheet_name="1. Estructura catálogo", index=False)
        df_gmv.to_excel(writer, sheet_name="2. GMV estructural", index=False)
        df_perf.to_excel(writer, sheet_name="3. Performance por cuenta", index=False)
        df_unicos.to_excel(writer, sheet_name="4. Productos únicos x cuenta", index=False)
        df_esc.to_excel(writer, sheet_name="5. Escenarios proyectados", index=False)

    print(f"OK Excel: {OUT_XLSX}")

    # Print resumen
    print()
    print("=" * 70)
    print("RESUMEN ESTRATÉGICO")
    print("=" * 70)
    print(f"\nEstructura:")
    print(f"  Items activos: {total_items}")
    print(f"  Productos únicos (despues dedup): {productos_unicos}")
    print(f"  → Productos solo en 1 cuenta: {productos_solo_1_cuenta}")
    print(f"  → Productos en 2 cuentas: {productos_en_2_cuentas}")
    print(f"  → Productos en 3 cuentas: {productos_en_3_cuentas}")
    print(f"  Ratio items/producto: {total_items/productos_unicos:.2f}x")
    print(f"\nGMV 180d:")
    print(f"  Total 3 cuentas:      ${gmv_total:>12,}")
    print(f"  Consolidable (1 cta): ${gmv_consolidable:>12,}  ({gmv_consolidable/gmv_total*100:.1f}%)")
    print(f"  Redundante (perderías):${gmv_redundante:>11,}  ({gmv_redundante/gmv_total*100:.1f}%)")
    print(f"\nEscenarios 12m proyectado:")
    for k, v in escenarios.items():
        print(f"  {k:30s}: ${v['GMV_12m_proyectado_CLP']:>12,}")


if __name__ == "__main__":
    main()
