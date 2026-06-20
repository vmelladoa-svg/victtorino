"""
Genera títulos optimizados para los 82 items 'SEO de cero'.
Estrategia:
  - Producto base = primeras palabras significativas del título actual
  - Atributos clave del item: MODEL, ALPHANUMERIC_MODEL, MATERIAL, COLOR, FINISH, BRAND, dimensiones
  - Componer: <Producto> <Modelo/Specs> <Material> <Color> <Acabado> <Marca>
  - Capitalizar tipo Título, máximo 60 chars
  - Comparar score título nuevo vs actual

Output: titulos_sugeridos_seo.xlsx (revisión humana antes de aplicar)
"""
import json
import re
import pickle
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
SEO_ENR = ROOT / "analisis_seo_sin_visitas_enriched.xlsx"
OUT = ROOT / "titulos_sugeridos_seo.xlsx"

# Atributos a incluir si están presentes, en orden de preferencia
ATTR_PRIORITY = [
    "ALPHANUMERIC_MODEL", "MODEL",
    "DIAMETER", "LENGTH", "WIDTH", "HEIGHT", "DEPTH",
    "ROLL_LENGTH", "VOLUME_CAPACITY",
    "MATERIAL", "MAIN_MATERIAL", "MAJOR_COMPONENT",
    "COLOR", "FINISH",
    "BRAND",
]

STOP_BRANDS = {"genérico", "generico", "sin marca"}  # no usar como marca


def to_title_case(s):
    """Capitalización tipo Título: cada palabra inicia mayúscula salvo conectores."""
    if not s:
        return s
    smalls = {"de", "del", "la", "el", "y", "o", "en", "con", "sin", "para", "por", "a", "al", "x"}
    words = s.lower().split()
    out = []
    for i, w in enumerate(words):
        if i > 0 and w in smalls:
            out.append(w)
        else:
            # Mantener números intactos
            if w[0].isdigit():
                out.append(w)
            else:
                out.append(w[0].upper() + w[1:])
    return " ".join(out)


def attr_index(snapshot_item):
    out = {}
    for a in (snapshot_item.get("attributes") or []):
        val = a.get("value_name") or ((a.get("values") or [{}])[0].get("name"))
        if val:
            out[a["id"]] = val
    return out


def find_template_winner(df, category, exclude_id):
    """Devuelve un item ganador (más ventas + visitas) de la misma categoría."""
    candidates = df[
        (df["Categoría"] == category) &
        (df["ItemID"] != exclude_id) &
        (df["Vendidos180d"] > 0)
    ].sort_values(["Vendidos180d", "Visitas30d"], ascending=False)
    if candidates.empty:
        return None
    return candidates.iloc[0]


def build_new_title(current, attrs, template_title=None, max_len=60):
    """
    Enriquece el título actual agregando atributos faltantes (no reescribe).
    Pasos:
      1. Normalizar espacios y capitalización
      2. Quitar palabras duplicadas consecutivas (ej: 'plateado plateado')
      3. Agregar al final: dimensiones, material, color, finish, marca — solo si no están ya
    """
    base = re.sub(r"\s+", " ", (current or "").strip())
    base_lower = base.lower()

    # Detectar palabras duplicadas consecutivas
    words = base.split()
    cleaned_words = []
    for w in words:
        if cleaned_words and cleaned_words[-1].lower() == w.lower():
            continue
        cleaned_words.append(w)
    base = " ".join(cleaned_words)
    base_lower = base.lower()

    # Set de keywords ya presentes (versión lowercase + sin tildes)
    def strip_accents(s):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()
    base_norm = strip_accents(base)

    additions = []

    def has(text):
        if not text:
            return True
        return strip_accents(text) in base_norm

    # Agregar dimensiones si están en atributos pero no en título
    for dim_key, sufijo in [
        ("ROLL_LENGTH", ""),       # ej "216 m"
        ("VOLUME_CAPACITY", ""),   # ej "500 ml"
        ("LENGTH", ""),
        ("DIAMETER", ""),
    ]:
        v = attrs.get(dim_key)
        if v and not has(v):
            additions.append(v)
            break  # una sola medida principal

    # Material (si tiene sustancia)
    mat = attrs.get("MATERIAL") or attrs.get("MAIN_MATERIAL") or attrs.get("MAJOR_COMPONENT")
    if mat:
        # Solo agregar si menciona acero/inox/vidrio/etc
        if any(m in mat.lower() for m in ("acero", "inox", "vidrio", "porcelana", "cerámica", "ceramica", "metal", "pvc", "abs", "abs")):
            if not has(mat):
                additions.append(mat)

    # Color
    color = attrs.get("COLOR")
    if color and not has(color):
        additions.append(color)

    # Finish
    finish = attrs.get("FINISH")
    if finish and not has(finish):
        additions.append(finish)

    # Marca (si no es genérica y no está)
    brand = attrs.get("BRAND")
    if brand and brand.lower() not in STOP_BRANDS and not has(brand):
        additions.append(brand)

    # Componer
    new = base + (" " + " ".join(additions) if additions else "")
    new = re.sub(r"\s+", " ", new).strip()
    new = to_title_case(new)

    # Truncar a max_len si excede (palabra entera)
    if len(new) > max_len:
        cut = new[:max_len].rsplit(" ", 1)[0]
        new = cut
    return new


def score_title(title):
    """Reutilizable: score 0-100."""
    if not title:
        return 0
    s = 0
    L = len(title)
    if L >= 55: s += 30
    elif L >= 40: s += 20
    elif L >= 30: s += 10
    if re.search(r"\d", title): s += 15
    if re.search(r"\b(blanco|negro|cromado|plateado|dorado|azul|rojo|verde|transparente|mate|brillante|gris)\b", title, re.I): s += 15
    if re.search(r"\b(acero|inoxidable|inox|pl[áa]stico|vidrio|porcelana|cer[áa]mica|metal|cromado)\b", title, re.I): s += 15
    if re.search(r"\b(victtorino|domenica|colomba|notte|tumm|t[aä]umm)\b", title, re.I): s += 10
    words = title.split()
    if words and sum(1 for w in words if w[0:1].isupper()) > len(words) * 0.7: s += 10
    if "  " not in title: s += 5
    return min(s, 100)


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    snapshots = data["snapshots"]

    # Index items raw by id (con atributos)
    raw_by_id = {}
    for c in ("C1", "C2", "C3"):
        for it in snapshots[c]["items"]:
            if it.get("status") == "active":
                raw_by_id[it["id"]] = it

    # 82 items SEO de cero
    seo = pd.read_excel(SEO_ENR)
    seo_cero = seo[seo["Acción recomendada"].str.startswith("SEO de cero")].copy()
    print(f"Procesando {len(seo_cero)} items SEO de cero")

    rows = []
    for _, r in seo_cero.iterrows():
        iid = r["ItemID"]
        raw = raw_by_id.get(iid)
        if not raw:
            continue
        attrs = attr_index(raw)
        current = r["Título actual"] or ""
        template = find_template_winner(df, r["Categoría"], iid)
        new_title = build_new_title(current, attrs, template["Título"] if template is not None else None)

        rows.append({
            "Cuenta": r["Cuenta"],
            "ItemID": iid,
            "Categoría": r["Categoría"],
            "Stock": r["Stock"],
            "Precio": r["Precio"],
            "Fotos": r["Fotos"],
            "Título actual": current,
            "Long actual": len(current),
            "Score actual": score_title(current),
            "Título sugerido": new_title,
            "Long sugerido": len(new_title),
            "Score sugerido": score_title(new_title),
            "Δ Score": score_title(new_title) - score_title(current),
            "Template (ganador cat)": template["Título"] if template is not None else "",
            "Template ID": template["ItemID"] if template is not None else "",
            "Attrs MODEL": attrs.get("MODEL", ""),
            "Attrs COLOR": attrs.get("COLOR", ""),
            "Attrs FINISH": attrs.get("FINISH", ""),
            "Attrs MATERIAL": attrs.get("MATERIAL") or attrs.get("MAIN_MATERIAL", ""),
            "Attrs BRAND": attrs.get("BRAND", ""),
            "Urgencia (heredada)": r["Urgencia 0-100"],
            "Permalink": r["Permalink"],
        })

    out = pd.DataFrame(rows)
    out = out.sort_values(["Δ Score", "Urgencia (heredada)"], ascending=[False, False])
    out.to_excel(OUT, index=False)
    print(f"OK {OUT}")
    print(f"\nDistribución Δ Score:")
    print(out["Δ Score"].describe())
    print(f"\nItems con mejora >= 20 puntos: {(out['Δ Score']>=20).sum()}")
    print(f"Items con mejora >= 10 puntos: {(out['Δ Score']>=10).sum()}")
    print(f"Items con cambio (Δ != 0): {(out['Δ Score']!=0).sum()}")
    print(f"Items sin mejora (Δ <= 0): {(out['Δ Score']<=0).sum()}")
    print()
    print("=== Top 15 mejoras ===")
    for _, r in out.head(15).iterrows():
        print(f"  +{r['Δ Score']:>3d}  {r['Cuenta']} {r['ItemID']}  ({r['Score actual']}→{r['Score sugerido']}, {r['Long actual']}→{r['Long sugerido']} chars)")
        print(f"        AHORA: {r['Título actual']}")
        print(f"        NUEVO: {r['Título sugerido']}")


if __name__ == "__main__":
    main()
