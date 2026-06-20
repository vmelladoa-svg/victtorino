# -*- coding: utf-8 -*-
"""
Ejemplo de uso de cada módulo del cliente Walmart Marketplace API.
Requiere credenciales en .env (ver .env.example).
"""
import json

import orders
import inventory
import prices


def pp(label: str, data: dict) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print("=" * 50)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    # ── Órdenes ──────────────────────────────────────────────────────────────
    print("\n[1] Listando órdenes recientes (limit=5)...")
    try:
        resultado = orders.get_orders(limit=5)
        pp("Órdenes recientes", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    print("\n[2] Órdenes con status Created...")
    try:
        resultado = orders.get_orders(limit=5, status="Created")
        pp("Órdenes nuevas", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    # ── Detalle y acknowledge de una orden (ejemplo con ID ficticio) ──────────
    orden_id = "ORDEN-EJEMPLO-123"
    print(f"\n[3] Detalle de orden {orden_id}...")
    try:
        resultado = orders.get_order(orden_id)
        pp("Detalle de orden", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    print(f"\n[4] Acknowledge orden {orden_id}...")
    try:
        resultado = orders.acknowledge_order(orden_id)
        pp("Acknowledge", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    # ── Inventario ───────────────────────────────────────────────────────────
    sku = "VICTTORINO-LP-80x44"
    print(f"\n[5] Stock de SKU: {sku}...")
    try:
        resultado = inventory.get_inventory(sku)
        pp("Inventario actual", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    print(f"\n[6] Actualizando stock de {sku} a 25 unidades...")
    try:
        resultado = inventory.update_inventory(sku, quantity=25)
        pp("Stock actualizado", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")

    # ── Precio ───────────────────────────────────────────────────────────────
    print(f"\n[7] Actualizando precio de {sku} a $49.990...")
    try:
        resultado = prices.update_price(sku, price=49990.00)
        pp("Precio actualizado", resultado)
    except RuntimeError as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    main()
