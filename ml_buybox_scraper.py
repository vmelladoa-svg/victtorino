"""
Analiza por qué los productos premium no tienen Buy Box en ML.
"""
import os, json, time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "ml_cookies_c3.json")

PREMIUM_ITEMS = [
    ("MLC1293768192", "$129.190", "Receptáculo Ducha Metacrilato"),
    ("MLC1293700049", "$115.190", "Fluxometro Palanca Llave Corte"),
    ("MLC1293983654", "$120.490", "Fluxometro Palanca Salida Superior"),
    ("MLC2117169726", "$125.851", "Grifo Monomando Profesional Tüumm"),
]


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
        context = browser.new_context(
            user_agent=UA, locale="es-CL",
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        cargar_cookies(context)
        page = context.new_page()

        resultados = {}

        for item_id, precio, nombre in PREMIUM_ITEMS:
            print(f"\n=== {nombre} ({precio}) ===")
            url = f"https://www.mercadolibre.cl/p/{item_id}"
            # Intentar con la URL de publicacion directa
            url_pub = f"https://articulo.mercadolibre.cl/MLC-{item_id.replace('MLC','')}"

            try:
                page.goto(f"https://www.mercadolibre.cl/p/{item_id}", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass

            try:
                page.goto(f"https://www.mercadolibre.cl/{item_id.lower()}", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass

            time.sleep(3)
            page.screenshot(path=f"ml_bb_{item_id}.png")
            texto = page.evaluate("() => document.body.innerText")

            # Extraer info relevante
            info = {
                "url": page.url,
                "texto_preview": texto[:800],
            }
            resultados[item_id] = info
            print(f"  URL: {page.url}")
            print(f"  Texto: {texto[:400]}")

        with open("ml_buybox_analysis.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        browser.close()


if __name__ == "__main__":
    main()
