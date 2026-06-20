import requests
import json
import sys
from pathlib import Path

TOKENS_FILE = Path(__file__).parent / "tokens_cuenta3.json"
BASE_URL = "https://api.mercadolibre.com"


def load_access_token():
    return json.loads(TOKENS_FILE.read_text())["access_token"]


def get_headers():
    return {"Authorization": f"Bearer {load_access_token()}"}


def get_user_id():
    r = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
    r.raise_for_status()
    data = r.json()
    return data["id"], data["nickname"]


def get_all_item_ids(user_id):
    ids = []
    offset = 0
    limit = 50
    while True:
        r = requests.get(
            f"{BASE_URL}/users/{user_id}/items/search",
            headers=get_headers(),
            params={"offset": offset, "limit": limit},
        )
        r.raise_for_status()
        data = r.json()
        ids.extend(data["results"])
        offset += limit
        if offset >= data["paging"]["total"]:
            break
    return ids


def get_items_detail(item_ids):
    # La API acepta hasta 20 IDs por llamada
    items = []
    for i in range(0, len(item_ids), 20):
        chunk = ",".join(item_ids[i : i + 20])
        r = requests.get(f"{BASE_URL}/items", headers=get_headers(), params={"ids": chunk})
        r.raise_for_status()
        for entry in r.json():
            if entry.get("code") == 200:
                items.append(entry["body"])
    return items


def filter_activas(items):
    return [i for i in items if i.get("status") == "active" and i.get("available_quantity", 0) > 0]


def print_publicaciones(items, titulo="PUBLICACIONES"):
    status_label = {
        "active": "Activa",
        "paused": "Pausada",
        "closed": "Cerrada",
        "under_review": "En revisión",
        "inactive": "Inactiva",
    }

    print(f"\n{'='*70}")
    print(f"  {titulo}: {len(items)}")
    print(f"{'='*70}\n")

    for item in items:
        estado = status_label.get(item.get("status"), item.get("status"))
        precio = f"${item.get('price', 0):,.0f} {item.get('currency_id', '')}"
        stock = item.get("available_quantity", 0)
        vendidos = item.get("sold_quantity", 0)

        print(f"  ID       : {item['id']}")
        print(f"  Título   : {item['title']}")
        print(f"  Estado   : {estado}")
        print(f"  Precio   : {precio}")
        print(f"  Stock    : {stock}")
        print(f"  Vendidos : {vendidos}")
        print(f"  URL      : {item.get('permalink', '-')}")
        print(f"  {'-'*66}")


def main():
    solo_activas = "--todas" not in sys.argv

    print("Conectando con MercadoLibre...")
    user_id, nickname = get_user_id()
    print(f"Usuario: {nickname} (ID: {user_id})")

    print("Obteniendo publicaciones...")
    item_ids = get_all_item_ids(user_id)

    if not item_ids:
        print("No se encontraron publicaciones.")
        return

    print(f"Descargando detalle de {len(item_ids)} publicación(es)...")
    items = get_items_detail(item_ids)

    # Guardar JSON completo
    output = Path(__file__).parent / "publicaciones.json"
    output.write_text(json.dumps(items, indent=2, ensure_ascii=False))

    if solo_activas:
        items = filter_activas(items)
        print_publicaciones(items, titulo="ACTIVAS CON STOCK")
        # Guardar también el filtrado
        output_activas = Path(__file__).parent / "publicaciones_activas.json"
        output_activas.write_text(json.dumps(items, indent=2, ensure_ascii=False))
        print(f"\nActivas guardadas en: {output_activas}")
    else:
        print_publicaciones(items, titulo="TOTAL PUBLICACIONES")

    print(f"Detalle completo guardado en: {output}")
    if solo_activas:
        print(f"Tip: usa --todas para ver todas las publicaciones")


if __name__ == "__main__":
    main()
