"""
Crea la publicación: Pack Lavaplatos 80x44 + Llave Colomba Täumm + Canastillo
  1. Descarga fotos desde Google Drive
  2. Sube fotos a MercadoLibre
  3. Publica el ítem
  4. Agrega descripción
"""

import sys
import requests
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOKENS_FILE = Path(__file__).parent / "tokens_cuenta3.json"
BASE_URL    = "https://api.mercadolibre.com"

# IDs de archivos en Google Drive — fotos del pack (lavaplatos der + llave + canastillo)
GDRIVE_IDS = [
    # Carpeta 1: rejilla/canastillo
    "1_tIzcKDpjvp0iUcehFT8Hzs03RidfxLH",
    "1kWMwNry1xJPuUQrP9wf34xA-_21zqxtN",
    "176DibqcH4DXkTkvEJy0aOnb34el_CTYB",
    # Carpeta 2: pack completo
    "1M8O8a4QDZOwIk96Q2VIkqV2INIqVI6_j",
    "1ED9uJi8ta9SZXF7qmkzLnq2FpgbjvypV",
    "133vLc_u0UoXMhb8wONtvObLclmjEez2U",
    "11J8ljo8EgiNur2Mz9X-O6rOeVSdZwKIq",
]

DESCRIPCION = """TODO LO QUE NECESITAS PARA TU COCINA EN UN SOLO PACK

Instala tu nueva cocina sin complicaciones. Este pack incluye lavaplatos de acero inoxidable + llave monomando + canastillo de cocina, listos para usar desde el primer dia.

LAVAPLATOS 80x44 ACERO INOX:
- Material: Acero inoxidable 201
- Medidas: 80 x 44 x 14 cm
- Secador: Derecho
- Espesor: 0,5 mm
- Bowl: 34 x 40 cm
- Incluye: Desague con tubo rebalse + cinta sello

LLAVE MONOMANDO VERTICAL COLOMBA:
- Cuerpo y manilla de zamak cromado
- Cartucho ceramico de 35 mm
- Aireador con ahorro de agua
- Resistencia hidrostatica: 16 bar
- Altura total: 310 mm
- Garantia: 5 anos
- Incluye: Kit anclaje + 2 flexibles 35 cm acero inox

CANASTILLO DE COCINA:
- Incluido en el pack

QUE INCLUYE EL PACK:
- Lavaplatos 80x44 secador derecho
- Llave monomando vertical Colomba cromada
- Canastillo de cocina
- Desague con tubo rebalse
- Cinta sello
- Kit de anclaje completo
- 2 flexibles de 35 cm

ATRIBUTOS:
- Marca: Taumm
- Material: Acero inoxidable 201
- Medidas: 80 x 44 x 14 cm
- Color: Plateado/Cromado
- Garantia: 5 anos"""

ITEM_BODY = {
    "title": "Pack Lavaplatos 80x44 Sec Der + Llave Colomba Taumm + Canastillo",
    "category_id": "MLC454694",
    "price": 56990,
    "currency_id": "CLP",
    "available_quantity": 3,
    "buying_mode": "buy_it_now",
    "condition": "new",
    "listing_type_id": "gold_pro",
    "sale_terms": [
        {"id": "WARRANTY_TYPE", "value_name": "Garantía del vendedor"},
        {"id": "WARRANTY_TIME", "value_name": "5 años"},
    ],
    "family_name": "",
    "shipping": {
        "mode": "me2",
        "free_shipping": False,
    },
    "attributes": [
        {"id": "BRAND",                     "value_name": "Täumm"},
        {"id": "MODEL",                     "value_name": "Pack Lavaplatos 80x44 Der + Llave Colomba + Canastillo"},
        {"id": "ALPHANUMERIC_MODEL",        "value_name": "PACK-LV8044D-COLOMBA-CAN"},
        {"id": "KITCHEN_SINKS_TYPE",        "value_name": "Simple"},
        {"id": "INSTALLATION_TYPES",        "value_name": "Empotrado"},
        {"id": "MATERIAL",                  "value_name": "Acero inoxidable"},
        {"id": "FINISH",                    "value_name": "Cromado"},
        {"id": "SHAPE",                     "value_name": "Rectangular"},
        {"id": "MAIN_COLOR",                "value_id": "2450303", "value_name": "Plateado"},
        {"id": "LENGTH",                    "value_name": "80"},
        {"id": "WIDTH",                     "value_name": "44"},
        {"id": "DEPTH",                     "value_name": "14"},
        {"id": "THICKNESS",                 "value_name": "0.5"},
        {"id": "INCLUDES_FAUCET",           "value_name": "Sí"},
        {"id": "INCLUDES_ACCESSORIES",      "value_name": "Sí"},
        {"id": "IS_KIT",                    "value_name": "Sí"},
        {"id": "EMPTY_GTIN_REASON",         "value_id": "17055159",
                                            "value_name": "El producto es un kit o un pack"},
        {"id": "IS_SUITABLE_FOR_SHIPMENT",  "value_name": "Sí"},
        {"id": "HAS_COMPATIBILITIES",       "value_name": "No"},
        {"id": "IS_FLAMMABLE",              "value_name": "No"},
        {"id": "WITH_POSITIVE_IMPACT",      "value_name": "No"},
    ],
}


def load_token():
    return json.loads(TOKENS_FILE.read_text())["access_token"]


def headers(content_type=None):
    h = {"Authorization": f"Bearer {load_token()}"}
    if content_type:
        h["Content-Type"] = content_type
    return h


def download_gdrive(file_id):
    """Descarga un archivo de Google Drive (maneja confirmación para archivos >100KB)."""
    session = requests.Session()
    url = "https://drive.google.com/uc"
    params = {"export": "download", "id": file_id, "confirm": "t"}
    r = session.get(url, params=params, stream=True)
    r.raise_for_status()
    # Si devuelve HTML (página de confirmación), extraer token y reintentar
    if "text/html" in r.headers.get("Content-Type", ""):
        import re
        match = re.search(r'confirm=([0-9A-Za-z_\-]+)', r.text)
        if match:
            params["confirm"] = match.group(1)
            r = session.get(url, params=params, stream=True)
            r.raise_for_status()
    return r.content


def upload_foto(image_bytes, filename="foto.jpg"):
    """Sube una imagen a MercadoLibre y retorna el picture_id."""
    r = requests.post(
        f"{BASE_URL}/pictures/items/upload",
        headers={"Authorization": f"Bearer {load_token()}"},
        files={"file": (filename, image_bytes, "image/jpeg")},
    )
    if not r.ok:
        print(f"  ERROR subiendo {filename}: {r.status_code} {r.text[:200]}")
        return None
    data = r.json()
    pic_id = data.get("id") or (data.get("variations", [{}])[0].get("url"))
    return data


def main():
    print("\n" + "="*60)
    print("  PUBLICANDO: Pack Lavaplatos 80x44 + Llave Colomba Täumm")
    print("="*60)

    # ── PASO 1: Descargar y subir fotos ──────────────────────────
    print("\n[1/4] Descargando fotos desde Google Drive...")
    picture_ids = []

    for i, gid in enumerate(GDRIVE_IDS, 1):
        print(f"  Foto {i}/3: descargando id={gid}...", end=" ")
        try:
            img_bytes = download_gdrive(gid)
            print(f"OK ({len(img_bytes)//1024} KB) — subiendo a ML...", end=" ")
            data = upload_foto(img_bytes, f"pack_lv_{i}.jpg")
            if data:
                pic_id = data.get("id")
                if pic_id:
                    picture_ids.append({"id": pic_id})
                    print(f"OK → id={pic_id}")
                else:
                    # Intentar con URL directa
                    url = data.get("variations", [{}])[0].get("url", "")
                    if url:
                        picture_ids.append({"source": url})
                        print(f"OK → {url[:60]}")
                    else:
                        print(f"SIN ID — respuesta: {json.dumps(data)[:100]}")
            else:
                print("FALLO")
        except Exception as e:
            print(f"ERROR: {e}")

    if not picture_ids:
        print("\n  ✗ No se pudieron subir fotos. Abortando.")
        return

    print(f"\n  {len(picture_ids)} foto(s) subidas correctamente.")

    # ── PASO 2: Agregar fotos al cuerpo ──────────────────────────
    print("\n[2/4] Construyendo body de la publicación...")
    body = dict(ITEM_BODY)
    body["pictures"] = picture_ids
    print(f"  Fotos incluidas: {len(picture_ids)}")

    # ── PASO 3: Crear publicación ────────────────────────────────
    print("\n[3/4] Enviando POST /items...")
    r = requests.post(
        f"{BASE_URL}/items",
        headers=headers("application/json"),
        json=body,
    )

    if not r.ok:
        print(f"\n  ✗ Error al crear publicación: {r.status_code}")
        err = r.json()
        print(f"  {json.dumps(err, ensure_ascii=False, indent=2)[:800]}")
        return

    item = r.json()
    item_id = item.get("id")
    permalink = item.get("permalink", "")
    print(f"\n  ✓ Publicación creada: {item_id}")
    print(f"  URL: {permalink}")

    # Guardar respuesta
    Path(__file__).parent.joinpath("nuevo_item.json").write_text(
        json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # ── PASO 4: Agregar descripción ──────────────────────────────
    print("\n[4/4] Agregando descripción...")
    time.sleep(1)
    r2 = requests.post(
        f"{BASE_URL}/items/{item_id}/description",
        headers=headers("application/json"),
        json={"plain_text": DESCRIPCION},
    )
    if r2.ok:
        print("  ✓ Descripción agregada.")
    else:
        print(f"  ✗ Error descripción: {r2.status_code} {r2.text[:200]}")

    # ── RESUMEN ───────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  PUBLICACIÓN LISTA")
    print(f"  ID       : {item_id}")
    print(f"  Precio   : $56,990 CLP")
    print(f"  Stock    : 3")
    print(f"  Estado   : {item.get('status')}")
    print(f"  URL      : {permalink}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
