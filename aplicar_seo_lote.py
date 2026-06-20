"""
Aplica mejoras de SEO (titulo + descripcion) al lote de 77 publicaciones criticas SIN ventas.
Cada item: Claude genera contenido → PUT a ML.

Output:
  aplicar_seo_resultado.xlsx  — tabla con todos los items procesados, OK/error y diff
  aplicar_seo_resultado.log   — log detallado linea a linea
"""
import json
import os
import time
import logging
import sys
import io
from pathlib import Path
from datetime import datetime

import requests
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

# UTF-8 stdout para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
SNAP = ROOT / "data" / "auditoria"
load_dotenv(ROOT / ".env")

LOG_FILE = ROOT / "aplicar_seo_resultado.log"
OUT_XLSX = ROOT / "aplicar_seo_resultado.xlsx"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("seo")

ML = "https://api.mercadolibre.com"
TOKEN_PATHS = {
    "c1": ROOT / "tokens_cuenta1.json",
    "c2": ROOT / "tokens_cuenta2.json",
    "c3": ROOT / "tokens_cuenta3.json",
}
LABELS = {"c1": "C1 PREMIUMGRIFERIAS1", "c2": "C2 VICTTORINOOFICIAL2", "c3": "C3 NOVAGRIFERIAS3"}

anth = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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


def cargar_tokens():
    """Lee access_tokens de los archivos JSON."""
    out = {}
    for k, p in TOKEN_PATHS.items():
        out[k] = json.loads(p.read_text(encoding="utf-8"))["access_token"]
    return out


def cargar_77_criticas():
    """Replica logica de filtrado (criticas sin ventas, score<20)."""
    res = []
    for c in ["c1", "c2", "c3"]:
        snap = json.loads((SNAP / f"snapshot_{c}.json").read_text(encoding="utf-8"))
        visits = snap["visitas_30d"]
        for it in snap["items"]:
            if it.get("status") != "active": continue
            if (it.get("sold_quantity") or 0) > 0: continue
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
            res.append({"cuenta": c, "item": it})
    return res


def descripcion_atributos(item):
    pares = []
    for a in (item.get("attributes") or []):
        n = a.get("name") or a.get("id")
        v = a.get("value_name")
        if n and v: pares.append(f"{n}: {v}")
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

    r = anth.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = r.content[0].text.strip()
    if text.startswith("```"):
        text = text.strip("`").lstrip("json").strip()
    return json.loads(text)


def actualizar_titulo(token, item_id, nuevo_titulo):
    """PUT /items/{id} con nuevo titulo. Devuelve (ok, mensaje)."""
    r = requests.put(
        f"{ML}/items/{item_id}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"title": nuevo_titulo},
        timeout=20,
    )
    if r.status_code in (200, 201):
        return True, "OK"
    try:
        msg = r.json().get("message", r.text[:120])
    except: msg = r.text[:120]
    return False, f"HTTP {r.status_code}: {msg}"


def actualizar_descripcion(token, item_id, nueva_desc):
    """PUT /items/{id}/description o crea si no existe."""
    payload = {"plain_text": nueva_desc}
    r = requests.put(
        f"{ML}/items/{item_id}/description",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if r.status_code == 404:
        # No existe, crear
        r = requests.post(
            f"{ML}/items/{item_id}/description",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
    if r.status_code in (200, 201):
        return True, "OK"
    try:
        msg = r.json().get("message", r.text[:120])
    except: msg = r.text[:120]
    return False, f"HTTP {r.status_code}: {msg}"


def main():
    tokens = cargar_tokens()
    criticas = cargar_77_criticas()
    logger.info(f"Iniciando lote SEO — {len(criticas)} publicaciones criticas sin ventas")

    rows = []
    for i, m in enumerate(criticas, 1):
        c = m["cuenta"]
        it = m["item"]
        iid = it["id"]
        title_old = it.get("title", "")
        logger.info(f"[{i}/{len(criticas)}] {LABELS[c]} {iid} — {title_old[:55]}")

        # 1) Generar con Claude
        try:
            prop = claude_propuesta(it)
            t_new = prop["titulo"][:60]  # ML limit
            d_new = prop["descripcion"]
        except Exception as e:
            logger.error(f"  Claude fail: {e}")
            rows.append({
                "Cuenta": LABELS[c], "Item ID": iid, "Titulo viejo": title_old,
                "Titulo nuevo": "", "Largo nuevo": 0, "Estado titulo": f"ERROR Claude: {e}",
                "Estado descripcion": "N/A", "Permalink": it.get("permalink"),
            })
            continue

        # 2) PUT titulo
        ok_t, msg_t = actualizar_titulo(tokens[c], iid, t_new)
        time.sleep(0.4)

        # 3) PUT descripcion
        ok_d, msg_d = actualizar_descripcion(tokens[c], iid, d_new)
        time.sleep(0.5)

        logger.info(f"  titulo={msg_t}  | descripcion={msg_d}")

        rows.append({
            "Cuenta": LABELS[c],
            "Item ID": iid,
            "Titulo viejo": title_old,
            "Largo viejo": len(title_old),
            "Titulo nuevo": t_new,
            "Largo nuevo": len(t_new),
            "Estado titulo": msg_t,
            "Estado descripcion": msg_d,
            "Descripcion nueva (preview)": d_new[:200] + ("..." if len(d_new) > 200 else ""),
            "Permalink": it.get("permalink"),
        })

    # Resumen
    df = pd.DataFrame(rows)
    df.to_excel(OUT_XLSX, index=False)

    ok_t = (df["Estado titulo"] == "OK").sum()
    ok_d = (df["Estado descripcion"] == "OK").sum()
    logger.info(f"\n=== RESUMEN ===")
    logger.info(f"  Items procesados: {len(df)}")
    logger.info(f"  Titulos actualizados: {ok_t}")
    logger.info(f"  Descripciones actualizadas: {ok_d}")
    logger.info(f"  Excel: {OUT_XLSX}")
    logger.info(f"  Log:   {LOG_FILE}")


if __name__ == "__main__":
    main()
