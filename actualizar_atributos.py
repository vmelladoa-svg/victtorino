"""
Actualiza atributos vacíos de publicaciones MercadoLibre.

Uso:
  python actualizar_atributos.py --generar   # genera atributos_pendientes.json para revisar
  python actualizar_atributos.py --aplicar   # aplica los cambios con value_to_set completado
"""

import requests
import json
import time
import sys
from pathlib import Path

TOKENS_FILE    = Path(__file__).parent / "tokens_cuenta3.json"
CALIDAD_FILE   = Path(__file__).parent / "calidad_fichas.json"
ACTIVAS_FILE   = Path(__file__).parent / "publicaciones_activas.json"
PENDIENTES_FILE = Path(__file__).parent / "atributos_pendientes.json"
BASE_URL       = "https://api.mercadolibre.com"

# Valores sugeridos automáticamente para atributos booleanos comunes
SUGERENCIAS_BOOL = {
    "INCLUDES_AERATOR":           "No",
    "INCLUDES_WATER_FILTER":      "No",
    "IS_MIXER":                   "Sí",
    "IS_KIT":                     "No",
    "IS_GOURMET":                 "No",
    "IS_SUITABLE_FOR_WATER_HEATER": "No",
    "IS_SWIVEL_PRODUCT":          "No",
    "WITH_EXTENSIVE_SPOUT":       "No",
    "WITH_FLEXIBLE_FAUCET":       "No",
    "IS_SUITABLE_FOR_SHIPMENT":   "Sí",
    "HAS_COMPATIBILITIES":        "No",
    "IS_NEW_OFFER":               "No",
    "IS_FLAMMABLE":               "No",
    "WITH_POSITIVE_IMPACT":       "No",
}


def load_access_token():
    return json.loads(TOKENS_FILE.read_text())["access_token"]


def get_headers():
    return {"Authorization": f"Bearer {load_access_token()}"}


def get_category_attributes(category_id, cache={}):
    if category_id in cache:
        return cache[category_id]
    r = requests.get(f"{BASE_URL}/categories/{category_id}/attributes", headers=get_headers())
    if r.ok:
        cache[category_id] = {a["id"]: a for a in r.json()}
    else:
        cache[category_id] = {}
    time.sleep(0.1)
    return cache[category_id]


def sugerir_valor(attr_id, value_type, allowed_values):
    if attr_id in SUGERENCIAS_BOOL:
        return SUGERENCIAS_BOOL[attr_id]
    if value_type == "boolean":
        return "No"
    if allowed_values:
        return f"ELEGIR: {' | '.join(v['name'] for v in allowed_values[:6])}"
    return None


# ─────────────────────────────────────────────
# FASE 1: GENERAR
# ─────────────────────────────────────────────
def generar():
    calidad = json.loads(CALIDAD_FILE.read_bytes().decode("latin-1"))
    activas = json.loads(ACTIVAS_FILE.read_bytes().decode("latin-1"))
    activas_idx = {i["id"]: i for i in activas}

    con_vacios = [r for r in calidad if any("Atributos" in p for p in r["problemas"])]
    print(f"\nPublicaciones con atributos vacíos: {len(con_vacios)}\n")

    pendientes = []

    for idx, r in enumerate(con_vacios, 1):
        item_id = r["id"]
        item = activas_idx.get(item_id)
        if not item:
            continue

        print(f"  [{idx}/{len(con_vacios)}] {item_id}", end="\r")

        category_id = item.get("category_id", "")
        cat_attrs = get_category_attributes(category_id)

        attrs_vacios = []
        for a in item.get("attributes", []):
            if a.get("value_name"):
                continue
            cat_attr = cat_attrs.get(a["id"], {})
            allowed = cat_attr.get("allowed_values", [])
            value_type = cat_attr.get("value_type", a.get("value_type", "string"))
            sugerido = sugerir_valor(a["id"], value_type, allowed)

            attrs_vacios.append({
                "id":             a["id"],
                "name":           a["name"],
                "value_type":     value_type,
                "allowed_values": [v["name"] for v in allowed] if allowed else [],
                "suggested":      sugerido,
                # Edita este campo antes de --aplicar (null = no actualizar)
                "value_to_set":   sugerido if sugerido and not sugerido.startswith("ELEGIR") else None,
            })

        if attrs_vacios:
            pendientes.append({
                "id":       item_id,
                "titulo":   r["titulo"],
                "precio":   r["precio"],
                "categoria": category_id,
                "atributos": attrs_vacios,
            })

    PENDIENTES_FILE.write_text(
        json.dumps(pendientes, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    auto = sum(
        1 for p in pendientes for a in p["atributos"]
        if a["value_to_set"] and not a["value_to_set"].startswith("ELEGIR")
    )
    manual = sum(
        1 for p in pendientes for a in p["atributos"]
        if not a["value_to_set"] or a["value_to_set"].startswith("ELEGIR")
    )

    print(f"\n{'='*65}")
    print(f"  Publicaciones con atributos vacíos : {len(pendientes)}")
    print(f"  Atributos con valor auto-sugerido  : {auto}  (listos para --aplicar)")
    print(f"  Atributos que requieren tu valor   : {manual}  (editar en JSON)")
    print(f"{'='*65}")
    print(f"\n  Archivo generado: {PENDIENTES_FILE}")
    print(f"  Revisa y edita 'value_to_set' donde sea necesario.")
    print(f"  Luego ejecuta:  python actualizar_atributos.py --aplicar\n")


# ─────────────────────────────────────────────
# FASE 2: APLICAR
# ─────────────────────────────────────────────
def aplicar():
    if not PENDIENTES_FILE.exists():
        print("Primero ejecuta --generar.")
        return

    pendientes = json.loads(PENDIENTES_FILE.read_text(encoding="utf-8"))

    total_items     = 0
    total_attrs     = 0
    errores         = []

    print(f"\nAplicando atributos...\n")

    for item in pendientes:
        item_id = item["id"]
        attrs_a_enviar = [
            {"id": a["id"], "value_name": a["value_to_set"]}
            for a in item["atributos"]
            if a.get("value_to_set") and not str(a["value_to_set"]).startswith("ELEGIR")
        ]

        if not attrs_a_enviar:
            continue

        r = requests.put(
            f"{BASE_URL}/items/{item_id}",
            headers={**get_headers(), "Content-Type": "application/json"},
            json={"attributes": attrs_a_enviar},
        )

        if r.ok:
            total_items += 1
            total_attrs += len(attrs_a_enviar)
            print(f"  OK  {item_id}  ({len(attrs_a_enviar)} atributos)  {item['titulo'][:50]}")
        else:
            errores.append({"id": item_id, "error": r.json()})
            print(f"  ERR {item_id}  {r.json().get('message','')}")

        time.sleep(0.3)

    print(f"\n{'='*65}")
    print(f"  Publicaciones actualizadas : {total_items}")
    print(f"  Atributos aplicados        : {total_attrs}")
    if errores:
        print(f"  Errores                    : {len(errores)}")
        err_file = Path(__file__).parent / "errores_atributos.json"
        err_file.write_text(json.dumps(errores, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Detalle errores en        : {err_file}")
    print(f"{'='*65}\n")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if "--aplicar" in sys.argv:
        aplicar()
    else:
        generar()
