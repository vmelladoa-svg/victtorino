"""
Genera muestra de 5 publicaciones con título y descripción optimizados (Claude).
Solo SELECCIONA candidatos sin ventas (no toca producción).
Output: muestra_seo_propuesta.xlsx — para validación antes de aplicar masivamente.
"""
import json
import os
from pathlib import Path
import random

import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).parent
SNAP = ROOT / "data" / "auditoria"
load_dotenv(ROOT / ".env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LABELS = {"c1": "C1 PREMIUMGRIFERIAS1",
          "c2": "C2 VICTTORINOOFICIAL2",
          "c3": "C3 NOVAGRIFERIAS3"}

SYSTEM = """Eres experto en SEO de MercadoLibre Chile para una tienda de griferias, accesorios
de bano y cocina. Tu trabajo es optimizar publicaciones para maximizar visibilidad organica
y conversion.

REGLAS PARA TITULO ML:
- Maximo 60 caracteres (limite ML)
- Incluye palabra clave principal al inicio (lo que el cliente buscaria)
- Incluye material, color y caracteristica diferenciadora
- Sin caracteres especiales, sin emojis, sin mayusculas excesivas
- Sin "OFERTA", "PROMOCION", "BARATO" (ML penaliza)

REGLAS PARA DESCRIPCION ML:
- 200-500 palabras
- Estructura: parrafo intro + caracteristicas tecnicas + beneficios + medidas + garantia
- Incluye palabras clave naturales (variaciones del producto)
- Usa frases cortas y claras
- Sin HTML ni markdown (solo texto plano con saltos de linea)
- Cierra con call-to-action sutil

TONO: comercial y profesional, espanol chileno natural."""


def cargar_criticas():
    """Retorna las 77 publicaciones criticas SIN ventas, mezcla de las 3 cuentas."""
    out = []
    for c in ["c1", "c2", "c3"]:
        snap = json.loads((SNAP / f"snapshot_{c}.json").read_text(encoding="utf-8"))
        visits = snap["visitas_30d"]
        for it in snap["items"]:
            if it.get("status") != "active": continue
            if (it.get("sold_quantity") or 0) > 0: continue  # solo sin ventas
            title = it.get("title") or ""
            n_attrs = len(it.get("attributes") or [])
            v30 = visits.get(it["id"], 0)
            score = 0
            if len(title) >= 60: score += 35
            elif len(title) >= 50: score += 25
            elif len(title) >= 40: score += 15
            if n_attrs >= 10: score += 35
            elif n_attrs >= 5: score += 20
            if v30 >= 50: score += 30
            elif v30 >= 10: score += 15
            elif v30 >= 1: score += 5
            if score >= 20: continue
            out.append({"cuenta": c, "item": it})
    return out


def descripcion_atributos(item):
    """Resume los atributos en una lista plana para pasar a Claude."""
    pares = []
    for a in (item.get("attributes") or []):
        n = a.get("name") or a.get("id")
        v = a.get("value_name")
        if n and v:
            pares.append(f"{n}: {v}")
    return pares[:20]


def claude_propuesta(item):
    titulo = item.get("title", "")
    cat = item.get("category_id", "")
    precio = item.get("price")
    attrs = descripcion_atributos(item)
    attr_txt = "\n  - " + "\n  - ".join(attrs) if attrs else "  (sin atributos especificados)"

    user_msg = f"""Optimiza esta publicacion para mejor SEO en MercadoLibre Chile.

Titulo actual: {titulo}
Categoria ML: {cat}
Precio: ${precio:,} CLP

Atributos existentes:
{attr_txt}

Devuelve SOLO JSON valido con este formato:
{{"titulo": "...", "descripcion": "..."}}

No agregues texto antes ni despues del JSON."""

    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = r.content[0].text.strip()
    # Limpiar: a veces viene en bloque ```json...```
    if text.startswith("```"):
        text = text.strip("`").lstrip("json").strip()
    return json.loads(text)


def main():
    candidatos = cargar_criticas()
    print(f"Criticas sin ventas disponibles: {len(candidatos)}")

    # Muestra balanceada por cuenta
    random.seed(42)
    by_cuenta = {"c1": [], "c2": [], "c3": []}
    for c in candidatos:
        by_cuenta[c["cuenta"]].append(c)
    for k in by_cuenta: random.shuffle(by_cuenta[k])
    muestra = (by_cuenta["c1"][:2] + by_cuenta["c2"][:2] + by_cuenta["c3"][:1])
    print(f"Muestra a procesar: {len(muestra)}")

    rows = []
    for i, m in enumerate(muestra, 1):
        it = m["item"]
        print(f"  [{i}/{len(muestra)}] {it['id']} — {it.get('title','')[:60]}")
        try:
            prop = claude_propuesta(it)
            rows.append({
                "Cuenta": LABELS[m["cuenta"]],
                "Item ID": it["id"],
                "Categoría": it.get("category_id"),
                "Precio": it.get("price"),
                "Stock": it.get("available_quantity"),
                "Título ACTUAL": it.get("title"),
                "Largo actual": len(it.get("title") or ""),
                "Título PROPUESTO": prop["titulo"],
                "Largo propuesto": len(prop["titulo"]),
                "Descripción PROPUESTA": prop["descripcion"],
                "Permalink": it.get("permalink"),
            })
        except Exception as e:
            print(f"     ERROR: {e}")
            rows.append({
                "Cuenta": LABELS[m["cuenta"]],
                "Item ID": it["id"],
                "Título ACTUAL": it.get("title"),
                "Título PROPUESTO": f"(error: {e})",
            })

    df = pd.DataFrame(rows)
    out = ROOT / "muestra_seo_propuesta.xlsx"
    df.to_excel(out, index=False)
    print(f"\nOK  {out}")
    print(f"   {len(rows)} propuestas generadas para revision.")


if __name__ == "__main__":
    main()
