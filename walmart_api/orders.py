# -*- coding: utf-8 -*-
from client import WalmartClient

_client = WalmartClient()


def get_orders(limit: int = 10, status: str | None = None) -> dict:
    """Lista órdenes recientes. status: Created | Acknowledged | Shipped | Delivered | Cancelled."""
    params: dict = {"limit": limit}
    if status:
        params["status"] = status
    return _client.get("/v3/orders", params=params)


def get_order(purchase_order_id: str) -> dict:
    """Retorna el detalle completo de una orden por su ID."""
    return _client.get(f"/v3/orders/{purchase_order_id}")


def acknowledge_order(purchase_order_id: str) -> dict:
    """Confirma la recepción de una orden (requerido por Walmart antes de despachar)."""
    return _client.post(f"/v3/orders/{purchase_order_id}/acknowledge")


def ship_order(purchase_order_id: str, tracking_info: dict) -> dict:
    """
    Marca una orden como enviada.

    tracking_info esperado:
    {
        "trackingNo": "123456789",
        "carrierName": "Starken",        # o UPS, FedEx, etc.
        "methodCode": "Standard",
        "shipDateTime": "2026-05-16T10:00:00.000Z",
        "lines": [
            {"lineNumber": "1", "unitOfMeasurement": "EACH", "item": {"productName": "...", "sku": "SKU-001"}, "orderLineStatuses": [{"status": "Shipped", "statusQuantity": {"unitOfMeasurement": "EACH", "amount": "1"}, "trackingInfo": {...}}]}
        ]
    }
    """
    payload = {
        "orderShipment": {
            "orderLines": {
                "orderLine": tracking_info.get("lines", [])
            }
        }
    }
    return _client.post(f"/v3/orders/{purchase_order_id}/shipping", json=payload)
