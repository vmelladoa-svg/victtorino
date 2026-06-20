# -*- coding: utf-8 -*-
import uuid
from typing import Any

import requests

from auth import get_token


class WalmartClient:
    BASE_URL = "https://marketplace.walmartapis.com"

    def request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: Any = None,
        xml_body: str | None = None,
    ) -> dict:
        """
        Ejecuta una llamada a la API con todos los headers requeridos.
        Soporta body JSON y XML (para endpoints de inventario/precio).
        """
        headers = {
            "WM_SEC.ACCESS_TOKEN": get_token(),
            "WM_SVC.NAME": "Walmart Marketplace",
            "WM_QOS.CORRELATION_ID": str(uuid.uuid4()),
            "Accept": "application/json",
        }

        if xml_body is not None:
            headers["Content-Type"] = "application/xml"
            body_kwargs: dict = {"data": xml_body.encode()}
        elif json is not None:
            headers["Content-Type"] = "application/json"
            body_kwargs = {"json": json}
        else:
            body_kwargs = {}

        url = f"{self.BASE_URL}{path}"
        try:
            r = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                timeout=30,
                **body_kwargs,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Error de conexión: {e}") from e

        if not r.ok:
            raise RuntimeError(
                f"Error {r.status_code} en {method} {path}: {r.text[:300]}"
            )

        if r.status_code == 204 or not r.content:
            return {}

        return r.json()

    # Atajos de conveniencia
    def get(self, path: str, params: dict | None = None) -> dict:
        return self.request("GET", path, params=params)

    def post(self, path: str, json: Any = None, xml_body: str | None = None) -> dict:
        return self.request("POST", path, json=json, xml_body=xml_body)

    def put(self, path: str, params: dict | None = None, json: Any = None, xml_body: str | None = None) -> dict:
        return self.request("PUT", path, params=params, json=json, xml_body=xml_body)
