# -*- coding: utf-8 -*-
from client import WalmartClient

_client = WalmartClient()


def get_inventory(sku: str) -> dict:
    """Consulta el stock disponible de un producto por SKU."""
    return _client.get("/v3/inventory", params={"sku": sku})


def update_inventory(sku: str, quantity: int) -> dict:
    """
    Actualiza la cantidad disponible de un producto.
    Walmart requiere body XML para este endpoint.
    """
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<inventory xmlns="http://walmart.com/">
    <sku>{sku}</sku>
    <quantity>
        <unit>EACH</unit>
        <amount>{quantity}</amount>
    </quantity>
    <fulfillmentLagTime>1</fulfillmentLagTime>
</inventory>"""
    return _client.put("/v3/inventory", xml_body=xml, params={"sku": sku})
