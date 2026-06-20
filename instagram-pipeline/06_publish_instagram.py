"""
Bloque 6 — Publicacion en Instagram via Meta Graph API.

Soporta:
  - Carrusel multi-foto (hasta 10 imagenes)
  - Etiqueta de producto del Catalogo Meta (Shopping)
  - Hashtags como primer comentario (caption queda limpio)

Uso:
  python 06_publish_instagram.py --test          # publica el primer post del calendario
  python 06_publish_instagram.py --next          # publica el siguiente pendiente
  python 06_publish_instagram.py --sku XXX --tipo emocional
  python 06_publish_instagram.py --dry-run --test
"""
import sys
import io
import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CAPTIONS = ROOT / "captions"
CONFIG_PATH = ROOT / "meta_config.json"
LOG_CSV = DATA / "publicaciones_log.csv"
WOO_PRODS = ROOT.parent / "woo_products_all.json"
SKU_TO_META = DATA / "sku_to_meta_product.json"

GRAPH = "https://graph.facebook.com/v21.0"


def cargar_config():
    if not CONFIG_PATH.exists():
        print(f"FALTA {CONFIG_PATH}")
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def cargar_calendario():
    with open(DATA / "calendario_instagram.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cargar_caption(sku, tipo):
    f = CAPTIONS / f"{sku}_{tipo}.txt"
    return f.read_text(encoding="utf-8") if f.exists() else None


def split_caption_hashtags(text):
    """Separa cuerpo y hashtags. Devuelve (body, hashtags_str)."""
    lines = text.splitlines()
    hashtags_line = ""
    body_lines = lines[:]
    # buscar ultima linea que comience con '#'
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("#"):
            hashtags_line = lines[i].strip()
            body_lines = lines[:i]
            break
    # remover trailing whitespace lines del cuerpo
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    return "\n".join(body_lines), hashtags_line


def ya_publicado(sku, tipo):
    if not LOG_CSV.exists(): return False
    with open(LOG_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sku"] == sku and r["tipo"] == tipo and r["status"] == "ok":
                return True
    return False


def loguear(sku, tipo, fecha, status, media_id, comment_id="", error="", fb_post_id=""):
    LOG_CSV.parent.mkdir(exist_ok=True)
    nuevo = not LOG_CSV.exists()
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["timestamp","fecha","sku","tipo","status","media_id","comment_id","error","fb_post_id"])
        w.writerow([datetime.now().isoformat(), fecha, sku, tipo, status, media_id, comment_id, error, fb_post_id])


# ════════════════════════════════════════════════════════
# Helpers Meta API
# ════════════════════════════════════════════════════════

def crear_child_carrusel(ig_id, page_token, image_url, product_tags=None):
    """POST /{ig_id}/media is_carousel_item=true → devuelve child container id.
       Para Shopping tags en carrusel, los tags van por child (no en el container)."""
    params = {
        "access_token": page_token,
        "image_url": image_url,
        "is_carousel_item": "true",
    }
    if product_tags:
        params["product_tags"] = json.dumps(product_tags)
    r = requests.post(f"{GRAPH}/{ig_id}/media", params=params, timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return r.json().get("id"), "OK"


def crear_container_carrusel(ig_id, page_token, children_ids, caption, product_tags=None):
    """POST /{ig_id}/media CAROUSEL con children + caption."""
    params = {
        "access_token": page_token,
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
    }
    if product_tags:
        params["product_tags"] = json.dumps(product_tags)
    r = requests.post(f"{GRAPH}/{ig_id}/media", params=params, timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return r.json().get("id"), "OK"


def publicar_container(ig_id, page_token, creation_id):
    """POST /{ig_id}/media_publish → media_id final."""
    r = requests.post(f"{GRAPH}/{ig_id}/media_publish",
                      params={"access_token": page_token, "creation_id": creation_id},
                      timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return r.json().get("id"), "OK"


def comentar(media_id, page_token, text):
    """POST /{media_id}/comments → comment_id (para hashtags en primer comentario)."""
    r = requests.post(f"{GRAPH}/{media_id}/comments",
                      params={"access_token": page_token, "message": text},
                      timeout=30)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return r.json().get("id"), "OK"


def publicar_en_facebook(page_id, page_token, image_urls, caption):
    """Publica en la Page de Facebook.
       - 1 foto: POST /{page_id}/photos
       - N fotos: subir como unpublished, luego /{page_id}/feed con attached_media
       Devuelve (fb_post_id, msg)."""
    if not image_urls:
        return None, "sin fotos"
    if len(image_urls) == 1:
        r = requests.post(f"{GRAPH}/{page_id}/photos",
                          params={"access_token": page_token,
                                  "url": image_urls[0],
                                  "message": caption},
                          timeout=60)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}: {r.text[:200]}"
        return r.json().get("post_id") or r.json().get("id"), "OK"

    # Multi-foto: subir cada una sin publicar, luego post de feed con attached_media
    attached = []
    for url in image_urls:
        r = requests.post(f"{GRAPH}/{page_id}/photos",
                          params={"access_token": page_token,
                                  "url": url, "published": "false"},
                          timeout=60)
        if r.status_code != 200:
            return None, f"upload child HTTP {r.status_code}: {r.text[:120]}"
        attached.append({"media_fbid": r.json()["id"]})
        time.sleep(0.5)
    r2 = requests.post(f"{GRAPH}/{page_id}/feed",
                       params={"access_token": page_token,
                               "message": caption,
                               "attached_media": json.dumps(attached)},
                       timeout=60)
    if r2.status_code != 200:
        return None, f"feed HTTP {r2.status_code}: {r2.text[:200]}"
    return r2.json().get("id"), "OK"


# ════════════════════════════════════════════════════════
# Flujo principal
# ════════════════════════════════════════════════════════

def _fotos_de_sku(sku):
    """Lee woo_products_all.json y devuelve hasta 10 URLs de fotos del SKU."""
    prods = json.loads(WOO_PRODS.read_text(encoding="utf-8"))
    for p in prods:
        if p.get("sku") == sku:
            return [img["src"] for img in (p.get("images") or [])][:10]
    return []


def _publicar(entry, cfg, dry_run=False):
    sku = entry["sku"]
    tipo = entry["tipo_caption"]
    fecha = entry["fecha"]

    print(f"\n=== Publicar SKU {sku} ({tipo}) ===")
    print(f"  Producto: {entry['nombre'][:60]}")

    if ya_publicado(sku, tipo):
        print(f"  ya publicado antes (skip)")
        return 0

    caption_raw = cargar_caption(sku, tipo)
    if not caption_raw:
        print(f"  ERROR: caption no encontrado")
        return 1
    body, hashtags = split_caption_hashtags(caption_raw)
    print(f"  Caption body: {len(body)} chars  |  Hashtags al comment: {len(hashtags)} chars")

    # Fotos para carrusel
    fotos = _fotos_de_sku(sku)
    print(f"  Fotos disponibles: {len(fotos)}")
    if not fotos:
        print("  ERROR: sin fotos")
        return 1

    # Mapping a Meta catalog product
    mapping = json.loads(SKU_TO_META.read_text(encoding="utf-8")) if SKU_TO_META.exists() else {}
    meta_product_id = mapping.get(sku)
    product_tags = None
    if meta_product_id:
        # product_tags en IG: lista de tags con product_id y posicion (x,y) fraccional [0,1]
        # Posicion centro = (0.5, 0.5)
        product_tags = [{"product_id": meta_product_id, "x": 0.5, "y": 0.5}]
        print(f"  Product Tag Shopping: meta_id={meta_product_id}")
    else:
        print(f"  Sin product tag (no mapping)")

    if dry_run:
        print(f"  [DRY-RUN] sin enviar a Meta")
        return 0

    # Si solo hay 1 foto → publicacion simple (sin carrusel)
    ig_id = cfg["IG_BUSINESS_ID"]
    page_token = cfg["META_PAGE_TOKEN"]

    if len(fotos) == 1:
        # Simple
        r = requests.post(f"{GRAPH}/{ig_id}/media",
                          params={"access_token": page_token, "image_url": fotos[0],
                                  "caption": body,
                                  **({"product_tags": json.dumps(product_tags)} if product_tags else {})},
                          timeout=60)
        if r.status_code != 200:
            err = f"crear container simple: HTTP {r.status_code}: {r.text[:200]}"
            print(f"  ❌ {err}")
            loguear(sku, tipo, fecha, "error", "", "", err)
            return 1
        creation_id = r.json()["id"]
    else:
        # Carrusel — product_tags van por CHILD, no por container
        print("  Creando children de carrusel...")
        children = []
        for i, url in enumerate(fotos):
            cid, msg = crear_child_carrusel(ig_id, page_token, url, product_tags)
            if not cid:
                print(f"    foto {i+1}: ERROR {msg}")
                # Si falla por product_tag, reintentar sin tag
                if product_tags:
                    cid, msg = crear_child_carrusel(ig_id, page_token, url, None)
                    if cid:
                        print(f"    foto {i+1}: reintentado sin product_tag → OK")
                        product_tags = None  # quitar para todos los siguientes
            if cid:
                children.append(cid)
            time.sleep(0.5)
        if len(children) < 2:
            err = f"insuficientes children ({len(children)}) para carrusel"
            print(f"  ❌ {err}")
            loguear(sku, tipo, fecha, "error", "", "", err)
            return 1
        print(f"  {len(children)} children creados {'(con product_tags)' if product_tags else '(sin product_tags)'}")

        # Container del carrusel — SIN product_tags (van en children)
        creation_id, msg = crear_container_carrusel(ig_id, page_token, children, body, None)
        if not creation_id:
            err = f"crear carrusel: {msg}"
            print(f"  ❌ {err}")
            loguear(sku, tipo, fecha, "error", "", "", err)
            return 1

    # Esperar a que IG procese
    print(f"  creation_id={creation_id}  esperando procesamiento...")
    time.sleep(8)

    # Publicar
    media_id, msg = publicar_container(ig_id, page_token, creation_id)
    if not media_id:
        err = f"publish: {msg}"
        print(f"  ❌ {err}")
        loguear(sku, tipo, fecha, "error", "", "", err)
        return 1
    print(f"  ✅ PUBLICADO  media_id={media_id}")

    # Hashtags como primer comentario (deja el caption limpio)
    comment_id = ""
    if hashtags:
        time.sleep(2)
        cid, msg = comentar(media_id, page_token, hashtags)
        if cid:
            comment_id = cid
            print(f"  ✅ Hashtags en comment {cid}")
        else:
            print(f"  ⚠ Comment falló: {msg}")

    # === Publicar también en Facebook Page ===
    fb_post_id = ""
    print("  → Publicando también en Facebook Page...")
    fb_id, fb_msg = publicar_en_facebook(cfg["FB_PAGE_ID"], page_token, fotos, body)
    if fb_id:
        fb_post_id = fb_id
        print(f"  ✅ Facebook OK  post_id={fb_id}")
    else:
        print(f"  ⚠️  Facebook falló: {fb_msg}")

    loguear(sku, tipo, fecha, "ok", media_id, comment_id, "" if fb_id else fb_msg, fb_post_id)
    print(f"  Veelo en https://www.instagram.com/{cfg['IG_USERNAME']}/")
    if fb_post_id:
        print(f"  Y en https://www.facebook.com/{cfg['FB_PAGE_NAME']}/")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    p.add_argument("--next", action="store_true")
    p.add_argument("--sku")
    p.add_argument("--tipo", default="emocional")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    cfg = cargar_config()
    print(f"Cuenta: @{cfg['IG_USERNAME']}")

    if args.test:
        return _publicar(cargar_calendario()[0], cfg, args.dry_run)
    if args.next:
        for e in cargar_calendario():
            if not ya_publicado(e["sku"], e["tipo_caption"]):
                return _publicar(e, cfg, args.dry_run)
        print("Todos publicados.")
        return 0
    if args.sku:
        for e in cargar_calendario():
            if e["sku"] == args.sku and e["tipo_caption"] == args.tipo:
                return _publicar(e, cfg, args.dry_run)
        print(f"No encontrado SKU={args.sku} tipo={args.tipo}")
        return 1
    p.print_help()


if __name__ == "__main__":
    sys.exit(main())
