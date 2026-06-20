"""
Abre Chrome en Mercado Ads raíz. Vos navegás manualmente al editor de Campaña Mayo
(o donde quieras). El script monitorea la URL del browser cada 3 segundos y la imprime
para descubrir la ruta correcta del editor de campaña.

Después podemos automatizar con la URL real.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
STORAGE = ROOT / "data" / "auditoria" / "playwright_storage" / "storage_C3.json"
SHOTS = ROOT / "data" / "auditoria" / "playwright_shots"
SHOTS.mkdir(parents=True, exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200, args=["--start-maximized"])
        context = await browser.new_context(
            storage_state=str(STORAGE) if STORAGE.exists() else None,
            viewport=None,
        )
        page = await context.new_page()

        await page.goto("https://www.mercadolibre.cl/ads/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        print(f"Inicial: {page.url}")
        print()
        print("=== INSTRUCCIONES PARA VOS ===")
        print("Navegá MANUALMENTE en el navegador:")
        print("  1. Si te pide login, logueate como C3 (NOVAGRIFERIAS3)")
        print("  2. Andá al menú Campañas → 'Campaña Mayo'")
        print("  3. Hacé scroll hasta ver la lista de los 154 items")
        print("  4. Buscá el item MLC3779856474 si querés")
        print("  5. Intentá hacer click en su toggle de pausa")
        print()
        print("Yo voy a monitorear las URLs por las que pasás. Tomá tu tiempo.")
        print()
        print("=== URLs visitadas (cada 3s, dedup) ===")

        urls_vistas = []
        last_url = ""
        for i in range(300):  # 15 min máximo
            await page.wait_for_timeout(3000)
            current = page.url
            if current != last_url:
                urls_vistas.append(current)
                print(f"  [{i*3:>4}s] {current}")
                last_url = current
                # Screenshot cada cambio de URL
                ts = i * 3
                try:
                    await page.screenshot(path=str(SHOTS / f"explore_{ts:04d}.png"), full_page=False)
                except Exception:
                    pass

        # Después de 15 min, dump completo
        print(f"\n=== Resumen URLs visitadas ===")
        for u in urls_vistas:
            print(f"  {u}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
