# -*- coding: utf-8 -*-
"""
Descarga fotos desde ML y las sube a Meta Ads como imagenes publicitarias.
Genera los hashes necesarios para crear los anuncios.
"""
import json, requests, time, sys
from pathlib import Path

META_TOKEN = "EAAYlThMWakQBRdYv4ifF30c9hUCawmde3hpn375uU6znZCLwR9DZAXxDHf1rsJCTwYs2HlKm1kEYbnQhV4akdzoSV9gdhlWtqp2hFCK45LlwariYMcfUarkS5kp4Quy1V0IfM13pHspJ6gyld9YOFB7ODJTwDGAZA605DIPx2L66BgfZCb7l6xEpBMUMM9nbNnjUP1vSZCOAyZCQ86stB6bWTfmArXLifT2Crgfog8NR3eIXNOZB2287PbXkwgDyG4DsKCE6j23oKprqSrF7mLX8O0YAd0iZBGovMAZDZD"
ACCOUNT   = "act_2087839325471724"
ML_TOKEN  = json.loads(Path("tokens_cuenta1.json").read_text())["access_token"]
BASE_META = "https://graph.facebook.com/v21.0"
BASE_ML   = "https://api.mercadolibre.com"
ML_H      = {"Authorization": f"Bearer {ML_TOKEN}"}

# Items de lavaplatos a usar para el carrusel 1A
ITEMS_CAROUSEL = [
    ("MLC1524613378", "Lavaplatos 80x44 Inox",           "victtorino.cl/categoria/lavaplatos"),
    ("MLC2227061028", "Pack Lavaplatos 80x44 + Accesorios", "victtorino.cl/categoria/lavaplatos"),
    ("MLC1711075051", "Lavaplatos Doble 120x44",          "victtorino.cl/categoria/lavaplatos"),
    ("MLC2101080396", "Lavaplatos 80x50 + Llave",         "victtorino.cl/categoria/lavaplatos"),
]

# Item para imagen unica 1B (Shower & Receptaculos)
ITEM_1B = "MLC3146811724"  # Lavaplatos 55x43 — si no hay receptaculo disponible usar este

def get_best_photo_url(item_id):
    """Obtiene la URL JPEG de la foto de mayor resolucion del item ML."""
    r = requests.get(f"{BASE_ML}/items/{item_id}", headers=ML_H)
    if r.status_code != 200:
        return None, None, None
    data = r.json()
    title = data.get("title", item_id)
    pics = data.get("pictures", [])
    if not pics:
        return None, title, None

    # Preferir fotos JPG primero, luego convertir webp a jpg via URL
    def max_height(p):
        ms = p.get("max_size", "0x0")
        try:
            return int(ms.split("x")[1])
        except:
            return 0

    # Ordenar por resolucion descendente
    sorted_pics = sorted(pics, key=max_height, reverse=True)

    # Intentar primero las que son JPG
    jpg_pics = [p for p in sorted_pics if ".jpg" in (p.get("secure_url") or "")]
    best = jpg_pics[0] if jpg_pics else sorted_pics[0]

    url = best.get("secure_url") or best.get("url")
    # Si es webp, cambiar extension a jpg (ML CDN suele aceptar esto)
    if url and ".webp" in url:
        url = url.replace(".webp", ".jpg")

    return url, title, best.get("max_size")

def download_image(url, filename):
    """Descarga imagen y la guarda localmente."""
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return False
    Path(filename).write_bytes(r.content)
    return True

def upload_to_meta(filepath):
    """Sube imagen a Meta Ads y retorna el hash."""
    with open(filepath, "rb") as f:
        content = f.read()
    # Verificar que es JPEG valido (empieza con FF D8)
    if content[:2] != b'\xff\xd8':
        print(f"  Archivo no es JPEG valido (magic={content[:4].hex()})")
        return None
    r = requests.post(
        f"{BASE_META}/{ACCOUNT}/adimages",
        data={"access_token": META_TOKEN},
        files={"filename": (Path(filepath).name, content, "image/jpeg")}
    )
    resp = r.json()
    if "images" in resp:
        images = resp["images"]
        hash_val = list(images.values())[0].get("hash")
        return hash_val
    elif "error" in resp:
        e = resp["error"]
        print(f"  Error Meta: {e.get('message')} | {e.get('error_user_msg','')}")
        return None
    return None

print("=" * 60)
print("DESCARGANDO Y SUBIENDO FOTOS A META ADS")
print("=" * 60)

results = {"carousel_1a": [], "imagen_1b": None}
Path("temp_fotos").mkdir(exist_ok=True)

# ── Carrusel 1A: Lavaplatos ──────────────────────────────────────────────────
print("\n[CARRUSEL 1A] Procesando 4 fotos de lavaplatos...")
for i, (item_id, label, url_dest) in enumerate(ITEMS_CAROUSEL, 1):
    print(f"\n  Tarjeta {i}: {label} ({item_id})")

    photo_url, title, max_size = get_best_photo_url(item_id)
    if not photo_url:
        print(f"    Sin foto disponible")
        continue

    print(f"    Foto ML: {max_size} -> descargando...")
    ext = "jpg"
    filename = f"temp_fotos/carousel_1a_{i}_{item_id}.jpg"

    if not download_image(photo_url, filename):
        print(f"    Error descargando")
        continue

    size_kb = Path(filename).stat().st_size // 1024
    print(f"    Descargada: {size_kb} KB -> subiendo a Meta...")

    hash_val = upload_to_meta(filename)
    if hash_val:
        results["carousel_1a"].append({
            "tarjeta": i,
            "item_id": item_id,
            "label": label,
            "hash": hash_val,
            "url_destino": f"https://{url_dest}"
        })
        print(f"    OK — hash: {hash_val}")
    time.sleep(0.5)

# ── Imagen 1B: Shower & Receptaculos ────────────────────────────────────────
print(f"\n[IMAGEN 1B] Buscando foto para Shower/Receptaculos...")
# Buscar receptaculos en C1
search = requests.get(
    f"{BASE_ML}/users/483903060/items/search?q=receptaculo+ducha&limit=5",
    headers=ML_H
).json()

item_1b_id = None
if search.get("results"):
    item_1b_id = search["results"][0]
    print(f"  Encontrado: {item_1b_id}")
else:
    item_1b_id = ITEM_1B
    print(f"  Usando lavaplatos como placeholder: {item_1b_id}")

photo_url, title, max_size = get_best_photo_url(item_1b_id)
if photo_url:
    filename = f"temp_fotos/imagen_1b_{item_1b_id}.jpg"
    print(f"  Foto: {max_size} -> descargando...")
    if download_image(photo_url, filename):
        size_kb = Path(filename).stat().st_size // 1024
        print(f"  Descargada: {size_kb} KB -> subiendo a Meta...")
        hash_val = upload_to_meta(filename)
        if hash_val:
            results["imagen_1b"] = {"item_id": item_1b_id, "hash": hash_val}
            print(f"  OK — hash: {hash_val}")

# ── Guardar resultados ───────────────────────────────────────────────────────
with open("meta_imagenes_hashes.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print(f"Carrusel 1A: {len(results['carousel_1a'])} fotos subidas")
for card in results["carousel_1a"]:
    print(f"  Tarjeta {card['tarjeta']}: {card['label']} -> hash={card['hash']}")
if results["imagen_1b"]:
    print(f"Imagen 1B: hash={results['imagen_1b']['hash']}")
print("\nHashes guardados en meta_imagenes_hashes.json")
print("Proximo paso: crear anuncios con estos hashes")
