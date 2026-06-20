# -*- coding: utf-8 -*-
"""
Crear anuncios (creatividades + ads) en Meta Ads para Victtorino.
Usa los hashes de imagen previamente subidos.
"""
import json, requests, time, sys
from pathlib import Path

TOKEN    = "EAAYlThMWakQBRdYv4ifF30c9hUCawmde3hpn375uU6znZCLwR9DZAXxDHf1rsJCTwYs2HlKm1kEYbnQhV4akdzoSV9gdhlWtqp2hFCK45LlwariYMcfUarkS5kp4Quy1V0IfM13pHspJ6gyld9YOFB7ODJTwDGAZA605DIPx2L66BgfZCb7l6xEpBMUMM9nbNnjUP1vSZCOAyZCQ86stB6bWTfmArXLifT2Crgfog8NR3eIXNOZB2287PbXkwgDyG4DsKCE6j23oKprqSrF7mLX8O0YAd0iZBGovMAZDZD"
ACCOUNT  = "act_2087839325471724"
PAGE_ID  = "1340666836072901"
PIXEL_ID = "1361965342502798"
BASE     = "https://graph.facebook.com/v21.0"

# IDs de ad sets creados anteriormente
ADSET_1A = "120249078453230066"  # Lavaplatos
ADSET_1B = "120249078454060066"  # Shower & Receptaculos

# Hashes de imagenes subidas
hashes = json.loads(Path("meta_imagenes_hashes.json").read_text())
H1 = hashes["carousel_1a"][0]["hash"]  # 80x44
H2 = hashes["carousel_1a"][1]["hash"]  # Pack 80x44
H3 = hashes["carousel_1a"][2]["hash"]  # Doble 120x44
H4 = hashes["carousel_1a"][3]["hash"]  # 80x50 + Llave
H_1B = hashes["imagen_1b"]["hash"]     # Shower

URL_LAVAPLATOS   = "https://victtorino.cl/categoria-producto/lavaplatos/"
URL_RECEPTACULOS = "https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/"

# UTM estandar (ver CONVENCION_UTM.md). Las macros {{...}} las rellena Meta por anuncio.
URL_TAGS = "utm_source=facebook&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}"

def api_post(path, payload):
    payload["access_token"] = TOKEN
    r = requests.post(f"{BASE}/{path}", json=payload)
    return r.json()

def check(resp, label):
    if "error" in resp:
        e = resp["error"]
        print(f"  ERROR [{label}]: {e.get('message')} | {e.get('error_user_msg','')}")
        return False
    return True

results = {}

# ════════════════════════════════════════════════════════════════════════════
# CREATIVE 1A — CARRUSEL LAVAPLATOS
# ════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("CREANDO CREATIVE 1A — Carrusel Lavaplatos")
print("=" * 60)

creative_1a = api_post(f"{ACCOUNT}/adcreatives", {
    "name": "Creative 1A - Lavaplatos Carrusel",
    "url_tags": URL_TAGS,
    "object_story_spec": {
        "page_id": PAGE_ID,
        "link_data": {
            "link": URL_LAVAPLATOS,
            "message": (
                "¿Renovando tu cocina? \U0001f3e0\n\n"
                "Los lavaplatos de acero inoxidable Victtorino tienen el mejor precio de Chile "
                "— con envío desde $2.490 a todo el país.\n\n"
                "✅ Acero inoxidable premium\n"
                "✅ Múltiples tamaños disponibles\n"
                "✅ Envío rápido a todo Chile\n"
                "✅ Hasta 12 cuotas sin interés\n\n"
                "Ver catálogo completo \U0001f447"
            ),
            "child_attachments": [
                {
                    "link": URL_LAVAPLATOS,
                    "name": "Lavaplatos Inox 80x44",
                    "description": "Desde $49.990 · Envío gratis",
                    "image_hash": H1,
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": URL_LAVAPLATOS}}
                },
                {
                    "link": URL_LAVAPLATOS,
                    "name": "Pack Lavaplatos + Accesorios",
                    "description": "Pack completo listo para instalar",
                    "image_hash": H2,
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": URL_LAVAPLATOS}}
                },
                {
                    "link": URL_LAVAPLATOS,
                    "name": "Lavaplatos Doble 120x44",
                    "description": "El mas vendido · Stock disponible hoy",
                    "image_hash": H3,
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": URL_LAVAPLATOS}}
                },
                {
                    "link": URL_LAVAPLATOS,
                    "name": "Lavaplatos 80x50 + Llave",
                    "description": "Envío a todo Chile desde $2.490",
                    "image_hash": H4,
                    "call_to_action": {"type": "SHOP_NOW", "value": {"link": URL_LAVAPLATOS}}
                }
            ],
            "call_to_action": {"type": "SHOP_NOW"}
        }
    }
})

if not check(creative_1a, "Creative 1A"):
    print("  Intentando formato alternativo...")
    sys.exit(1)

creative_1a_id = creative_1a["id"]
results["creative_1a_id"] = creative_1a_id
print(f"  Creative 1A creado: {creative_1a_id}")
time.sleep(0.5)

# ── Anuncio 1A ───────────────────────────────────────────────────────────────
print("\nCreando Anuncio 1A...")
ad_1a = api_post(f"{ACCOUNT}/ads", {
    "name": "Ad 1A - Lavaplatos Carrusel",
    "adset_id": ADSET_1A,
    "creative": {"creative_id": creative_1a_id},
    "status": "PAUSED"
})

if check(ad_1a, "Ad 1A"):
    results["ad_1a_id"] = ad_1a["id"]
    print(f"  Anuncio 1A creado: {ad_1a['id']}")
time.sleep(0.5)

# ════════════════════════════════════════════════════════════════════════════
# CREATIVE 1B — IMAGEN SHOWER & RECEPTACULOS
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CREANDO CREATIVE 1B - Shower & Receptaculos")
print("=" * 60)

creative_1b = api_post(f"{ACCOUNT}/adcreatives", {
    "name": "Creative 1B - Shower Imagen",
    "url_tags": URL_TAGS,
    "object_story_spec": {
        "page_id": PAGE_ID,
        "link_data": {
            "message": (
                "Tu baño merece una transformación ✨\n\n"
                "Recáptaculos de ducha y mamparas con diseño premium "
                "— fabricados en acero y acrílico de alta resistencia.\n\n"
                "\U0001f4e6 Despacho a todo Chile\n"
                "\U0001f4b3 Paga en cuotas sin interés\n"
                "\U0001f527 Fácil instalación\n\n"
                "¡Cotiza ahora y transforma tu baño!"
            ),
            "link": URL_RECEPTACULOS,
            "name": "Baños modernos desde $43.000",
            "description": "Envío a todo Chile · Stock disponible",
            "image_hash": H_1B,
            "call_to_action": {"type": "LEARN_MORE", "value": {"link": URL_RECEPTACULOS}}
        }
    }
})

if not check(creative_1b, "Creative 1B"):
    sys.exit(1)

creative_1b_id = creative_1b["id"]
results["creative_1b_id"] = creative_1b_id
print(f"  Creative 1B creado: {creative_1b_id}")
time.sleep(0.5)

# ── Anuncio 1B ───────────────────────────────────────────────────────────────
print("\nCreando Anuncio 1B...")
ad_1b = api_post(f"{ACCOUNT}/ads", {
    "name": "Ad 1B - Shower Imagen",
    "adset_id": ADSET_1B,
    "creative": {"creative_id": creative_1b_id},
    "status": "PAUSED"
})

if check(ad_1b, "Ad 1B"):
    results["ad_1b_id"] = ad_1b["id"]
    print(f"  Anuncio 1B creado: {ad_1b['id']}")

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
for k, v in results.items():
    print(f"  {k}: {v}")

print("""
ESTADO:
  - Todos los anuncios en PAUSED
  - Campana 1 lista para activar cuando quieras
  - Para activar: Meta Ads Manager -> seleccionar campana -> activar
  - Campana 3 (Instagram): necesita creatividades de contenido (fotos estilo Instagram)
  - Campana 2 (Remarketing): activar en 7 dias cuando el pixel tenga datos
""")

with open("meta_ads_completo.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Guardado en meta_ads_completo.json")
