"""
Prueba en seco del módulo post-compra.
Consulta órdenes reales de las últimas 24h y muestra el mensaje que se enviaría,
SIN enviar nada.

Uso:
    python test_post_compra.py
"""
import sys
import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

# Agregar ml-responder al path para usar sus módulos
sys.path.insert(0, str(Path(__file__).parent / "ml-responder"))

from agent.complementarios import sugerir_complementarios, generar_mensaje_post_compra

BASE_URL = "https://api.mercadolibre.com"
VENTANA_HORAS = 48  # más amplia para el test

CUENTAS = [
    {"nombre": "Cuenta 1", "tokens_file": Path("tokens_cuenta1.json")},
    {"nombre": "Cuenta 2", "tokens_file": Path("tokens_cuenta2.json")},
    {"nombre": "Cuenta 3", "tokens_file": Path("tokens_cuenta3.json")},
]

ORDENES_ESTADOS = ["confirmed", "payment_required", "paid"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _refrescar_token(tokens_file):
    data = json.loads(tokens_file.read_text())
    r = requests.post(f"{BASE_URL}/oauth/token", data={
        "grant_type":    "refresh_token",
        "client_id":     os.getenv("ML_CLIENT_ID"),
        "client_secret": os.getenv("ML_CLIENT_SECRET"),
        "refresh_token": data["refresh_token"],
    })
    if r.status_code == 200:
        nueva = r.json()
        data.update(nueva)
        tokens_file.write_text(json.dumps(data, indent=2))
        print(f"  Token refrescado.")
        return nueva["access_token"]
    print(f"  ERROR refrescando token: {r.status_code}")
    return None


def _identificar_tipo_venta(orden):
    shipping = orden.get("shipping") or {}
    if not shipping or not shipping.get("id"):
        return "acordar"
    if "to_be_agreed" in orden.get("tags", []):
        return "acordar"
    return "normal"


def probar_cuenta(nombre, tokens_file):
    print(f"\n{'='*55}")
    print(f"  {nombre}")
    print(f"{'='*55}")

    if not tokens_file.exists():
        print(f"  ⚠  Archivo {tokens_file} no encontrado. Saltando.")
        return

    data = json.loads(tokens_file.read_text())
    token = data["access_token"]
    seller_id = data.get("user_id")

    desde = (datetime.now(timezone.utc) - timedelta(hours=VENTANA_HORAS)).strftime(
        "%Y-%m-%dT%H:%M:%S.000-00:00"
    )
    params = {"seller": seller_id, "order.date_created.from": desde, "sort": "date_desc", "limit": 20}

    r = requests.get(f"{BASE_URL}/orders/search", headers=_headers(token), params=params)
    if r.status_code == 401:
        print("  Token expirado, refrescando...")
        token = _refrescar_token(tokens_file)
        if not token:
            return
        r = requests.get(f"{BASE_URL}/orders/search", headers=_headers(token), params=params)

    if r.status_code != 200:
        print(f"  ERROR: {r.status_code} {r.text[:200]}")
        return

    ordenes = r.json().get("results", [])
    relevantes = [o for o in ordenes if o.get("status") in ORDENES_ESTADOS]

    print(f"  Órdenes últimas {VENTANA_HORAS}h: {len(ordenes)} total, {len(relevantes)} relevantes")

    if not relevantes:
        print("  Sin órdenes para probar.")
        return

    for orden in relevantes[:3]:  # máximo 3 para no gastar tokens
        orden_id     = orden["id"]
        buyer        = orden.get("buyer", {})
        buyer_nombre = buyer.get("first_name") or buyer.get("nickname") or "Cliente"
        status       = orden.get("status")
        items        = orden.get("order_items", [])
        titulo       = items[0]["item"]["title"] if items else "Producto sin título"
        tipo_venta   = _identificar_tipo_venta(orden)
        complementarios = sugerir_complementarios(titulo)

        print(f"\n  Orden #{orden_id} — {status}")
        print(f"  Comprador  : {buyer_nombre}")
        print(f"  Producto   : {titulo}")
        print(f"  Tipo venta : {tipo_venta}")
        print(f"  Sugerencias: {complementarios or 'ninguna'}")
        print(f"\n  Generando mensaje con Claude...")

        mensaje = generar_mensaje_post_compra(
            nombre_comprador=buyer_nombre,
            titulo_producto=titulo,
            tipo_venta=tipo_venta,
            complementarios=complementarios,
        )

        if mensaje:
            print(f"\n  ┌─ MENSAJE QUE SE ENVIARÍA {'─'*30}")
            for linea in mensaje.split("\n"):
                print(f"  │ {linea}")
            print(f"  └{'─'*45}")
        else:
            print("  ⚠  No se pudo generar mensaje.")


if __name__ == "__main__":
    print("\n🧪 PRUEBA EN SECO — post-compra Victtorino")
    print("   (no se envía ningún mensaje real)\n")

    for cuenta in CUENTAS:
        probar_cuenta(cuenta["nombre"], cuenta["tokens_file"])

    print("\n✅ Prueba completada.")
