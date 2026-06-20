"""
Análisis SEO de items sin visitas 30d (stock>0).
- Trae atributos requeridos/críticos por categoría ML
- Detecta atributos faltantes por item
- Scorea calidad del título (longitud, especs, keywords del rubro)
- Compara contra items "ganadores" (vendidos>=3) de la misma categoría
- Output: analisis_seo_sin_visitas.xlsx priorizado por (potencial * facilidad)
"""
import json
import re
import time
import pickle
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
OUT = ROOT / "analisis_seo_sin_visitas.xlsx"
CACHE = ROOT / "data" / "auditoria" / "cat_attrs_cache.json"

TOK_C1 = json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"]
H = {"Authorization": f"Bearer {TOK_C1}"}


def fetch_cat_attrs(cat_id, cache):
    if cat_id in cache:
        return cache[cat_id]
    r = requests.get(f"https://api.mercadolibre.com/categories/{cat_id}/attributes",
                     headers=H, timeout=15)
    if r.status_code != 200:
        cache[cat_id] = []
        return []
    attrs = r.json()
    # Solo guardar lo necesario
    keep = []
    for a in attrs:
        tags = a.get("tags") or {}
        if any(tags.get(k) for k in ("required", "catalog_required", "fixed", "conditional_required")):
            keep.append({
                "id": a["id"], "name": a.get("name"),
                "type": a.get("value_type"),
                "tags": [k for k, v in tags.items() if v],
                "values_count": len(a.get("values") or []),
            })
    cache[cat_id] = keep
    return keep


def title_score(title):
    """Score 0-100 del título según best practices ML."""
    if not title:
        return 0, ["Título vacío"]
    issues = []
    score = 0
    L = len(title)
    if L >= 55:
        score += 30
    elif L >= 40:
        score += 20
        issues.append(f"Título corto ({L} chars, ideal 55-60)")
    else:
        score += 5
        issues.append(f"Título muy corto ({L} chars)")
    # Tiene números (especs)
    if re.search(r"\d", title):
        score += 15
    else:
        issues.append("Falta especificación numérica (medida, capacidad)")
    # Tiene color
    if re.search(r"\b(blanco|negro|cromado|plateado|dorado|azul|rojo|verde|transparente|mate|brillante|gris)\b", title, re.I):
        score += 15
    else:
        issues.append("Falta color/acabado en título")
    # Tiene material
    if re.search(r"\b(acero|inoxidable|inox|pl[áa]stico|vidrio|porcelana|cer[áa]mica|metal|cromado)\b", title, re.I):
        score += 15
    else:
        issues.append("Falta material en título")
    # Tiene marca o referencia
    if re.search(r"\b(victtorino|domenica|colomba|notte|tumm|t[aä]umm)\b", title, re.I):
        score += 10
    # Mayúsculas iniciales (capitalización correcta)
    words = title.split()
    if words and sum(1 for w in words if w[0].isupper()) > len(words) * 0.7:
        score += 10
    else:
        issues.append("Capitalización pobre (debería ser tipo Título)")
    # No tener doble espacio
    if "  " not in title:
        score += 5
    else:
        issues.append("Doble espacio en título")
    return min(score, 100), issues


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    sin = df[(df["Visitas30d"] == 0) & (df["Stock"] > 0)].copy()
    print(f"Items sin visitas: {len(sin)}")

    # Cache de atributos por categoría
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        cache = {}
    cats = sin["Categoría"].unique().tolist()
    print(f"Categorías a consultar: {len(cats)}")
    for i, c in enumerate(cats, 1):
        if c in cache:
            continue
        fetch_cat_attrs(c, cache)
        print(f"  [{i}/{len(cats)}] {c}: {len(cache[c])} atributos críticos")
        time.sleep(0.1)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cache: {CACHE}")

    # Items "ganadores" (vendidos>=3) por categoría para comparativa
    ganadores = df[df["Vendidos180d"] >= 3].groupby("Categoría").agg(
        n_gan=("ItemID", "count"),
        avg_title_len=("Título", lambda x: int(x.str.len().mean())),
    ).reset_index()
    ganadores_map = {r["Categoría"]: r for _, r in ganadores.iterrows()}

    # Necesitamos atributos REALES del item — los traemos en bulk
    print("\nTrayendo atributos por item...")
    snapshots = data["snapshots"]
    item_to_attrs = {}
    for c in ("C1", "C2", "C3"):
        for it in snapshots[c]["items"]:
            if it.get("status") != "active":
                continue
            item_to_attrs[it["id"]] = {a["id"] for a in (it.get("attributes") or [])}
    print(f"  Items con atributos en snapshot: {len(item_to_attrs)}")

    # Scoring por item
    rows = []
    for _, r in sin.iterrows():
        iid = r["ItemID"]
        cat = r["Categoría"]
        title = r["Título"] or ""
        cat_attrs = cache.get(cat, [])
        critical_ids = {a["id"] for a in cat_attrs}
        actual_attrs = item_to_attrs.get(iid, set())
        missing_critical = sorted(critical_ids - actual_attrs)
        ts, t_issues = title_score(title)

        # Score global (potencial mejora SEO)
        # Más alto = más urgente arreglar
        urgencia = 0
        if ts < 50: urgencia += 30
        elif ts < 70: urgencia += 15
        urgencia += min(len(missing_critical) * 5, 30)
        # Si tiene stock alto, vale más arreglar
        if r["Stock"] >= 10: urgencia += 15
        # Si fotos están bien (4+) y no tiene visitas, el SEO debe ser el problema
        if r["Fotos"] >= 4: urgencia += 10

        gan = ganadores_map.get(cat)
        gan_n = int(gan["n_gan"]) if gan is not None else 0
        gan_title_len = int(gan["avg_title_len"]) if gan is not None else 0

        rows.append({
            "Cuenta": r["Cuenta"],
            "ItemID": iid,
            "Título actual": title,
            "Long título": len(title),
            "Long título ganadores cat": gan_title_len,
            "Categoría": cat,
            "Ganadores en cat": gan_n,
            "Precio": r["Precio"],
            "Stock": r["Stock"],
            "Fotos": r["Fotos"],
            "Listing": r["ListingType"],
            "HealthCalc": r["HealthCalc"],
            "Score título 0-100": ts,
            "Issues título": " | ".join(t_issues),
            "Atributos críticos faltantes": len(missing_critical),
            "IDs faltantes": ", ".join(missing_critical[:10]),
            "Urgencia 0-100": min(urgencia, 100),
            "Permalink": r["Permalink"],
        })

    out = pd.DataFrame(rows).sort_values(["Urgencia 0-100", "Stock"], ascending=[False, False])
    out.to_excel(OUT, index=False)
    print(f"\nOK {OUT}")

    print(f"\n=== Distribución urgencia ===")
    print(out["Urgencia 0-100"].describe())
    print(f"\n=== Por cuenta ===")
    print(out.groupby("Cuenta")["Urgencia 0-100"].agg(["count", "mean", "max"]).round(1))

    print(f"\n=== Top 15 más urgentes ===")
    for _, r in out.head(15).iterrows():
        print(f"  [{r['Urgencia 0-100']}] {r['Cuenta']} {r['ItemID']} | {r['Título actual'][:55]}")
        print(f"        score título {r['Score título 0-100']} | attrs faltantes {r['Atributos críticos faltantes']} | "
              f"stock {r['Stock']} | fotos {r['Fotos']}")


if __name__ == "__main__":
    main()
