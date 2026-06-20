"""
Captura la tabla de campañas en alta resolución.
"""
import os, json, time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "ml_cookies_c3.json")


def cargar_cookies(context):
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    cookies = []
    for c in raw:
        domain = c["domain"]
        if c.get("hostOnly") and domain.startswith("."):
            domain = domain[1:]
        cookie = {
            "name": c["name"], "value": c["value"], "domain": domain,
            "path": c.get("path", "/"), "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False), "sameSite": "None",
        }
        if not c.get("session") and c.get("expirationDate"):
            cookie["expires"] = int(c["expirationDate"])
        cookies.append(cookie)
    context.add_cookies(cookies)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Viewport ancho y alto para ver todo sin scroll
        context = browser.new_context(
            user_agent=UA, locale="es-CL",
            viewport={"width": 1600, "height": 1200},
            device_scale_factor=2,  # alta resolucion
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        cargar_cookies(context)
        page = context.new_page()

        page.goto("https://ads.mercadolibre.cl/product-ads/admin/campaigns?fe-rollout-version=v2&status=A%2CD", wait_until="domcontentloaded")
        time.sleep(8)

        # Cerrar banner
        try:
            page.keyboard.press("Escape")
            time.sleep(1)
        except Exception:
            pass

        # Scroll hasta la tabla
        page.evaluate("window.scrollTo(0, 700)")
        time.sleep(2)
        page.screenshot(path="ml_ads_tabla_hd.png")

        # Extraer texto de la tabla directamente
        tabla = page.evaluate("""
            () => {
                const rows = document.querySelectorAll('table tr, [class*="row"], [class*="campaign-row"]');
                const data = [];
                rows.forEach(row => {
                    const text = row.innerText.trim();
                    if (text && text.length > 5 && text.length < 500) {
                        data.push(text);
                    }
                });
                return data;
            }
        """)
        print("=== FILAS DE LA TABLA ===")
        for row in tabla:
            print(row)
            print("---")

        browser.close()
        print("\nScreenshot guardado en ml_ads_tabla_hd.png")


if __name__ == "__main__":
    main()
