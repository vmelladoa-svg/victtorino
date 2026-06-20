"""
Aplica cambios de título en Seller Center vía Playwright (navegador automatizado).
Modo visible con slow_mo para que veas qué pasa.

Flujo:
  1. Por cuenta (C1, C2, C3):
     a. Abrir navegador con storage_state si existe
     b. Si NO está logueado, esperar login manual (incluido 2FA)
     c. Guardar storage_state
     d. Iterar items de esa cuenta:
        - GET editor URL
        - Esperar a que cargue el input título
        - Borrar y tipear nuevo título
        - Click "Guardar"
        - Manejar modal "Cambiar la familia"
        - Verificar que el título quedó cambiado
        - Screenshot si falla
  2. Log JSON con resultado por item

Uso:
  python titulos_playwright_aplicar.py             # piloto 1 item
  python titulos_playwright_aplicar.py --p1        # solo P1
  python titulos_playwright_aplicar.py --p1 --p2   # P1+P2
  python titulos_playwright_aplicar.py --all       # los 30
  python titulos_playwright_aplicar.py --only MLC1859010123,MLC2961406356
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from titulos_top30_curated import CURATED, TOP30, title_score

ROOT = Path(__file__).parent
STORAGE_DIR = ROOT / "data" / "auditoria" / "playwright_storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
SHOTS_DIR = ROOT / "data" / "auditoria" / "playwright_shots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_OUT = ROOT / "data" / "auditoria" / f"titulos_playwright_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

# Parsear args
MODE = "piloto"
ONLY_IDS = None
for i, a in enumerate(sys.argv):
    if a == "--all": MODE = "all"
    elif a == "--p1": MODE = "p1" if MODE == "piloto" else MODE + "+p1"
    elif a == "--p2": MODE = "p2" if MODE == "piloto" else MODE + "+p2"
    elif a == "--p3": MODE = "p3" if MODE == "piloto" else MODE + "+p3"
    elif a == "--only" and i+1 < len(sys.argv):
        ONLY_IDS = set(sys.argv[i+1].split(","))


def items_para_modo():
    by_id = {it["iid"]: it for it in TOP30}
    rows = []
    for iid, new_title in CURATED.items():
        it = by_id.get(iid)
        if not it: continue
        delta = title_score(new_title) - title_score(it["title"])
        rows.append({"iid": iid, "cuenta": it["cuenta"], "current": it["title"],
                    "new": new_title, "delta": delta})
    rows.sort(key=lambda r: -r["delta"])
    if ONLY_IDS:
        return [r for r in rows if r["iid"] in ONLY_IDS]
    if MODE == "piloto":
        return rows[:1]
    selected = []
    if "all" in MODE: return rows
    if "p1" in MODE: selected.extend(rows[:10])
    if "p2" in MODE: selected.extend(rows[10:20])
    if "p3" in MODE: selected.extend(rows[20:30])
    return selected


async def ensure_login(page, cuenta, sample_item_id, max_wait_s=900):
    """
    Flujo nuevo:
      1. Navegar DIRECTO al editor del primer item
      2. Si ML redirige a 'login' o muestra '¡Hola!' → no logueado
      3. Esperar (sin re-navegar) hasta que la URL del navegador sea la del editor real
         (ML te lleva ahí solo después del login). Victor hace login EN LA MISMA PESTAÑA.
      4. Cuando URL contenga "publicaciones/.../modificar" o "user_product_item_detail_form"
         → logueado.

    Importante: NO abrir otras pestañas. El login DEBE ser en la pestaña que controlamos.
    """
    target_url = f"https://www.mercadolibre.cl/publicaciones/{sample_item_id}/modificar"
    print(f"  Navegando directo al editor del piloto: {target_url[:80]}")
    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  ⚠ Error cargando target: {e}")
    await page.wait_for_timeout(3000)

    def is_on_editor():
        u = page.url.lower()
        # El editor real redirige a una URL con "user_product_item_detail_form" o queda en /publicaciones/.../modificar
        if "user_product_item_detail_form" in u: return True
        if "/publicaciones/" in u and "/modificar" in u and "login" not in u: return True
        if "modificar/bomni" in u: return True
        return False

    if is_on_editor():
        print(f"  ✓ Editor cargado (sesión activa) - URL: {page.url[:80]}")
        return True

    print(f"\n  ⚠ NO HAY SESIÓN — ML te llevó a login")
    print(f"  >>> EN LA MISMA PESTAÑA del Chrome abierto:")
    print(f"  >>>   1. Hacé LOGIN con la cuenta {cuenta}")
    print(f"  >>>   2. Completá 2FA si te pide")
    print(f"  >>>   3. ML automáticamente te devuelve al editor del item")
    print(f"  >>> NO abras pestañas nuevas, NO abras otro Chrome. Usá ESTA pestaña.")
    print(f"  >>> Esperando hasta {max_wait_s}s...")

    waited = 0
    while waited < max_wait_s:
        await page.wait_for_timeout(3000)
        waited += 3
        if is_on_editor():
            print(f"  ✓ Editor detectado (después de {waited}s) - URL: {page.url[:80]}")
            await page.wait_for_timeout(2000)  # esperar render
            return True
        if waited % 15 == 0:
            print(f"     ...esperando login ({waited}s/{max_wait_s}s) URL actual: {page.url[:80]}")
    print(f"  ✗ Timeout esperando login")
    return False


async def cambiar_titulo(page, iid, old_title, new_title):
    """
    Flow descubierto en inspección:
      1. Ir a /publicaciones/{iid}/modificar (redirige a editor SYI omni-update)
      2. Esperar SPA render
      3. Scroll a #title_task (panel accordion del título)
      4. Click en su toggle para expandir
      5. Adentro del panel: 1 input con valor=título actual
      6. Limpiar y tipear nuevo título
      7. Click botón "Confirmar" dentro del panel
      8. Manejar modal "cambiar familia" si aparece (Confirmar)
      9. Verificar cambio
    """
    edit_url = f"https://www.mercadolibre.cl/publicaciones/{iid}/modificar"
    log_entry = {"iid": iid, "old": old_title, "new": new_title, "status": "PENDING"}

    try:
        print(f"\n  → Navegando a editor {iid}")
        await page.goto(edit_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # 1) Localizar panel del título
        panel = page.locator("#title_task")
        if await panel.count() == 0:
            await page.screenshot(path=str(SHOTS_DIR / f"fail_no_panel_{iid}.png"))
            log_entry["status"] = "FAIL_NO_TITLE_PANEL"
            return log_entry

        # 2) Scroll para que sea visible
        await panel.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        # 3) Click toggle del panel
        toggle = panel.locator("button.accordion-container__toggle").first
        if await toggle.count() > 0:
            try:
                await toggle.click(timeout=5000)
            except Exception:
                # Forzar click vía JS si el toggle está bloqueado por CSS pero presente
                await toggle.evaluate("el => el.click()")
        else:
            # Fallback: clickear el header completo
            await panel.locator(".accordion-container__header").first.click()
        await page.wait_for_timeout(2500)
        print(f"     panel título expandido")

        # 4) Localizar el input editable dentro del panel
        title_input = panel.locator("input, textarea").first
        n_in = await panel.locator("input, textarea").count()
        if n_in == 0:
            await page.screenshot(path=str(SHOTS_DIR / f"fail_no_input_expanded_{iid}.png"))
            log_entry["status"] = "FAIL_NO_INPUT_EXPANDED"
            return log_entry

        # Validar que está visible y enabled
        try:
            visible = await title_input.is_visible(timeout=2000)
            enabled = await title_input.is_enabled(timeout=2000)
            current_val = await title_input.input_value(timeout=2000)
        except Exception:
            visible = enabled = False
            current_val = ""
        print(f"     input: visible={visible} enabled={enabled} valor_actual='{current_val[:50]}'")

        if not (visible and enabled):
            await page.screenshot(path=str(SHOTS_DIR / f"fail_input_disabled_{iid}.png"))
            log_entry["status"] = "FAIL_INPUT_DISABLED"
            return log_entry

        # 5) Limpiar y escribir nuevo
        await title_input.click()
        await page.wait_for_timeout(300)
        # triple click para seleccionar todo, luego eliminar
        await title_input.press("Control+A")
        await page.wait_for_timeout(200)
        await title_input.press("Delete")
        await page.wait_for_timeout(200)
        await title_input.type(new_title, delay=20)
        await page.wait_for_timeout(800)

        # Verificar valor nuevo en input
        try:
            v_after = await title_input.input_value(timeout=2000)
            print(f"     nuevo valor en input: '{v_after[:50]}'")
        except Exception:
            v_after = ""

        # 6) Botón "Confirmar" dentro del panel
        confirm_btn = None
        # Buscar dentro del panel primero
        for sel in ['button:has-text("Confirmar")', 'button:has-text("Guardar")']:
            try:
                btns = panel.locator(sel)
                c = await btns.count()
                for i in range(c):
                    b = btns.nth(i)
                    if await b.is_visible(timeout=1000) and await b.is_enabled(timeout=1000):
                        confirm_btn = b
                        print(f"     botón confirmar encontrado en panel: {sel}")
                        break
                if confirm_btn: break
            except Exception:
                continue
        if not confirm_btn:
            await page.screenshot(path=str(SHOTS_DIR / f"fail_no_confirm_{iid}.png"))
            log_entry["status"] = "FAIL_NO_CONFIRM_BUTTON"
            return log_entry

        await confirm_btn.click()
        print(f"     click Confirmar — esperando respuesta...")
        await page.wait_for_timeout(3000)

        # 7) Modal de "cambiar la familia" o confirmación adicional
        # Buscar modal de "atención" o similar
        modal_confirmed = False
        for sel in [
            '[role="dialog"] button:has-text("Confirmar")',
            '[role="dialog"] button:has-text("Continuar")',
            '[role="dialog"] button:has-text("Sí")',
            '[role="dialog"] button.andes-button--loud',
            '.andes-modal__actions button:has-text("Confirmar")',
        ]:
            try:
                btns = page.locator(sel)
                c = await btns.count()
                for i in range(c):
                    b = btns.nth(i)
                    if await b.is_visible(timeout=1500) and await b.is_enabled(timeout=1000):
                        await b.click()
                        print(f"     modal confirmado ({sel})")
                        modal_confirmed = True
                        break
                if modal_confirmed: break
            except Exception:
                continue

        await page.wait_for_timeout(4500)

        # 8) Verificar resultado
        try:
            # Re-leer el panel (puede haberse colapsado de nuevo)
            new_panel_text = await panel.text_content()
            if new_title[:25].lower() in (new_panel_text or "").lower():
                log_entry["status"] = "OK"
                print(f"     ✓ Nuevo título confirmado")
            else:
                # quizá la página cambió - revisar contenido global
                content = await page.content()
                if new_title[:25].lower() in content.lower():
                    log_entry["status"] = "OK"
                    print(f"     ✓ Nuevo título encontrado en página (global)")
                else:
                    log_entry["status"] = "UNVERIFIED"
                    log_entry["panel_text"] = (new_panel_text or "")[:200]
                    print(f"     ~ No se verificó — panel dice: {(new_panel_text or '')[:80]}")
        except Exception:
            log_entry["status"] = "OK_NO_VERIFY"
        return log_entry

    except PWTimeout as e:
        await page.screenshot(path=str(SHOTS_DIR / f"timeout_{iid}.png"))
        log_entry["status"] = "TIMEOUT"
        log_entry["error"] = str(e)[:200]
        return log_entry
    except Exception as e:
        try:
            await page.screenshot(path=str(SHOTS_DIR / f"error_{iid}.png"))
        except Exception:
            pass
        log_entry["status"] = "ERROR"
        log_entry["error"] = str(e)[:300]
        return log_entry


async def main():
    items = items_para_modo()
    if not items:
        print("Nada que hacer.")
        return
    print(f"Modo: {MODE} | Items a procesar: {len(items)}")
    by_cuenta = {}
    for it in items:
        by_cuenta.setdefault(it["cuenta"], []).append(it)

    log = []
    async with async_playwright() as p:
        for cuenta, lista in by_cuenta.items():
            print(f"\n{'='*60}\n  CUENTA {cuenta} — {len(lista)} items\n{'='*60}")
            storage_file = STORAGE_DIR / f"storage_{cuenta}.json"
            storage = str(storage_file) if storage_file.exists() else None
            browser = await p.chromium.launch(headless=False, slow_mo=200,
                                              args=["--start-maximized"])
            context = await browser.new_context(
                storage_state=storage,
                viewport=None,  # tamaño real ventana
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/123.0 Safari/537.36"),
            )
            page = await context.new_page()
            # Pasar el primer item ID de esta cuenta para usarlo como destino post-login
            first_item_id = lista[0]["iid"]
            ok = await ensure_login(page, cuenta, first_item_id)
            if not ok:
                print(f"  ⛔ No se pudo loguear en {cuenta} — saltando esta cuenta")
                await browser.close()
                continue
            # Guardar storage para próxima
            await context.storage_state(path=str(storage_file))
            print(f"  Storage guardado: {storage_file}")

            for i, it in enumerate(lista, 1):
                print(f"\n  [{i}/{len(lista)}] {it['iid']} ({cuenta})")
                print(f"     ANTES: {it['current']}")
                print(f"     NUEVO: {it['new']}")
                res = await cambiar_titulo(page, it["iid"], it["current"], it["new"])
                res["cuenta"] = cuenta
                log.append(res)
                print(f"     RESULTADO: {res['status']}")
                # Pequeño descanso entre items
                await page.wait_for_timeout(1500)

            await browser.close()
            print(f"  Cuenta {cuenta} terminada.")

    LOG_OUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for x in log if x["status"] == "OK")
    fail = sum(1 for x in log if x["status"] != "OK")
    print(f"\n=== Total: OK {ok} | FAIL {fail} ===\n LOG: {LOG_OUT}")


if __name__ == "__main__":
    asyncio.run(main())
