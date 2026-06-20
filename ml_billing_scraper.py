"""
Extrae el detalle de cobros de un mes específico de ML Billing.
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
    captured_api = []

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

        def on_response(response):
            url = response.url
            try:
                body = response.json()
                captured_api.append({"url": url, "data": body})
            except Exception:
                pass

        page.on("response", on_response)

        # Detalle de Abril (mes cerrado y pagado)
        url_abril = "https://myaccount.mercadolibre.cl/billing/detail/20260423?fromSummary=true"
        print(f"Navegando a: {url_abril}")
        page.goto(url_abril, wait_until="domcontentloaded")
        time.sleep(6)

        page.screenshot(path="ml_billing_abril.png", full_page=True)
        texto = page.evaluate("() => document.body.innerText")
        print(f"URL final: {page.url}")
        print(f"\nTexto:\n{texto[:3000]}")

        with open("ml_billing_abril.txt", "w", encoding="utf-8") as f:
            f.write(texto)

        # Guardar APIs relevantes
        relevantes = [item for item in captured_api if any(
            k in item['url'] for k in ['detail', 'group', 'charge', 'concept', 'billing']
        )]
        with open("ml_billing_abril_api.json", "w", encoding="utf-8") as f:
            json.dump(relevantes, f, ensure_ascii=False, indent=2)

        print(f"\n{len(relevantes)} APIs relevantes capturadas")
        for item in relevantes:
            print(f"  {item['url'][:100]}")

        browser.close()


if __name__ == "__main__":
    main()
