"""
Bloque 4 — Generacion de captions para Instagram.

Para cada SKU con score >= 4:
  Genera 3 variantes de caption con Claude API:
    captions/{sku}_tecnico.txt    — Especificaciones, materiales, dimensiones
    captions/{sku}_emocional.txt  — Lifestyle, transformacion, aspiracion
    captions/{sku}_oferta.txt     — Precio, urgencia, llamada a la accion

Todos con DOBLE CTA al cierre:
  - Web: https://www.victtorino.cl
  - WhatsApp: https://wa.link/77uj18

Output: captions/{sku}_{tipo}.txt + captions/_resumen.csv
"""
import sys
import io
import csv
import json
import os
import time
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from anthropic import Anthropic

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CAPTIONS = ROOT / "captions"
CAPTIONS.mkdir(exist_ok=True)

CSV_IN = DATA / "catalogo_instagram.csv"
SCORE_MIN = 4
WEB_CTA = "https://www.victtorino.cl"
WA_CTA = "https://wa.link/77uj18"

# API key desde .env del proyecto padre
def cargar_anthropic_key():
    env_path = ROOT.parent / ".env"
    if not env_path.exists():
        print(f"FALTA {env_path} — necesito ANTHROPIC_API_KEY")
        sys.exit(1)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ANTHROPIC_API_KEY no encontrada en .env")
    sys.exit(1)


client = Anthropic(api_key=cargar_anthropic_key())

SYSTEM_PROMPT = """Eres copywriter experto en Instagram para una tienda chilena
de griferias, lavaplatos y accesorios de bano y cocina llamada VICTTORINO.

REGLA DE IDIOMA — OBLIGATORIA:
Espanol CHILENO neutro. PROHIBIDO el voseo argentino bajo cualquier circunstancia.
- USA: tu / te / tienes / quieres / sientes / empiezas / entras / vienes / piensas
- NO USES NUNCA: vos / tenes / sentis / queres / empezas / entras (voseo)
  / sentís / venís / pensás / sos
- NO uses "che" ni jerga argentina.
- NO uses "fijate", "dale", "vamos arrancando", "te re sirve".
- SI usas tutearle al cliente, usa "tu/te" (no "vos/te").

HOOK FUERTE — OBLIGATORIO:
La PRIMERA LINEA del caption debe ser un GANCHO de 8-14 palabras que enganche al
scroll. Es lo unico que el usuario ve antes del "ver mas" en Instagram.
Patrones que funcionan:
- Pregunta provocadora: "Que pasa cuando el bano deja de ser solo un bano?"
- Cifra concreta: "Por menos de $40.000, este lavaplatos cambia tu cocina."
- Afirmacion sorpresiva: "Pocos lo saben, pero este detalle define toda la cocina."
- Imagen sensorial: "El sonido del agua cae distinto cuando todo esta bien instalado."
Despues del hook, salto de linea y desarrollas el cuerpo.

Reglas SIEMPRE:
- 2-4 emojis maximo por caption, bien ubicados
- Hashtags al final: 8-12 hashtags relevantes en una sola linea
- Caption total: 800-1500 caracteres (incluyendo hashtags)
- Sin asteriscos ni markdown
- Tono adaptado al tipo de caption pedido
- TERMINAR SIEMPRE con doble CTA:

Compralo en {WEB_CTA}
O escribenos por WhatsApp: {WA_CTA}

Devuelve SOLO el caption completo, sin titulo ni explicaciones extras."""


def cargar_shortlist():
    items = []
    with open(CSV_IN, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("pass_filter", "").lower() == "true" \
               and int(r["filter_score"]) >= SCORE_MIN \
               and r.get("image_url"):  # excluir sin foto
                items.append(r)
    return items


PROMPTS_POR_TIPO = {
    "tecnico": (
        "Genera un caption TECNICO. Foco en especificaciones del producto: "
        "material, medidas, acabado, instalacion, garantia. Tono profesional, "
        "directo, informativo. Para clientes que ya saben lo que buscan."
    ),
    "emocional": (
        "Genera un caption EMOCIONAL/LIFESTYLE. Foco en como este producto "
        "transforma el bano o la cocina, en la sensacion de tener un espacio "
        "renovado, en la inspiracion. Para clientes que estan imaginando su "
        "remodelacion. Sin especificaciones tecnicas."
    ),
    "oferta": (
        "Genera un caption de OFERTA/VENTA. Menciona el precio con sentido "
        "de oportunidad (sin inventar descuentos). Destaca envio gratis sobre "
        "$50.000 RM. Usa urgencia sutil. Llamada a la accion clara."
    ),
}


def generar_caption(producto, tipo):
    """Llama a Claude para generar un caption."""
    instruccion = PROMPTS_POR_TIPO[tipo]
    user_msg = f"""Producto:
Nombre: {producto['name']}
SKU: {producto['sku']}
Precio: ${int(producto['price']):,} CLP
Stock: {producto['stock']} unidades
Categoria: {producto['category']}
URL web: {producto['product_url']}

{instruccion}"""
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=SYSTEM_PROMPT.format(WEB_CTA=WEB_CTA, WA_CTA=WA_CTA),
        messages=[{"role": "user", "content": user_msg}],
    )
    return r.content[0].text.strip()


def slugify_sku(sku):
    return re.sub(r"[^A-Za-z0-9_-]", "_", sku) or "sin_sku"


def main():
    print("=== Bloque 4: Generacion de captions ===\n")
    shortlist = cargar_shortlist()
    print(f"Shortlist (score >= {SCORE_MIN}, con foto): {len(shortlist)} SKUs")
    print(f"Captions por SKU: 3 (tecnico + emocional + oferta)")
    print(f"Total a generar: {len(shortlist) * 3} captions\n")

    # Indice de outputs
    index_rows = []
    for i, prod in enumerate(shortlist, 1):
        sku_slug = slugify_sku(prod["sku"])
        print(f"[{i}/{len(shortlist)}] {prod['sku']} — {prod['name'][:55]}")
        for tipo in ["tecnico", "emocional", "oferta"]:
            dest = CAPTIONS / f"{sku_slug}_{tipo}.txt"
            if dest.exists() and dest.stat().st_size > 50:
                print(f"  {tipo}: skip (ya existe)")
                index_rows.append({"sku": prod["sku"], "tipo": tipo,
                                    "archivo": str(dest.relative_to(ROOT)),
                                    "status": "skip_existe"})
                continue
            try:
                caption = generar_caption(prod, tipo)
                dest.write_text(caption, encoding="utf-8")
                print(f"  {tipo}: OK ({len(caption)} chars)")
                index_rows.append({"sku": prod["sku"], "tipo": tipo,
                                    "archivo": str(dest.relative_to(ROOT)),
                                    "status": "ok",
                                    "chars": len(caption)})
                time.sleep(0.4)  # backoff suave
            except Exception as e:
                print(f"  {tipo}: ERROR {e.__class__.__name__}")
                index_rows.append({"sku": prod["sku"], "tipo": tipo,
                                    "archivo": "", "status": f"err_{e.__class__.__name__}"})

    # Indice CSV
    index_csv = CAPTIONS / "_resumen.csv"
    with open(index_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sku", "tipo", "archivo", "status", "chars"])
        w.writeheader()
        for r in index_rows: w.writerow({**{"chars": ""}, **r})

    print(f"\n=== Listo ===")
    ok = sum(1 for r in index_rows if r["status"] == "ok")
    skip = sum(1 for r in index_rows if r["status"] == "skip_existe")
    err = sum(1 for r in index_rows if r["status"].startswith("err"))
    print(f"  OK:    {ok}")
    print(f"  Skip:  {skip}")
    print(f"  Error: {err}")
    print(f"  Indice: {index_csv}")
    print(f"  Captions: {CAPTIONS}/")


if __name__ == "__main__":
    main()
