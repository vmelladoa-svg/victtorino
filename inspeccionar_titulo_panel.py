"""
Inspector específico: abre el editor, hace click en el panel 'Título',
captura qué aparece (modal, input, mensaje, error).
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "auditoria" / "inspect"
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C1.json"

ITEM_ID = "MLC1858919499"
EDIT_URL = f"https://www.mercadolibre.cl/publicaciones/{ITEM_ID}/modificar"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        print(f"Cargando: {EDIT_URL}")
        await page.goto(EDIT_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        # Scroll para que se renderice todo
        for _ in range(6):
            await page.mouse.wheel(0, 600)
            await page.wait_for_timeout(300)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1500)

        # Capturar antes del click
        await page.screenshot(path=str(OUT / "before_click.png"), full_page=True)

        # Buscar el panel Título por id="title_task" y click en su toggle
        print("\n=== Buscando panel Título ===")
        panel = page.locator("#title_task")
        n = await panel.count()
        print(f"Panel #title_task encontrado: {n}")
        if n == 0:
            print("No se encontró. Salgo.")
            await browser.close()
            return

        # Scroll hacia el panel
        await panel.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(OUT / "panel_title_visible.png"), full_page=True)

        # Click en el toggle del panel
        toggle = panel.locator("button.accordion-container__toggle").first
        if await toggle.count() == 0:
            # Probar click en el header completo
            print("toggle no encontrado, clickeando header del panel")
            await panel.locator(".accordion-container__header").first.click()
        else:
            print("Clickeando toggle del panel Título")
            try:
                await toggle.click(timeout=5000)
            except Exception as e:
                print(f"  click toggle falló: {e}")
                # Forzar click
                await toggle.evaluate("el => el.click()")

        await page.wait_for_timeout(3000)

        # Capturar después del click
        await page.screenshot(path=str(OUT / "after_click.png"), full_page=True)

        # Inspeccionar contenido del panel ahora expandido
        print(f"\n=== Contenido del panel después del click ===")
        # Inputs dentro del panel
        inputs = panel.locator("input, textarea")
        n_in = await inputs.count()
        print(f"Inputs/textarea dentro de #title_task: {n_in}")
        for i in range(min(n_in, 5)):
            el = inputs.nth(i)
            try:
                visible = await el.is_visible(timeout=500)
                enabled = await el.is_enabled(timeout=500)
                name = await el.get_attribute("name") or ""
                ph = await el.get_attribute("placeholder") or ""
                aria = await el.get_attribute("aria-label") or ""
                val = ""
                try: val = await el.input_value(timeout=500)
                except: pass
                print(f"  [{i}] visible={visible} enabled={enabled} name={name!r} placeholder={ph!r} aria={aria!r} val={val[:40]!r}")
            except Exception as e:
                print(f"  [{i}] error: {e}")

        # Buscar mensaje de error/info dentro del panel
        text_content = await panel.text_content()
        print(f"\nTexto del panel completo:\n{text_content[:1500]}")

        # Dump HTML del panel
        panel_html = await panel.inner_html()
        (OUT / "title_panel.html").write_text(panel_html, encoding="utf-8")
        print(f"\nHTML del panel guardado en {OUT / 'title_panel.html'}")

        # Mantener 10s para mirar
        print("\nMantengo abierto 10s para que mires...")
        await page.wait_for_timeout(10000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
