"""
Piloto: pausar 1 item específico en la campaña Ads C3 via Playwright (UI web).
La API rechaza con 401 (sin permiso write), pero la UI web puede tener distintos
permisos. Probamos.

Flujo:
  1. Abrir Chrome (storage_C3 si existe, sino login manual)
  2. Navegar a Mercado Ads → Campaña Mayo
  3. Buscar item MLC3779856474
  4. Click toggle de pausa
  5. Verificar
  6. Si OK, listar items procesados; si falla, screenshot + reportar
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C3.json"
SHOTS = ROOT / "data" / "auditoria" / "playwright_shots"
SHOTS.mkdir(parents=True, exist_ok=True)

ADS_CAMPAIGN_ID = 357141159  # Campaña Mayo
ADS_URL = f"https://www.mercadolibre.cl/ads/product-ads/campaigns/{ADS_CAMPAIGN_ID}"
PILOTO_ITEM = "MLC3779856474"  # Pack Lavaplatos 80x44 Izq, CPC alto sin venta


async def ensure_login(page, max_wait_s=900):
    """Si no hay sesión, espera login en Mercado Ads de C3."""
    print(f"  Navegando a {ADS_URL}")
    try:
        await page.goto(ADS_URL, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    await page.wait_for_timeout(3000)

    def url_indicates_login():
        u = page.url.lower()
        return any(m in u for m in ("login", "authentication", "/auth/", "registration"))

    if not url_indicates_login():
        try:
            content = (await page.content()).lower()
            no_session = ("para vender, ingresa", "¡hola! para vender", "ingresá tu e-mail")
            if not any(m in content for m in no_session):
                print(f"  ✓ Ya en Ads, URL: {page.url[:80]}")
                return True
        except Exception:
            pass

    print(f"\n  ⚠ Login requerido — logueate con cuenta C3 (NOVAGRIFERIAS3) EN ESTA pestaña")
    print(f"  Esperando hasta {max_wait_s}s...")
    waited = 0
    consec = 0
    while waited < max_wait_s:
        await page.wait_for_timeout(2000)
        waited += 2
        if not url_indicates_login():
            try:
                content = (await page.content()).lower()
                no_session = ("para vender, ingresa", "¡hola! para vender", "ingresá tu contraseña")
                if not any(m in content for m in no_session):
                    consec += 1
                    if consec >= 2:
                        print(f"  ✓ Login detectado en {waited}s (URL: {page.url[:80]})")
                        return True
            except Exception:
                pass
        else:
            consec = 0
        if waited % 20 == 0:
            print(f"     ...esperando ({waited}s) URL: {page.url[:80]}")
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        ok = await ensure_login(page)
        if not ok:
            print("✗ Sin login, abortando")
            await browser.close()
            return

        # Guardar storage
        await context.storage_state(path=str(STORAGE))
        print(f"  Storage C3 guardado: {STORAGE}")

        # Si la URL final no es la campaña, navegar ahora
        if str(ADS_CAMPAIGN_ID) not in page.url:
            print(f"  Navegando a campaña: {ADS_URL}")
            await page.goto(ADS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)

        # Screenshot inicial
        await page.screenshot(path=str(SHOTS / "ads_campaign_landing.png"), full_page=True)
        print(f"  Screenshot: {SHOTS}/ads_campaign_landing.png")

        # Inspeccionar lo que hay en pantalla
        title = await page.title()
        print(f"  Page title: {title}")
        print(f"  URL final: {page.url}")

        # Buscar el item de prueba en el listado
        # Estrategias múltiples:
        # - Search box con el item ID
        # - O scroll buscando el texto
        # - O tabla con filas filtrables

        # Probar buscador
        search_selectors = [
            'input[placeholder*="buscar" i]',
            'input[placeholder*="producto" i]',
            'input[type="search"]',
            'input[name*="search" i]',
        ]
        search_input = None
        for sel in search_selectors:
            try:
                el = page.locator(sel).first
                if await el.count() > 0 and await el.is_visible(timeout=2000):
                    search_input = el
                    print(f"  Buscador encontrado: {sel}")
                    break
            except Exception:
                continue

        if search_input:
            await search_input.fill(PILOTO_ITEM)
            await page.wait_for_timeout(2500)
            await page.screenshot(path=str(SHOTS / "ads_search_result.png"), full_page=True)
            print(f"  Screenshot búsqueda: {SHOTS}/ads_search_result.png")

        # Buscar toggle de status (switch ML/Andes)
        # Andes design system usa class="andes-switch" o role="switch"
        toggles = page.locator('button[role="switch"], input[role="switch"], .andes-switch__input, [data-testid*="switch"]')
        n_toggles = await toggles.count()
        print(f"  Toggles visibles en pantalla: {n_toggles}")

        # Si hay tabla, listar filas
        rows = page.locator('tr, [role="row"]')
        n_rows = await rows.count()
        print(f"  Filas (tr / role=row): {n_rows}")

        # Dump HTML resumido
        html = await page.content()
        (SHOTS / "ads_campaign_page.html").write_text(html[:200000], encoding="utf-8")
        print(f"  HTML dump: {SHOTS}/ads_campaign_page.html ({len(html)} chars total, guardé 200k)")

        # Esperar para que vos puedas ver
        print(f"\n  Manteniendo abierto 30s — mira la pantalla y avisame qué ves")
        await page.wait_for_timeout(30000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
