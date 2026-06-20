"""
Ahora sabemos que Mercado Ads vive en https://ads.mercadolibre.cl/productAds
Vamos a:
  1. Navegar allí con sesión C3
  2. Capturar todas las XHR (especialmente api.mercadolibre.com/advertising/...)
  3. Tomar screenshots de cada vista
  4. Navegar a la campaña 357141159 y al detalle de items
  5. Si encontramos toggle de pausa, hacer click programático en un item piloto
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C3.json"
OUT = ROOT / "data" / "auditoria"
SHOTS = OUT / "playwright_shots"
SHOTS.mkdir(parents=True, exist_ok=True)

CAMPAIGN_ID = 357141159
PILOTO_ITEM = "MLC3779856474"

# URLs candidatas dentro de ads.mercadolibre.cl
URLS = [
    "https://ads.mercadolibre.cl/productAds",
    f"https://ads.mercadolibre.cl/productAds/campaigns/{CAMPAIGN_ID}",
    f"https://ads.mercadolibre.cl/productAds/campaigns/{CAMPAIGN_ID}/items",
    f"https://ads.mercadolibre.cl/productAds/campaigns/{CAMPAIGN_ID}/products",
    f"https://ads.mercadolibre.cl/productAds/{CAMPAIGN_ID}",
    "https://ads.mercadolibre.cl/productAds/campaigns",
]


async def main():
    requests_captured = []
    responses_captured = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        def on_request(req):
            url = req.url
            if not url.endswith((".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2", ".ico", ".webp", ".gif", ".mp4")):
                if any(k in url for k in ("/api/", "/advertising/", "/ads-", "/private/", "/internal/",
                                          "graphql", "/items", "/campaign", "/product_ads", "/pads",
                                          "ads.mercadolibre", "api.mercadolibre")):
                    requests_captured.append({
                        "url": url,
                        "method": req.method,
                        "headers": dict(req.headers),
                        "post_data": req.post_data[:1000] if req.post_data else None,
                    })

        async def on_response(resp):
            url = resp.url
            if not url.endswith((".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2", ".ico", ".webp", ".gif")):
                if any(k in url for k in ("/advertising/", "/ads-", "api.mercadolibre", "ads.mercadolibre")):
                    try:
                        body = await resp.text()
                        responses_captured[url] = {
                            "status": resp.status,
                            "body_snippet": body[:500],
                        }
                    except Exception:
                        responses_captured[url] = {"status": resp.status, "body_snippet": "(error)"}

        page.on("request", on_request)
        page.on("response", lambda r: asyncio.ensure_future(on_response(r)))

        for url in URLS:
            print(f"\n→ {url}")
            try:
                resp = await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(4000)
                status = resp.status if resp else "?"
                final = page.url
                title = await page.title()
                print(f"  [{status}] URL final: {final[:120]}")
                print(f"  Title: {title[:80]}")

                # Si vemos "Campaña Mayo" en la página, estamos en el lugar correcto
                content = await page.content()
                indicators = []
                for ind in ["Campaña Mayo", "campaña mayo", str(CAMPAIGN_ID), PILOTO_ITEM,
                            "Pausar", "pausar", "Activar", "Estado", "Bid sugerido",
                            "Inversión", "Mercado Ads", "Product Ads"]:
                    if ind in content:
                        indicators.append(ind)
                if indicators:
                    print(f"  ✓ Indicadores en página: {indicators[:8]}")

                # Screenshot
                safe_name = url.replace("https://", "").replace("/", "_").replace(":", "")[:80]
                shot_path = SHOTS / f"explore_{safe_name}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                print(f"  Screenshot: {shot_path.name}")

                # Dump HTML
                html_path = SHOTS / f"explore_{safe_name}.html"
                html_path.write_text(content[:300000], encoding="utf-8")
            except Exception as e:
                print(f"  ⚠ {type(e).__name__}: {str(e)[:80]}")

        # Si después de las URLs estoy en una vista útil, dejarla abierta y explorar elementos
        print(f"\n→ URL final estable: {page.url}")

        # Buscar toggles, botones, etc
        for selector_name, selector in [
            ("role=switch", '[role="switch"]'),
            ("button switch", 'button[role="switch"]'),
            ("andes-switch", '.andes-switch'),
            ("andes-button (Pausar)", 'button:has-text("Pausar")'),
            ("andes-button (Estado)", 'button:has-text("Estado")'),
            ("button (Activar)", 'button:has-text("Activar")'),
            ("table rows", 'tr'),
            ("data-testid", '[data-testid]'),
            ("links to campaigns", 'a[href*="campaign"]'),
            ("links to /items", 'a[href*="/items"]'),
        ]:
            try:
                el = page.locator(selector)
                n = await el.count()
                if n > 0:
                    print(f"  {selector_name:30} → {n} elementos")
                    # Inspeccionar primeros 3
                    for i in range(min(n, 3)):
                        try:
                            text = (await el.nth(i).inner_text())[:60].replace("\n", " | ")
                            href = await el.nth(i).get_attribute("href") if "link" in selector_name else None
                            print(f"    [{i}] {text!r}  href={href}")
                        except Exception:
                            pass
            except Exception:
                pass

        # Guardar storage
        try:
            await context.storage_state(path=str(STORAGE))
        except:
            pass

        print(f"\n  Manteniendo abierto 20s para observación final...")
        await page.wait_for_timeout(20000)
        await browser.close()

    print(f"\n\n=== {len(requests_captured)} requests capturadas ===")
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in requests_captured:
        grouped[r["url"].split("?")[0]].append(r)

    for url, reqs in sorted(grouped.items()):
        methods = set(r["method"] for r in reqs)
        resp_status = responses_captured.get(reqs[0]["url"], {}).get("status", "?")
        print(f"  [{','.join(sorted(methods)):8}] [{resp_status:>3}] {url}  (×{len(reqs)})")
        # Si es write, mostrar body
        writes = [r for r in reqs if r["method"] in ("POST", "PUT", "PATCH", "DELETE")]
        for w in writes[:2]:
            if w["post_data"]:
                print(f"      ↳ {w['method']} body: {w['post_data'][:200]}")

    print(f"\n=== Endpoints WRITE detectados ===")
    writes = [r for r in requests_captured if r["method"] in ("POST", "PUT", "PATCH", "DELETE")]
    if writes:
        for w in writes:
            print(f"\n  {w['method']} {w['url']}")
            print(f"  Auth: {w['headers'].get('authorization', 'NONE')[:80]}")
            print(f"  Cookie: {w['headers'].get('cookie', 'NONE')[:80]}")
            if w["post_data"]:
                print(f"  Body: {w['post_data'][:300]}")
    else:
        print("  (ninguno en navegación pasiva)")

    (OUT / "ads_explorar_real_log.json").write_text(
        json.dumps({
            "requests": requests_captured,
            "responses": responses_captured,
        }, indent=2, ensure_ascii=False)
    )
    print(f"\nLog: {OUT}/ads_explorar_real_log.json")


if __name__ == "__main__":
    asyncio.run(main())
