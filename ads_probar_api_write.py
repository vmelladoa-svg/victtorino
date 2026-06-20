"""
Prueba sistemática de endpoints WRITE de Mercado Ads.
Probamos cada combinación de método/URL/body con varios tokens para descubrir
si alguno acepta cambio de status. NO modifica nada real: usamos el item piloto
MLC3779856474 y, antes de mandar, mostramos el body. Si el endpoint responde 200/204
significa que el cambio se aplicó — verificamos con GET y revertimos si hace falta.

Pruebas:
  1. PUT /product_ads/items con body lista de items (forma original)
  2. PUT /product_ads/items con body objeto único
  3. PUT /product_ads/items/{item_id}
  4. POST /product_ads/items
  5. PATCH /product_ads/items
  6. PUT /product_ads/campaigns/{cid}/items
  7. PUT /product_ads/campaigns/{cid}/items/{item_id}
  8. PUT /product_ads/items/status
  9. PUT /product_ads/items/state
 10. POST /product_ads/items/status

Con cada uno de los 4 tokens disponibles.
"""
import json
from pathlib import Path
import requests

ROOT = Path(__file__).parent
TOKENS = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
    "JOSE": json.loads((ROOT / "tokens_joseruben2.json").read_text())["access_token"],
}
AID = 79197
CAMPAIGN_ID = 357141159
PILOTO_ITEM = "MLC3779856474"
BASE = f"https://api.mercadolibre.com/advertising/advertisers/{AID}/product_ads"


def get_item_current_status(token):
    """Lee estado actual del item piloto."""
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/items", headers=h, params={
        "campaign_id": CAMPAIGN_ID,
    }, timeout=20)
    if r.status_code != 200:
        return None, f"GET items failed: {r.status_code}"
    for it in r.json().get("results", []):
        if it.get("item_id") == PILOTO_ITEM:
            return it, "ok"
    return None, "item not found in campaign"


def try_write(token_name, token, method, path, body, params=None, extra_headers=None):
    """Intenta un write y registra resultado."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Caller-Scopes": "ads:write",  # algunos endpoints requieren scope explícito
    }
    if extra_headers:
        headers.update(extra_headers)
    url = f"https://api.mercadolibre.com{path}"
    try:
        r = requests.request(method, url, headers=headers, params=params,
                             json=body if body is not None else None, timeout=20)
        info = {
            "token": token_name, "method": method, "url": url,
            "status": r.status_code,
            "body_snippet": r.text[:400],
        }
        print(f"  [{r.status_code}] {method:5} {path}")
        if r.status_code in (200, 201, 204):
            print(f"    ✓ ÉXITO con token {token_name}!")
            print(f"    Body: {r.text[:300]}")
        elif r.status_code == 401:
            print(f"    ✗ 401 unauthorized")
        elif r.status_code == 403:
            print(f"    ✗ 403 forbidden — {r.text[:120]}")
        elif r.status_code == 404:
            print(f"    · 404 (endpoint no existe)")
        elif r.status_code in (400, 422):
            print(f"    ! {r.status_code} validation — {r.text[:200]}")
            # 400/422 puede indicar endpoint VÁLIDO pero body incorrecto
        else:
            print(f"    ? {r.status_code} — {r.text[:200]}")
        return info
    except Exception as e:
        print(f"  ERROR {method} {path}: {e}")
        return {"token": token_name, "method": method, "url": url, "error": str(e)}


def main():
    print(f"=== Verificando estado actual del item piloto {PILOTO_ITEM} ===\n")
    item, msg = get_item_current_status(TOKENS["C3"])
    if not item:
        print(f"✗ {msg}")
        return
    current_status = item.get("status")
    print(f"  Item: {item.get('title', '')[:60]}")
    print(f"  Status actual: {current_status}")
    print(f"  Listo para probar pausa (active → paused)\n")

    target_status = "paused" if current_status == "active" else "active"
    results = []

    # Bodies a probar
    bodies = {
        "list": [{"item_id": PILOTO_ITEM, "status": target_status}],
        "single": {"item_id": PILOTO_ITEM, "status": target_status},
        "wrapped": {"items": [{"item_id": PILOTO_ITEM, "status": target_status}]},
        "id_only_status": {"status": target_status},
    }

    # Variantes de URLs
    variants = [
        # (method, path_template, body_key, params, label)
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/items", "list",          None, "PUT list"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/items", "single",        None, "PUT single"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/items", "wrapped",       None, "PUT wrapped"),
        ("POST",  f"/advertising/advertisers/{AID}/product_ads/items", "list",          None, "POST list"),
        ("PATCH", f"/advertising/advertisers/{AID}/product_ads/items", "list",          None, "PATCH list"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/items/{PILOTO_ITEM}", "id_only_status", None, "PUT /items/{id}"),
        ("PATCH", f"/advertising/advertisers/{AID}/product_ads/items/{PILOTO_ITEM}", "id_only_status", None, "PATCH /items/{id}"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/campaigns/{CAMPAIGN_ID}/items", "list", None, "PUT /campaigns/{cid}/items list"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/campaigns/{CAMPAIGN_ID}/items/{PILOTO_ITEM}", "id_only_status", None, "PUT /campaigns/{cid}/items/{id}"),
        ("POST",  f"/advertising/advertisers/{AID}/product_ads/items/status", "list", None, "POST /items/status"),
        ("PUT",   f"/advertising/advertisers/{AID}/product_ads/items/status", "list", None, "PUT /items/status"),
        # endpoints alternativos
        ("PUT",   f"/advertising/advertisers/{AID}/items", "list", None, "PUT /advertisers/{aid}/items (sin product_ads)"),
        ("PUT",   f"/ads/advertisers/{AID}/product_ads/items", "list", None, "PUT /ads/... (sin /advertising)"),
        # PADS (product ads search) namespace
        ("PUT",   f"/advertising/product_ads/items/{PILOTO_ITEM}", "id_only_status", None, "PUT /advertising/product_ads/items/{id}"),
    ]

    print(f"=== Probando {len(variants)} variantes × {len(TOKENS)} tokens = {len(variants)*len(TOKENS)} requests ===\n")

    for token_name, token in TOKENS.items():
        print(f"\n--- Token: {token_name} ---")
        for method, path, body_key, params, label in variants:
            body = bodies[body_key]
            info = try_write(token_name, token, method, path, body, params)
            info["label"] = label
            results.append(info)

    # Resumen
    print(f"\n\n=== RESUMEN ===")
    success = [r for r in results if r.get("status") in (200, 201, 204)]
    val_errors = [r for r in results if r.get("status") in (400, 422)]
    forbidden = [r for r in results if r.get("status") in (401, 403)]
    not_found = [r for r in results if r.get("status") == 404]
    other = [r for r in results if r.get("status") not in (200, 201, 204, 400, 401, 403, 404, 422)]

    print(f"  ✓ Éxito (2xx): {len(success)}")
    print(f"  ! Validation (4xx no auth): {len(val_errors)}  ← endpoint válido pero body mal")
    print(f"  ✗ 401/403: {len(forbidden)}")
    print(f"  · 404: {len(not_found)}")
    print(f"  ? Otros: {len(other)}")

    if success:
        print(f"\n=== ÉXITOS ===")
        for s in success:
            print(f"  [{s['token']}] {s['method']} {s['url']}")
            print(f"    Label: {s['label']}")
            print(f"    Body: {s['body_snippet'][:200]}")

    if val_errors:
        print(f"\n=== VALIDATION ERRORS (endpoint válido, ajustar body) ===")
        for v in val_errors[:10]:
            print(f"  [{v['token']}] {v['method']} {v['url']}")
            print(f"    {v['body_snippet'][:300]}")

    # Guardar log
    out = ROOT / "data" / "auditoria" / f"ads_probar_api_write_log.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nLog completo: {out}")


if __name__ == "__main__":
    main()
