import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from playwright.sync_api import sync_playwright

API_HITS = []

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36")
        page = ctx.new_page()

        def on_resp(resp):
            u = resp.url
            if ("api" in u or "/h5/" in u or "goods" in u) and resp.request.resource_type in ("xhr", "fetch"):
                try:
                    ct = resp.headers.get("content-type", "")
                    body = resp.text() if "json" in ct else ""
                except Exception:
                    body = ""
                API_HITS.append({"url": u, "method": resp.request.method,
                                 "status": resp.status, "len": len(body),
                                 "body_head": body[:300],
                                 "post": (resp.request.post_data or "")[:300]})
        page.on("response", on_resp)

        print(">> abriendo /goods/list/all ...")
        page.goto("https://shop.chilat.com/goods/list/all", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        # scroll para disparar carga
        for _ in range(3):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)

        print(f"\n=== requests XHR/fetch capturados: {len(API_HITS)} ===")
        for hcall in API_HITS:
            print(f"\n[{hcall['method']} {hcall['status']}] len={hcall['len']}")
            print("  URL :", hcall["url"])
            if hcall["post"]:
                print("  BODY:", hcall["post"])
            if hcall["body_head"]:
                print("  RESP:", hcall["body_head"])
        browser.close()

run()
