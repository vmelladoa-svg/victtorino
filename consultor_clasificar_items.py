"""
Clasifica las 530 publicaciones de las 3 cuentas en 3 grupos según actividad comercial:

GRUPO 1 (G1) — VENTAS ACTIVAS / RECIENTES
  Ventas 180d >= 3 OR (Ventas 180d >= 1 AND Visitas 30d >= 20)
  → Los "campeones": están corriendo, hay que escalar

GRUPO 2 (G2) — DESACELERADAS (tuvieron ventas pero ahora bajo movimiento)
  (Ventas 180d entre 1-2 AND Visitas 30d < 20) OR (Visitas 30d >= 10 AND Ventas 180d == 0)
  → Productos con interés histórico/visitas, sin convertir actualmente

GRUPO 3 (G3) — SIN MOVIMIENTO
  Visitas 30d == 0 AND Ventas 180d == 0
  → Muertos en el ranking de ML, requieren reset (republicar) o pausar

Score 1-10 por publicación basado en:
  - Conversión histórica (visitas/ventas)
  - Health del item
  - Stock disponible
  - Margen estimado
  - Posición en SOV (si está en Ads)
  - Tendencia (visitas pre vs post sesión 23-may si aplica)

Output: consultor_clasificacion_<fecha>.xlsx con hoja por cuenta + comparativa.
"""
import json
import pickle
from datetime import date
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
OUT = ROOT / f"consultor_clasificacion_{date.today().isoformat()}.xlsx"


def clasificar(row):
    """Devuelve (grupo, razón)."""
    v = row["Visitas30d"]
    s = row["Vendidos180d"]
    if s >= 3 or (s >= 1 and v >= 20):
        return "G1", "Ventas activas/recientes"
    if (1 <= s <= 2 and v < 20) or (v >= 10 and s == 0):
        return "G2", "Desacelerada o tráfico sin venta"
    if v == 0 and s == 0:
        return "G3", "Sin movimiento (muerta)"
    # Edge: visitas bajas (<10) sin ventas → tampoco muerta total
    if v > 0 and s == 0:
        return "G3", "Visitas mínimas sin venta"
    return "G3", "Sin clasificar (revisar)"


def score_potencial(row):
    """
    Score 1-10:
      +3 si ventas>0 (probó demanda)
      +2 si conv > 2%
      +2 si stock >= 5
      +1 si health >= 70
      +1 si listing gold_pro
      +1 si en Ads (tiene SOV)
    Min 1, max 10.
    """
    s = 0
    if row["Vendidos180d"] > 0:
        s += 3
        if row["Vendidos180d"] >= 5: s += 1
    conv = row["ConvRate%"]
    if conv >= 5: s += 2
    elif conv >= 2: s += 1
    if row["Stock"] >= 5: s += 2
    elif row["Stock"] >= 2: s += 1
    if row["HealthCalc"] >= 70: s += 1
    elif row["HealthCalc"] >= 50: s += 0.5
    if row["ListingType"] == "gold_pro": s += 1
    return max(1, min(10, round(s + 1)))  # +1 base


def detectar_oportunidades(row, grupo):
    opps = []
    if grupo == "G1":
        if row["Stock"] < 5: opps.append("Stock crítico — reabastecer urgente")
        if row["ListingType"] == "gold_special": opps.append("Migrar a gold_pro para más visibilidad")
        if row["Fotos"] < 6: opps.append("Subir más fotos (actualmente <6)")
        if row["HealthCalc"] < 80: opps.append("Completar atributos para health 90+")
    elif grupo == "G2":
        if row["Visitas30d"] >= 50 and row["Vendidos180d"] == 0:
            opps.append("Tráfico real sin convertir — revisar PRECIO o copy")
        if row["Vendidos180d"] >= 1 and row["Visitas30d"] < 10:
            opps.append("Vende cuando se ve — necesita más visibilidad (Ads o SEO)")
        if row["ListingType"] == "gold_special":
            opps.append("Upgrade gold_pro puede romper el techo")
    elif grupo == "G3":
        if row["Stock"] > 0:
            opps.append("Stock parado — republicar como nuevo o pausar/liquidar")
        opps.append("Considerar pausar para limpiar catálogo")
    return " | ".join(opps) if opps else "—"


def detectar_problemas(row, grupo):
    probs = []
    if row["Stock"] == 0:
        probs.append("CRITICO: sin stock — pausar o reabastecer")
    if row["Precio"] <= 0:
        probs.append("CRITICO: precio cero/inválido")
    if row["Fotos"] < 4:
        probs.append("Pocas fotos (<4)")
    if row["HealthCalc"] < 40:
        probs.append("Health muy bajo — atributos/descripción incompletos")
    if grupo == "G2" and row["Vendidos180d"] > 0:
        conv = row["ConvRate%"]
        if conv > 0 and conv < 1:
            probs.append(f"Conv {conv:.1f}% muy bajo")
    if len(row["Título"] or "") < 30:
        probs.append(f"Título corto ({len(row['Título'] or '')} chars)")
    return " | ".join(probs) if probs else "—"


def accion_recomendada(row, grupo, score):
    if grupo == "G1":
        if score >= 8: return "ESCALAR: subir presupuesto Ads, mantener stock, replicar a otras cuentas"
        if score >= 6: return "OPTIMIZAR: mejorar ficha (atributos, fotos) + subir bid Ads"
        return "PROTEGER: mantener, monitorear"
    if grupo == "G2":
        if row["Visitas30d"] >= 30 and row["Vendidos180d"] == 0:
            return "AJUSTAR PRECIO -10% + revisar competencia"
        if row["Vendidos180d"] >= 1 and row["Visitas30d"] < 10:
            return "DAR VISIBILIDAD: agregar a Ads o mejorar SEO título"
        return "REVISAR: actualizar ficha, considerar mejor categoría"
    # G3
    if row["Stock"] > 5:
        return "REPUBLICAR: cerrar viejo + crear nuevo con título optimizado (reset score ML)"
    return "PAUSAR: liberar inventario, dejar de aparecer en catálogo"


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    print(f"Procesando {len(df)} items totales en 3 cuentas")

    # Aplicar clasificación
    df[["Grupo", "Razón Grupo"]] = df.apply(lambda r: pd.Series(clasificar(r)), axis=1)
    df["Score potencial"] = df.apply(score_potencial, axis=1)
    df["Oportunidades"] = df.apply(lambda r: detectar_oportunidades(r, r["Grupo"]), axis=1)
    df["Problemas detectados"] = df.apply(lambda r: detectar_problemas(r, r["Grupo"]), axis=1)
    df["Acción recomendada"] = df.apply(lambda r: accion_recomendada(r, r["Grupo"], r["Score potencial"]), axis=1)

    # Excel
    cols = ["Cuenta", "ItemID", "Título", "Grupo", "Score potencial", "Razón Grupo",
            "Precio", "Stock", "ListingType", "Fotos", "Visitas30d", "Vendidos180d",
            "Revenue180d", "ConvRate%", "HealthCalc",
            "Oportunidades", "Problemas detectados", "Acción recomendada", "Permalink"]
    df_out = df[cols].sort_values(["Cuenta", "Grupo", "Score potencial"],
                                  ascending=[True, True, False])

    # Resumen por cuenta x grupo
    resumen = df.groupby(["Cuenta", "Grupo"]).agg(
        Items=("ItemID", "count"),
        Visitas_30d=("Visitas30d", "sum"),
        Vendidos_180d=("Vendidos180d", "sum"),
        Revenue_180d=("Revenue180d", "sum"),
        Score_avg=("Score potencial", "mean"),
        Stock_total=("Stock", "sum"),
    ).round(1).reset_index()

    # Top G1 (escalar)
    top_g1 = df[df["Grupo"]=="G1"].sort_values("Revenue180d", ascending=False).head(30)

    # G2 reactivar
    g2_reactivar = df[df["Grupo"]=="G2"].sort_values(["Visitas30d","Vendidos180d"], ascending=False).head(50)

    # G3 republicar (con stock)
    g3_republicar = df[(df["Grupo"]=="G3") & (df["Stock"]>=5)].sort_values("Stock", ascending=False).head(50)

    # G3 pausar (sin stock relevante)
    g3_pausar = df[(df["Grupo"]=="G3") & (df["Stock"]<5)].sort_values("Stock", ascending=False).head(50)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="0. Resumen 3 cuentas x grupo", index=False)
        df_out.to_excel(writer, sheet_name="1. Todas clasificadas", index=False)
        top_g1.to_excel(writer, sheet_name="2. G1 - Escalar", index=False)
        g2_reactivar.to_excel(writer, sheet_name="3. G2 - Reactivar", index=False)
        g3_republicar.to_excel(writer, sheet_name="4. G3 - Republicar", index=False)
        g3_pausar.to_excel(writer, sheet_name="5. G3 - Pausar", index=False)

    print(f"OK Excel: {OUT}\n")
    print("=== Resumen 3 cuentas x grupo ===")
    print(resumen.to_string(index=False))
    print(f"\nDistribución por cuenta:")
    for c in ("C1","C2","C3"):
        sub = df[df["Cuenta"]==c]
        g1=int((sub['Grupo']=='G1').sum()); g2=int((sub['Grupo']=='G2').sum()); g3=int((sub['Grupo']=='G3').sum())
        print(f"  {c}: total={len(sub)} | G1={g1} ({g1/len(sub)*100:.0f}%) | G2={g2} ({g2/len(sub)*100:.0f}%) | G3={g3} ({g3/len(sub)*100:.0f}%)")


if __name__ == "__main__":
    main()
