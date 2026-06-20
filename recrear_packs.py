import requests, json, time, re
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")

token  = json.loads(Path("tokens_cuenta3.json").read_text())["access_token"]
H_JSON = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
H      = {"Authorization": f"Bearer {token}"}

GDRIVE_IDS = [
    "1_tIzcKDpjvp0iUcehFT8Hzs03RidfxLH",
    "1kWMwNry1xJPuUQrP9wf34xA-_21zqxtN",
    "176DibqcH4DXkTkvEJy0aOnb34el_CTYB",
    "1M8O8a4QDZOwIk96Q2VIkqV2INIqVI6_j",
    "1ED9uJi8ta9SZXF7qmkzLnq2FpgbjvypV",
    "133vLc_u0UoXMhb8wONtvObLclmjEez2U",
    "11J8ljo8EgiNur2Mz9X-O6rOeVSdZwKIq",
]

def download_gdrive(file_id):
    session = requests.Session()
    r = session.get("https://drive.google.com/uc",
                    params={"export": "download", "id": file_id, "confirm": "t"}, stream=True)
    r.raise_for_status()
    if "text/html" in r.headers.get("Content-Type", ""):
        m = re.search(r"confirm=([0-9A-Za-z_\-]+)", r.text)
        if m:
            r = session.get("https://drive.google.com/uc",
                            params={"export": "download", "id": file_id, "confirm": m.group(1)},
                            stream=True)
    return r.content

def upload_photo(img_bytes, fname):
    r = requests.post("https://api.mercadolibre.com/pictures/items/upload",
                      headers={"Authorization": f"Bearer {token}"},
                      files={"file": (fname, img_bytes, "image/jpeg")})
    return r.json().get("id") if r.ok else None

# ── PASO 1: Cerrar listings anteriores ───────────────────────────
for iid in ["MLC1953791447", "MLC1953819727"]:
    r = requests.put(f"https://api.mercadolibre.com/items/{iid}",
                     headers=H_JSON, json={"status": "closed"})
    print(f"Cerrado {iid}: {r.status_code}")
time.sleep(2)

# ── PASO 2: Subir 7 fotos frescas ────────────────────────────────
print("\nSubiendo fotos...")
pic_ids = []
for i, gid in enumerate(GDRIVE_IDS, 1):
    img = download_gdrive(gid)
    pid = upload_photo(img, f"pack_{i}.jpg")
    if pid:
        pic_ids.append({"id": pid})
        print(f"  Foto {i}/7: OK")
print(f"Total fotos: {len(pic_ids)}")

ATTRS_COMUNES = [
    {"id": "IS_KIT",             "value_name": "Si"},
    {"id": "INCLUDES_FAUCET",    "value_name": "Si"},
    {"id": "MATERIAL",           "value_name": "Acero inoxidable"},
    {"id": "MAIN_COLOR",         "value_id": "2450303", "value_name": "Plateado"},
    {"id": "KITCHEN_SINKS_TYPE", "value_name": "Simple"},
    {"id": "INSTALLATION_TYPES", "value_name": "Empotrado"},
    {"id": "SHAPE",              "value_name": "Rectangular"},
    {"id": "LENGTH",             "value_name": "80 cm"},
    {"id": "WIDTH",              "value_name": "44 cm"},
    {"id": "DEPTH",              "value_name": "14 cm"},
    {"id": "THICKNESS",          "value_name": "0.5 mm"},
    {"id": "SELLER_PACKAGE_LENGTH", "value_name": "85 cm"},
    {"id": "SELLER_PACKAGE_WIDTH",  "value_name": "50 cm"},
    {"id": "SELLER_PACKAGE_HEIGHT", "value_name": "17 cm"},
    {"id": "SELLER_PACKAGE_WEIGHT", "value_name": "3500 g"},
]

LISTINGS = [
    {
        "label":       "DERECHO",
        "family_name": "Pack Lavaplatos 80x44 Sec Der + Llave Monomando + Canastillo",
        "gtin":        "659576865423",
        "model":       "Pack 80x44 Sec Der + Llave Colomba + Canastillo",
        "secador":     "Derecho",
    },
    {
        "label":       "IZQUIERDO",
        "family_name": "Pack Lavaplatos 80x44 Sec Izq + Llave Monomando + Canastillo",
        "gtin":        "752853007834",
        "model":       "Pack 80x44 Sec Izq + Llave Colomba + Canastillo",
        "secador":     "Izquierdo",
    },
]

for lst in LISTINGS:
    print(f"\n--- Creando {lst['label']} ---")
    time.sleep(1)

    body = {
        "family_name":       lst["family_name"],
        "category_id":       "MLC454694",
        "price":             56990,
        "currency_id":       "CLP",
        "available_quantity": 3,
        "buying_mode":       "buy_it_now",
        "condition":         "new",
        "listing_type_id":   "gold_pro",
        "pictures":          pic_ids[:1],
        "attributes": [
            {"id": "BRAND",  "value_name": "Taumm"},
            {"id": "MODEL",  "value_name": lst["model"]},
            {"id": "GTIN",   "value_name": lst["gtin"]},
            {"id": "IS_KIT", "value_name": "Si"},
            {"id": "MAIN_COLOR", "value_id": "2450303", "value_name": "Plateado"},
            {"id": "SELLER_PACKAGE_LENGTH", "value_name": "85 cm"},
            {"id": "SELLER_PACKAGE_WIDTH",  "value_name": "50 cm"},
            {"id": "SELLER_PACKAGE_HEIGHT", "value_name": "17 cm"},
            {"id": "SELLER_PACKAGE_WEIGHT", "value_name": "3500 g"},
        ],
    }

    r = requests.post("https://api.mercadolibre.com/items", headers=H_JSON, json=body)
    d = r.json()
    if not r.ok:
        cause = d.get("cause", [])
        errs = [c.get("message", "") for c in cause] if isinstance(cause, list) else [str(cause)]
        print(f"  ERROR: {errs}")
        continue

    ITEM_ID = d.get("id")
    print(f"  Creado: {ITEM_ID}")
    time.sleep(1)

    # PUT atributos completos + fotos
    r2 = requests.put(f"https://api.mercadolibre.com/items/{ITEM_ID}", headers=H_JSON, json={
        "pictures":   pic_ids,
        "sale_terms": [
            {"id": "WARRANTY_TYPE", "value_name": "Garantia del vendedor"},
            {"id": "WARRANTY_TIME", "value_name": "5 anos"},
        ],
        "attributes": [
            {"id": "BRAND", "value_name": "Taumm"},
            {"id": "MODEL", "value_name": lst["model"]},
        ] + ATTRS_COMUNES,
    })
    print(f"  PUT atributos: {r2.status_code}")
    time.sleep(1)

    desc = (
        f"TODO LO QUE NECESITAS PARA TU COCINA EN UN SOLO PACK\n\n"
        f"Instala tu nueva cocina sin complicaciones. Pack lavaplatos acero inoxidable "
        f"+ llave monomando + canastillo de cocina.\n\n"
        f"LAVAPLATOS 80x44 ACERO INOX:\n"
        f"- Material: Acero inoxidable 201 | Medidas: 80x44x14 cm | Secador: {lst['secador']}\n"
        f"- Espesor: 0,5 mm | Bowl: 34x40 cm\n"
        f"- Incluye: Desague con tubo rebalse + cinta sello\n\n"
        f"LLAVE MONOMANDO VERTICAL COLOMBA:\n"
        f"- Cuerpo y manilla zamak cromado | Cartucho ceramico 35mm | Aireador ahorro agua\n"
        f"- Resistencia: 16 bar | Altura: 310 mm | Garantia: 5 anos\n"
        f"- Incluye: Kit anclaje + 2 flexibles 35cm acero inox\n\n"
        f"CANASTILLO DE COCINA incluido en el pack.\n\n"
        f"QUE INCLUYE:\n"
        f"- Lavaplatos 80x44 secador {lst['secador'].lower()}\n"
        f"- Llave monomando vertical Colomba cromada\n"
        f"- Canastillo de cocina\n"
        f"- Desague con tubo rebalse + cinta sello\n"
        f"- Kit de anclaje completo\n"
        f"- 2 flexibles de 35cm acero inoxidable\n\n"
        f"Marca: Taumm | Material: Acero inoxidable 201 | Garantia: 5 anos"
    )
    r3 = requests.post(f"https://api.mercadolibre.com/items/{ITEM_ID}/description",
                       headers=H_JSON, json={"plain_text": desc})
    print(f"  DESC: {r3.status_code}")

    d4 = requests.get(f"https://api.mercadolibre.com/items/{ITEM_ID}", headers=H).json()
    print(f"  Titulo: {d4.get('title')}")
    print(f"  Status: {d4.get('status')} | Fotos: {len(d4.get('pictures', []))}")
    print(f"  URL: {d4.get('permalink', '')}")

print("\nListo.")
