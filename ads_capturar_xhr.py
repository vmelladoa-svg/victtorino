"""
Abre Chrome con sesión C3 y captura todas las requests XHR/fetch mientras
la UI de Mercado Ads carga. Objetivo: descubrir el endpoint INTERNO que la UI
usa para listar/editar items de la campaña (que típicamente es distinto al API
OAuth público y usa cookies de sesión).

Si encontramos un endpoint como:
  /advertising/ads-search-pads/...
  /api/v1/ads/...
  /ads-api/...
  /private/...
  o algún `:edit` / `:update`

→ podemos intentar replicarlo más adelante para pausar items.

NO hace clicks: solo navegación pasiva. Reporta los requests capturados.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C3.json"
OUT = ROOT / "data" / "auditoria"
OUT.mkdir(parents=True, exist_ok=True)

CAMPAIGN_ID = 357141159

URLS_TO_TRY = [
    "https://www.mercadolibre.cl/ads/",
    "https://www.mercadolibre.cl/ads/product-ads/campaigns",
    "https://www.mercadolibre.cl/ads/product-ads",
    f"https://www.mercadolibre.cl/ads/product-ads/campaigns/{CAMPAIGN_ID}",
    "https://ads.mercadolibre.cl/",
    "https://www.mercadolibre.cl/ads/dashboard",
]


async def main():
    requests_captured = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        # Listener: capturar TODAS las requests
        def on_request(req):
            url = req.url
            if "mercadolibre" in url or "mercadolibre.com" in url:
                # Solo me interesan los que parecen API
                if any(k in url for k in ("/api/", "/advertising/", "/ads-", "/ads/api", "/private/", "/internal/",
                                          "graphql", ":edit", ":update", "/items", "/campaigns")):
                    if not url.endswith((".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2", ".ico", ".webp")):
                        requests_captured.append({
                            "url": url,
                            "method": req.method,
                            "headers": dict(req.headers),
                            "post_data": req.post_data[:500] if req.post_data else None,
                            "resource_type": req.resource_type,
                            "from": page.url[:80],
                        })

        page.on("request", on_request)

        # Listener responses para verificar status
        responses = {}

        def on_response(resp):
            url = resp.url
            if "mercadolibre" in url and ("/api/" in url or "/advertising/" in url or "/ads-" in url):
                if not url.endswith((".js", ".css", ".png", ".jpg", ".svg", ".woff")):
                    responses[url] = resp.status

        page.on("response", on_response)

        print(f"Capturando XHR/fetch mientras navego por URLs candidatas...\n")
        for url in URLS_TO_TRY:
            print(f"→ {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=20000)
            except Exception as e:
                print(f"   ⚠ {type(e).__name__}: {str(e)[:80]}")
            await page.wait_for_timeout(3000)
            print(f"   URL final: {page.url[:100]}")
            print(f"   Requests capturadas hasta ahora: {len(requests_captured)}")

        # Esperar un poco extra por si hay redirecciones
        await page.wait_for_timeout(5000)

        # Status final + screenshot
        print(f"\n=== Screenshot final ===")
        await page.screenshot(path=str(OUT / "ads_xhr_final.png"), full_page=True)
        print(f"  {OUT}/ads_xhr_final.png")
        print(f"  URL final: {page.url}")
        print(f"  Title: {await page.title()}")

        # Guardar storage actualizado
        try:
            await context.storage_state(path=str(STORAGE))
            print(f"  Storage C3 actualizado: {STORAGE}")
        except Exception:
            pass

        # Dump HTML
        html = await page.content()
        (OUT / "ads_xhr_final.html").write_text(html[:300000], encoding="utf-8")

        await browser.close()

    # Analizar lo capturado
    print(f"\n\n=== {len(requests_captured)} requests capturadas ===\n")

    # Agrupar por URL base (sin query)
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in requests_captured:
        # Normalizar URL: quitar query
        url_base = r["url"].split("?")[0]
        grouped[url_base].append(r)

    print(f"  {len(grouped)} URLs únicas\n")
    for url, reqs in sorted(grouped.items()):
        methods = set(r["method"] for r in reqs)
        post = sum(1 for r in reqs if r["post_data"])
        st = responses.get(reqs[0]["url"], "?")
        print(f"  [{','.join(methods):8}] [{st:>3}] {url}  (×{len(reqs)})")
        if post:
            print(f"      ↳ {post} con body")

    # Identificar potenciales endpoints de WRITE
    print(f"\n=== Potenciales endpoints WRITE (POST/PUT/PATCH) ===")
    writes = [r for r in requests_captured if r["method"] in ("POST", "PUT", "PATCH", "DELETE")]
    if writes:
        for w in writes[:20]:
            print(f"  {w['method']} {w['url']}")
            print(f"    Body: {w.get('post_data', '')[:200]}")
            print(f"    Auth header: {w['headers'].get('authorization', 'NONE')[:80]}")
    else:
        print("  (ninguno — la UI no hizo writes en navegación pasiva)")

    # Guardar log
    log_file = OUT / "ads_xhr_capturado.json"
    log_file.write_text(json.dumps({
        "requests": requests_captured,
        "responses": responses,
        "urls_unique": sorted(grouped.keys()),
    }, indent=2, ensure_ascii=False))
    print(f"\nLog: {log_file}")


if __name__ == "__main__":
    asyncio.run(main())
