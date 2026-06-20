# -*- coding: utf-8 -*-
from client import WalmartClient

_client = WalmartClient()


def update_price(sku: str, price: float, currency: str = "USD") -> dict:
    """
    Actualiza el precio de un producto por SKU.
    Walmart requiere body XML para este endpoint.
    """
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Price xmlns="http://walmart.com/">
    <itemIdentifier>
        <sku>{sku}</sku>
    </itemIdentifier>
    <pricingList>
        <pricing>
            <currentPrice>
                <value currency="{currency}" amount="{price:.2f}"/>
            </currentPrice>
            <currentPriceType>BASE</currentPriceType>
        </pricing>
    </pricingList>
</Price>"""
    return _client.put("/v3/price", xml_body=xml)
