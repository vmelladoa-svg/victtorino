"""
Herramienta de inspección: abre el editor de un item, scrollea todo, guarda HTML completo
y screenshots. NO modifica nada. Sirve para entender la estructura del DOM y diseñar
los selectores correctos.

Outputs: data/auditoria/inspect/
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "auditoria" / "inspect"
OUT.mkdir(parents=True, exist_ok=True)
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C1.json"

ITEM_ID = "MLC1858919499"  # el del piloto


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        # Probar varias URLs candidatas
        urls = [
            f"https://www.mercadolibre.cl/publicaciones/{ITEM_ID}/modificar",
            f"https://www.mercadolibre.cl/anuncios/{ITEM_ID}",
            f"https://www.mercadolibre.cl/sell/syi/edit/{ITEM_ID}",
            f"https://www.mercadolibre.cl/publicaciones/{ITEM_ID}",
        ]

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Probando: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
            await page.wait_for_timeout(3000)
            final_url = page.url
            print(f"  URL final: {final_url}")

            # Scroll completo para cargar contenido lazy
            for _ in range(8):
                await page.mouse.wheel(0, 800)
                await page.wait_for_timeout(400)
            await page.wait_for_timeout(2000)

            # Capturar
            slug = url.split("/")[-1] or "root"
            html = await page.content()
            (OUT / f"{i}_{slug}.html").write_text(html, encoding="utf-8")
            await page.screenshot(path=str(OUT / f"{i}_{slug}.png"), full_page=True)

            # Buscar elementos clave
            counts = {}
            for sel in ["input", "textarea", "button", '[role="dialog"]', "h1", "h2", '[data-testid]']:
                try:
                    counts[sel] = await page.locator(sel).count()
                except Exception:
                    counts[sel] = -1
            print(f"  Elementos: {counts}")

            # Listar primeros 10 inputs visibles con sus atributos
            print(f"  Inputs visibles (primeros 10):")
            inputs = page.locator("input, textarea")
            n_in = await inputs.count()
            for j in range(min(n_in, 10)):
                el = inputs.nth(j)
                try:
                    visible = await el.is_visible(timeout=500)
                    if not visible: continue
                    name = await el.get_attribute("name") or ""
                    placeholder = await el.get_attribute("placeholder") or ""
                    aria = await el.get_attribute("aria-label") or ""
                    val = await el.input_value(timeout=500)
                    print(f"     name={name!r} placeholder={placeholder!r} aria={aria!r} val={val[:40]!r}")
                except Exception:
                    pass

            # Buscar palabras clave en el contenido
            content = html.lower()
            keywords = ["título", "titulo", "editar", "modificar", "edit", "nombre del producto",
                       "información del producto", "title", "edit-title"]
            found = {k: content.count(k) for k in keywords}
            print(f"  Palabras encontradas en HTML: {found}")

        print(f"\nOutput en: {OUT}")
        # Mantener abierto 5s para que pueda observarse
        await page.wait_for_timeout(5000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
