"""
Enriquece analisis_seo_sin_visitas.xlsx agregando:
  - Si tiene hermano con tráfico/ventas en otra publicación
  - Qué difiere (listing, categoría, fotos, listing type)
  - Acción recomendada concreta
"""
import json
import re
import pickle
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
IN = ROOT / "analisis_seo_sin_visitas.xlsx"
OUT = ROOT / "analisis_seo_sin_visitas_enriched.xlsx"


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    df["NormTitle"] = df["Título"].apply(lambda t: re.sub(r"\s+", " ", (t or "").strip().lower()))

    seo = pd.read_excel(IN)
    enrich_rows = []
    for _, r in seo.iterrows():
        iid = r["ItemID"]
        own = df[df["ItemID"] == iid].iloc[0]
        norm_t = re.sub(r"\s+", " ", (own["Título"] or "").strip().lower())
        siblings = df[(df["NormTitle"] == norm_t) & (df["ItemID"] != iid)]
        winner = None
        if not siblings.empty:
            # Mejor hermano (más ventas, luego más visitas)
            sib = siblings.sort_values(["Vendidos180d", "Visitas30d"], ascending=False).iloc[0]
            if sib["Vendidos180d"] > 0 or sib["Visitas30d"] > 0:
                winner = sib

        # Diff con winner si existe
        if winner is not None:
            diff = []
            if own["ListingType"] != winner["ListingType"]:
                diff.append(f"listing {own['ListingType']}≠{winner['ListingType']}")
            if own["Categoría"] != winner["Categoría"]:
                diff.append(f"cat {own['Categoría']}≠{winner['Categoría']}")
            if own["Fotos"] != winner["Fotos"]:
                diff.append(f"fotos {own['Fotos']}≠{winner['Fotos']}")
            if own["Precio"] != winner["Precio"]:
                diff.append(f"precio ${own['Precio']:,}≠${winner['Precio']:,}")
            accion = ""
            if own["ListingType"] == "gold_special" and winner["ListingType"] == "gold_pro":
                accion = "Upgrade a gold_pro (caso replicación pendiente)"
            elif own["Categoría"] != winner["Categoría"]:
                accion = f"Cambiar categoría a {winner['Categoría']}"
            elif own["Fotos"] < winner["Fotos"]:
                accion = "Copiar fotos del hermano"
            elif diff:
                accion = "Investigar diferencia ranking ML (mismo título, distinto comportamiento)"
            else:
                accion = "Mismo en todo — posible variación de antigüedad / azar algoritmo"
            sib_info = {
                "Hermano ID": winner["ItemID"],
                "Hermano Cuenta": winner["Cuenta"],
                "Hermano Visitas 30d": int(winner["Visitas30d"]),
                "Hermano Vendidos 180d": int(winner["Vendidos180d"]),
                "Hermano Listing": winner["ListingType"],
                "Hermano Categoría": winner["Categoría"],
                "Hermano Fotos": winner["Fotos"],
                "Hermano Precio": int(winner["Precio"]),
                "Diff vs hermano": " | ".join(diff) if diff else "ninguna diferencia visible",
                "Acción recomendada": accion,
            }
        else:
            sib_info = {
                "Hermano ID": "",
                "Hermano Cuenta": "",
                "Hermano Visitas 30d": "",
                "Hermano Vendidos 180d": "",
                "Hermano Listing": "",
                "Hermano Categoría": "",
                "Hermano Fotos": "",
                "Hermano Precio": "",
                "Diff vs hermano": "Sin hermano con tráfico",
                "Acción recomendada": "SEO de cero: optimizar título, completar atributos críticos faltantes",
            }
        enrich_rows.append({**r.to_dict(), **sib_info})

    out = pd.DataFrame(enrich_rows)
    # Reorganizar columnas
    order = ["Cuenta", "ItemID", "Título actual", "Long título", "Categoría", "Precio", "Stock", "Fotos",
             "Listing", "HealthCalc", "Score título 0-100", "Atributos críticos faltantes",
             "Urgencia 0-100",
             "Hermano ID", "Hermano Cuenta", "Hermano Visitas 30d", "Hermano Vendidos 180d",
             "Hermano Listing", "Hermano Categoría", "Hermano Fotos", "Hermano Precio",
             "Diff vs hermano", "Acción recomendada",
             "Issues título", "IDs faltantes", "Permalink"]
    out = out[order].sort_values("Urgencia 0-100", ascending=False)
    out.to_excel(OUT, index=False)
    print(f"OK {OUT}")

    print(f"\n=== Acciones recomendadas ===")
    print(out["Acción recomendada"].value_counts())


if __name__ == "__main__":
    main()
