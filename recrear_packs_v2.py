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

LOCAL_FOTOS = {
    "der":  Path("C:/Users/dell/OneDrive/Imágenes/80x44 Derecho .png"),
    "izq1": Path("C:/Users/dell/OneDrive/Imágenes/80x44 Izquierdo.png"),
    "izq2": Path("C:/Users/dell/OneDrive/Imágenes/80x44 Izquierdo 2.png"),
}

FOTOS_TECNICAS_DER = [
    "http://http2.mlstatic.com/D_610833-MLC110556604415_042026-O.webp",
    "http://http2.mlstatic.com/D_648185-MLC104682673841_012026-O.webp",
    "http://http2.mlstatic.com/D_862254-MLC109671865412_042026-O.webp",
    "http://http2.mlstatic.com/D_923911-MLC109467035191_032026-O.jpg",
]
FOTOS_TECNICAS_IZQ = [
    "http://http2.mlstatic.com/D_691282-MLC91744053644_092025-O.webp",
    "http://http2.mlstatic.com/D_633870-MLC92145225747_092025-O.webp",
    "http://http2.mlstatic.com/D_769695-MLC92145186339_092025-O.webp",
    "http://http2.mlstatic.com/D_645778-MLC92145117131_092025-O.webp",
]
FOTOS_LLAVE = [
    "http://http2.mlstatic.com/D_612228-MLC92318976149_092025-O.webp",
    "http://http2.mlstatic.com/D_745388-MLU70020658053_062023-O.jpg",
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


def upload_bytes(img_bytes, fname, mime="image/jpeg"):
    r = requests.post("https://api.mercadolibre.com/pictures/items/upload",
                      headers={"Authorization": f"Bearer {token}"},
                      files={"file": (fname, img_bytes, mime)})
    return r.json().get("id") if r.ok else None


def upload_local(path, fname):
    with open(path, "rb") as f:
        return upload_bytes(f.read(), fname, "image/png")


# ── PASO 1: Cerrar versiones anteriores ──────────────────────────
for iid in ["MLC1953768761", "MLC1953729411"]:
    r = requests.put(f"https://api.mercadolibre.com/items/{iid}",
                     headers=H_JSON, json={"status": "closed"})
    print(f"Cerrado {iid}: {r.status_code}")
time.sleep(2)

# ── PASO 2: Subir fotos frescas desde Drive ───────────────────────
print("\nSubiendo fotos desde Drive...")
drive_pics = []
for i, gid in enumerate(GDRIVE_IDS, 1):
    pid = upload_bytes(download_gdrive(gid), f"pack_{i}.jpg")
    if pid:
        drive_pics.append({"id": pid})
        print(f"  Drive {i}/7: OK")

# Fotos locales
print("Subiendo fotos locales...")
pid_der  = upload_local(LOCAL_FOTOS["der"],  "80x44_derecho.png")
pid_izq2 = upload_local(LOCAL_FOTOS["izq2"], "80x44_izquierdo2.png")
try:
    pid_izq1 = upload_local(LOCAL_FOTOS["izq1"], "80x44_izquierdo.png")
except:
    pid_izq1 = None

print(f"  Local der: {'OK' if pid_der else 'FALLO'}")
print(f"  Local izq: {'OK' if pid_izq1 or pid_izq2 else 'FALLO'}")

# Armar listas de fotos por listing
def build_pics(local_ids, tecnicas):
    pics = []
    for pid in local_ids:
        if pid:
            pics.append({"id": pid})
    pics += drive_pics
    pics += [{"source": u} for u in tecnicas]
    pics += [{"source": u} for u in FOTOS_LLAVE]
    return pics[:12]

FOTOS_DER = build_pics([pid_der], FOTOS_TECNICAS_DER)
FOTOS_IZQ = build_pics([pid_izq1, pid_izq2], FOTOS_TECNICAS_IZQ)

print(f"\nFotos preparadas — Der: {len(FOTOS_DER)}, Izq: {len(FOTOS_IZQ)}")

# ── ATRIBUTOS ─────────────────────────────────────────────────────
ATTRS_BASE = [
    {"id": "BRAND",                 "value_name": "Täumm"},
    {"id": "IS_KIT",                "value_name": "Sí"},
    {"id": "INCLUDES_FAUCET",       "value_name": "Sí"},
    {"id": "FAUCET_HOLES_NUMBER",   "value_name": "1"},
    {"id": "MATERIAL",              "value_name": "Acero inoxidable"},
    {"id": "FINISH",                "value_name": "Cepillado"},
    {"id": "SHAPE",                 "value_name": "Rectangular"},
    {"id": "MAIN_COLOR",            "value_id": "2450303", "value_name": "Plateado"},
    {"id": "KITCHEN_SINKS_TYPE",    "value_name": "Simple"},
    {"id": "INSTALLATION_TYPES",    "value_name": "Empotrado"},
    {"id": "LENGTH",                "value_name": "80 cm"},
    {"id": "WIDTH",                 "value_name": "44 cm"},
    {"id": "DEPTH",                 "value_name": "20 cm"},
    {"id": "THICKNESS",             "value_name": "0.5 mm"},
    {"id": "WITH_DETERGENT_DISPENSER", "value_name": "No"},
    {"id": "SELLER_PACKAGE_LENGTH", "value_name": "85 cm"},
    {"id": "SELLER_PACKAGE_WIDTH",  "value_name": "50 cm"},
    {"id": "SELLER_PACKAGE_HEIGHT", "value_name": "17 cm"},
    {"id": "SELLER_PACKAGE_WEIGHT", "value_name": "3500 g"},
]

# ── LISTINGS ──────────────────────────────────────────────────────
LISTINGS = [
    {
        "label":       "DERECHO",
        "family_name": "Lavaplatos 80x44 Acero Inox Pack Llave Canastillo Derecho",
        "gtin":        "659576865423",
        "model":       "Pack 80x44 Secador Derecho + Llave Colomba + Canastillo",
        "secador":     "Derecho",
        "fotos":       FOTOS_DER,
    },
    {
        "label":       "IZQUIERDO",
        "family_name": "Lavaplatos 80x44 Acero Inox Pack Llave Canastillo Izquierdo",
        "gtin":        "752853007834",
        "model":       "Pack 80x44 Secador Izquierdo + Llave Colomba + Canastillo",
        "secador":     "Izquierdo",
        "fotos":       FOTOS_IZQ,
    },
]

for lst in LISTINGS:
    print(f"\n{'='*55}")
    print(f"  Creando {lst['label']}...")
    time.sleep(1)

    body = {
        "family_name":        lst["family_name"],
        "category_id":        "MLC454694",
        "price":              56990,
        "currency_id":        "CLP",
        "available_quantity": 3,
        "buying_mode":        "buy_it_now",
        "condition":          "new",
        "listing_type_id":    "gold_pro",
        "pictures":           lst["fotos"][:1],
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
    print(f"  Creado: {ITEM_ID} | Título: {d.get('title')}")
    time.sleep(1)

    # PUT: fotos completas + atributos técnicos + garantía
    attrs_full = [{"id": "MODEL", "value_name": lst["model"]}] + ATTRS_BASE
    r2 = requests.put(f"https://api.mercadolibre.com/items/{ITEM_ID}", headers=H_JSON, json={
        "pictures":   lst["fotos"],
        "sale_terms": [
            {"id": "WARRANTY_TYPE", "value_name": "Garantía del vendedor"},
            {"id": "WARRANTY_TIME", "value_name": "5 años"},
        ],
        "attributes": attrs_full,
    })
    print(f"  PUT atributos + fotos: {r2.status_code}")
    time.sleep(1)

    # Descripción con tildes
    desc = (
        f"✅ TODO LO QUE NECESITAS PARA TU COCINA EN UN SOLO PACK\n\n"
        f"Instala tu nueva cocina sin complicaciones. Este pack incluye lavaplatos "
        f"de acero inoxidable + llave monomando Colomba + canastillo de cocina, "
        f"listos para usar desde el primer día.\n\n"
        f"LAVAPLATOS 80x44 ACERO INOX:\n"
        f"- Material: Acero inoxidable 201\n"
        f"- Medidas: 80 x 44 x 14 cm\n"
        f"- Secador: {lst['secador']}\n"
        f"- Espesor: 0,5 mm\n"
        f"- Bowl: 34 x 40 cm\n"
        f"- Incluye: Desagüe con tubo rebalse + cinta sello\n\n"
        f"LLAVE MONOMANDO VERTICAL COLOMBA:\n"
        f"- Cuerpo y manilla de zamak cromado\n"
        f"- Cartucho cerámico de 35 mm\n"
        f"- Aireador con ahorro de agua\n"
        f"- Resistencia hidrostática: 16 bar\n"
        f"- Altura total: 310 mm\n"
        f"- Garantía: 5 años\n"
        f"- Incluye: Kit anclaje + 2 flexibles 35 cm acero inox\n\n"
        f"CANASTILLO DE COCINA incluido en el pack.\n\n"
        f"✔ QUÉ INCLUYE EL PACK:\n"
        f"✔ Lavaplatos 80x44 secador {lst['secador'].lower()}\n"
        f"✔ Llave monomando vertical Colomba cromada\n"
        f"✔ Canastillo de cocina\n"
        f"✔ Desagüe con tubo rebalse\n"
        f"✔ Cinta sello\n"
        f"✔ Kit de anclaje completo\n"
        f"✔ 2 flexibles de 35 cm acero inoxidable\n\n"
        f"Marca: Täumm | Material: Acero inoxidable 201 | Medidas: 80x44x14 cm | Garantía: 5 años"
    )
    r3 = requests.post(f"https://api.mercadolibre.com/items/{ITEM_ID}/description",
                       headers=H_JSON, json={"plain_text": desc})
    print(f"  Descripción: {r3.status_code}")

    d4 = requests.get(f"https://api.mercadolibre.com/items/{ITEM_ID}", headers=H).json()
    print(f"  Título final: {d4.get('title')}")
    print(f"  Status: {d4.get('status')} | Fotos: {len(d4.get('pictures', []))}")
    print(f"  URL: {d4.get('permalink', '')}")

print("\n✅ Listo.")
