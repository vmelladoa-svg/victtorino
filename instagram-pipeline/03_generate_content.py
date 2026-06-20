"""
Bloque 3 — Generacion de contenido visual.

Para cada SKU con score >= 4:
  1. Descarga imagen original a raw_images/{sku}.jpg
  2. Genera 5 variantes con banana-claude / nanobanana MCP:
       studio_{sku}.jpg     1080x1080
       lifestyle_{sku}.jpg  1080x1080
       detail_{sku}.jpg     1080x1080
       carousel_{sku}.jpg   1080x1080
       story_{sku}.jpg      1080x1920
  3. Genera 3 captions con Claude API:
       captions/{sku}_tecnico.txt
       captions/{sku}_emocional.txt
       captions/{sku}_oferta.txt
     Todos con doble CTA (web + WhatsApp).

NOTA: banana-claude / nanobanana MCP es un servicio externo. Si no esta
instalado, este script muestra el comando para instalarlo y se detiene.
"""
import sys
import io
import csv
import shutil
import subprocess
import requests
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RAW = ROOT / "raw_images"
GEN = ROOT / "generated_images"
CAPTIONS = ROOT / "captions"
RAW.mkdir(exist_ok=True)
GEN.mkdir(exist_ok=True)
CAPTIONS.mkdir(exist_ok=True)

CSV_IN = DATA_DIR / "catalogo_instagram.csv"
SCORE_MIN = 4
WEB_CTA = "https://www.victtorino.cl"
WA_CTA = "https://wa.link/77uj18"


def cargar_shortlist():
    if not CSV_IN.exists():
        print(f"FALTA {CSV_IN} — corre 01_extract_catalog.py primero")
        sys.exit(1)
    items = []
    with open(CSV_IN, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("pass_filter", "").lower() == "true" and int(r["filter_score"]) >= SCORE_MIN:
                items.append(r)
    return items


def descargar_imagen(url, dest):
    """Descarga url a dest. Idempotente."""
    if dest.exists() and dest.stat().st_size > 0:
        return "skip_existe"
    try:
        r = requests.get(url, timeout=20, stream=True)
        if r.status_code != 200:
            return f"err_http_{r.status_code}"
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk: f.write(chunk)
        return "ok"
    except Exception as e:
        return f"err_{e.__class__.__name__}"


def check_banana_claude():
    """Verifica si banana-claude o nanobanana-mcp esta disponible."""
    # 1) Buscar en PATH
    for cmd in ["banana-claude", "nanobanana-mcp", "banana"]:
        if shutil.which(cmd):
            return True, cmd
    # 2) Buscar via npm
    try:
        r = subprocess.run(["npm", "list", "-g", "--depth=0"],
                           capture_output=True, text=True, timeout=10)
        if "nanobanana" in r.stdout.lower() or "banana-claude" in r.stdout.lower():
            return True, "(via npm global)"
    except Exception:
        pass
    return False, None


def main():
    print("=== Bloque 3: Generacion de contenido visual ===\n")
    shortlist = cargar_shortlist()
    print(f"Shortlist (score >= {SCORE_MIN}): {len(shortlist)} SKUs\n")

    # ────────────────────────────────────────────────────
    # 1) DESCARGA DE IMAGENES ORIGINALES
    # ────────────────────────────────────────────────────
    print("[1/3] Descargando imagenes originales...")
    stats = {"ok": 0, "skip_existe": 0, "err": 0}
    for r in shortlist:
        sku = r["sku"] or "sin_sku"
        url = r["image_url"]
        if not url:
            print(f"  WARN {sku}: sin image_url")
            stats["err"] += 1
            continue
        dest = RAW / f"{sku}.jpg"
        res = descargar_imagen(url, dest)
        if res == "ok":      stats["ok"] += 1
        elif res == "skip_existe": stats["skip_existe"] += 1
        else:                stats["err"] += 1
    print(f"  Descargadas nuevas: {stats['ok']}")
    print(f"  Ya existian:        {stats['skip_existe']}")
    print(f"  Errores:            {stats['err']}")
    print(f"  Total raw imagenes en {RAW.name}/: {len(list(RAW.glob('*.jpg')))}\n")

    # ────────────────────────────────────────────────────
    # 2) VERIFICACION DE BANANA-CLAUDE / NANOBANANA MCP
    # ────────────────────────────────────────────────────
    print("[2/3] Verificando banana-claude / nanobanana MCP...")
    ok, cmd = check_banana_claude()
    if not ok:
        print("\n  ⚠️  banana-claude NO esta instalado.")
        print("  Sin este servicio no se pueden generar las 5 variantes por SKU.\n")
        print("  Instalacion sugerida:\n")
        print("     npm install -g @nanobanana/mcp\n")
        print("  Alternativamente, otras opciones de generacion de imagenes con IA:")
        print("     - Replicate (https://replicate.com) — pay-per-image")
        print("     - OpenAI DALL-E 3 (https://platform.openai.com)")
        print("     - Stability AI SDXL (https://platform.stability.ai)\n")
        print("  Una vez instalado banana-claude, vuelve a correr este script.")
        print("  DETENIDO (Bloque 3 incompleto).")
        return
    print(f"  OK — disponible via: {cmd}\n")

    # ────────────────────────────────────────────────────
    # 3) GENERACION DE 5 VARIANTES POR SKU
    # ────────────────────────────────────────────────────
    print("[3/3] Generando 5 variantes por SKU con banana-claude...")
    print("  (no implementado todavia — solo placeholder de la integracion)")
    # TODO: aqui ira la llamada al MCP/CLI de banana-claude
    # for r in shortlist:
    #     for variante in ["studio", "lifestyle", "detail", "carousel", "story"]:
    #         banana_generar(...)


if __name__ == "__main__":
    main()
