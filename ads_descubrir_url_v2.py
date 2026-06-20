"""
La URL /ads/product-ads/... da 404. Vamos al panel del vendedor y descubrimos
dónde está realmente Mercado Ads (Publicidad).

Estrategia:
  1. Navegar al home logueado (mercadolibre.cl)
  2. Listar todos los links/botones que contengan "ads", "publicid", "anuncio", "promociona"
  3. Probar URLs candidatas:
     - https://www.mercadolibre.cl/publicidad
     - https://publicidad.mercadolibre.cl
     - https://www.mercadolibre.cl/anuncios
     - https://myaccount.mercadolibre.cl/...
  4. También probar el subdomain pads.mercadolibre.cl (Product Ads internal)
  5. Capturar todas las requests XHR durante la navegación
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C3.json"
OUT = ROOT / "data" / "auditoria"

URLS = [
    "https://www.mercadolibre.cl/",
    "https://myaccount.mercadolibre.cl/",
    "https://www.mercadolibre.cl/publicidad/",
    "https://www.mercadolibre.cl/publicidad",
    "https://publicidad.mercadolibre.cl/",
    "https://www.mercadolibre.cl/anuncios",
    "https://www.mercadolibre.cl/promociona",
    "https://www.mercadolibre.cl/ads/manager",
    "https://www.mercadolibre.cl/seller/ads/",
    "https://www.mercadolibre.cl/ml-ads/",
    "https://www.mercadolibre.cl/promociones",
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

        def on_request(req):
            url = req.url
            if "mercadolibre" in url and not url.endswith((".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2", ".ico", ".webp", ".gif")):
                if any(k in url for k in ("/api/", "/advertising/", "/ads-", "/private/", "/internal/",
                                          "graphql", "/items", "/campaign", "/product_ads", "/pads", "/publicidad")):
                    requests_captured.append({
                        "url": url,
                        "method": req.method,
                        "headers": dict(req.headers),
                        "post_data": req.post_data[:500] if req.post_data else None,
                    })

        page.on("request", on_request)

        # Primero: navegar al home y buscar el link "publicidad" / "ads"
        print(f"\n→ home mercadolibre.cl")
        await page.goto("https://www.mercadolibre.cl/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        print(f"  URL: {page.url[:80]} | Title: {(await page.title())[:60]}")

        # Buscar links con texto "publicidad", "ads", "promociona", "anuncio"
        print(f"\n→ Buscando enlaces de publicidad...")
        for kw in ["publicidad", "promocion", "anuncio", "ads", "mercado ads", "campaña"]:
            try:
                links = page.locator(f'a:has-text("{kw}")')
                n = await links.count()
                if n > 0:
                    for i in range(min(n, 5)):
                        href = await links.nth(i).get_attribute("href")
                        text = (await links.nth(i).inner_text()).strip()[:60]
                        if href:
                            print(f"  [{kw}] {text} → {href}")
            except Exception as e:
                pass

        # Mi cuenta / menú vendedor
        print(f"\n→ myaccount")
        try:
            await page.goto("https://myaccount.mercadolibre.cl/", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(4000)
            print(f"  URL: {page.url[:80]} | Title: {(await page.title())[:60]}")
            # Listar links que tengan "ads" / "publicidad" en href
            html = await page.content()
            import re
            hrefs = re.findall(r'href="([^"]+)"', html)
            ads_hrefs = set()
            for h in hrefs:
                if any(k in h.lower() for k in ("publicid", "/ads", "/mp-ads", "pads", "promocion", "ads-")):
                    if "mercadolibre" in h or h.startswith("/"):
                        ads_hrefs.add(h)
            if ads_hrefs:
                print(f"  Hrefs candidatos:")
                for h in sorted(ads_hrefs)[:30]:
                    print(f"    {h}")
        except Exception as e:
            print(f"  ⚠ {e}")

        # Probar las URLs candidatas
        for url in URLS[2:]:
            print(f"\n→ {url}")
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(3000)
                status = resp.status if resp else "?"
                final_url = page.url
                title = (await page.title())[:60]
                print(f"  [{status}] URL final: {final_url[:100]}")
                print(f"  Title: {title}")
                # Si la página dice "no existe" → 404 fake (no es real 404)
                content = (await page.content()).lower()
                if "no existe" in content or "page not found" in content:
                    print(f"  ✗ Página dice 'no existe'")
                else:
                    print(f"  ✓ Contenido válido (no 'no existe')")
                    # Si llegamos a una página válida, screenshot
                    await page.screenshot(path=str(OUT / f"ads_url_descubierta_{url.split('/')[-1] or 'root'}.png"))
            except Exception as e:
                print(f"  ⚠ {str(e)[:80]}")

        # Guardar storage updated
        try:
            await context.storage_state(path=str(STORAGE))
        except:
            pass

        await browser.close()

    # Reporte
    print(f"\n\n=== {len(requests_captured)} XHR/API capturadas ===")
    from collections import Counter
    urls = Counter()
    for r in requests_captured:
        urls[r["url"].split("?")[0]] += 1
    for url, n in urls.most_common(50):
        print(f"  {url}  ×{n}")

    (OUT / "ads_url_descubrir_xhr.json").write_text(
        json.dumps(requests_captured, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
