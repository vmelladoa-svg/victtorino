# -*- coding: utf-8 -*-
import base64
import os
import time
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

_TOKEN_URL = "https://marketplace.walmartapis.com/v3/token"

# Cache en memoria: (access_token, expira_en_timestamp)
_cache: tuple[str, float] | None = None


def _encode_credentials() -> str:
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    raw = f"{client_id}:{client_secret}"
    return base64.b64encode(raw.encode()).decode()


def get_token() -> str:
    """
    Retorna un access_token válido, renovándolo automáticamente si expiró.
    El token de Walmart dura 15 minutos; lo renovamos con 30 s de margen.
    """
    global _cache
    if _cache and time.time() < _cache[1]:
        return _cache[0]

    headers = {
        "Authorization": f"Basic {_encode_credentials()}",
        "WM_SVC.NAME": "Walmart Marketplace",
        "WM_QOS.CORRELATION_ID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    try:
        r = requests.post(
            _TOKEN_URL,
            headers=headers,
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Error obteniendo token Walmart: {r.status_code} — {r.text}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Error de conexión al obtener token: {e}") from e

    data = r.json()
    token = data["access_token"]
    expires_in = int(data.get("expires_in", 900))
    _cache = (token, time.time() + expires_in - 30)
    return token
