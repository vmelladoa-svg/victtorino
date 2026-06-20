"""
Test integral de Victoria — verifica TODOS los parametros del agente.

1. Health del servicio en Railway
2. Tokens ML de las 3 cuentas
3. Webhook handler (verificacion GET)
4. Comportamiento conversacional con Claude (casos especiales del prompt)
5. Brain — generacion de respuestas para mensaje WA tipico
6. Casos especiales:
   - Granito (debe rechazar)
   - Politica de canales (no mencionar ML/Falabella)
   - Politica de competencia (no comparar)
   - Objeciones de precio
   - Productos top
   - Envios y precios
   - Tienda fisica
   - Horario fuera de atencion
7. ML monitor — preguntas pendientes
8. Order poller — ordenes recientes
"""
import sys
import io
import json
import asyncio
import time
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
VICTORIA_URL = "https://victoria-agente-production.up.railway.app"


def header(t):
    print(f"\n{'='*70}\n  {t}\n{'='*70}")


def chk(ok, msg):
    s = "✓" if ok else "✗"
    print(f"  [{s}] {msg}")
    return ok


# ────────────────────────────────────────────────────────
# 1. Health del servicio
# ────────────────────────────────────────────────────────
def test_health():
    header("1. HEALTH DEL SERVICIO")
    r = requests.get(f"{VICTORIA_URL}/", timeout=10)
    ok1 = chk(r.status_code == 200, f"HTTP {r.status_code} en /")
    try:
        j = r.json()
        ok2 = chk(j.get("status") == "ok", f"status = {j.get('status')!r}")
        ok3 = chk(j.get("agente") == "Victoria", f"agente = {j.get('agente')!r}")
    except Exception as e:
        ok2 = ok3 = chk(False, f"body no es JSON: {e}")
    return ok1 and ok2 and ok3


# ────────────────────────────────────────────────────────
# 2. Tokens ML
# ────────────────────────────────────────────────────────
def test_tokens_ml():
    header("2. TOKENS MERCADOLIBRE (3 cuentas)")
    todos_ok = True
    for n in (1, 2, 3):
        path = ROOT / f"tokens_cuenta{n}.json"
        if not path.exists():
            chk(False, f"tokens_cuenta{n}.json no existe")
            todos_ok = False
            continue
        t = json.loads(path.read_text())["access_token"]
        r = requests.get("https://api.mercadolibre.com/users/me",
                         headers={"Authorization": f"Bearer {t}"}, timeout=10)
        ok = chk(r.status_code == 200, f"C{n} token valido (HTTP {r.status_code})")
        if not ok: todos_ok = False
    return todos_ok


# ────────────────────────────────────────────────────────
# 3. Webhook verificacion GET (Meta)
# ────────────────────────────────────────────────────────
def test_webhook_verify():
    header("3. WEBHOOK VERIFICACION (Meta GET)")
    r = requests.get(f"{VICTORIA_URL}/webhook/meta",
                     params={"hub.mode": "subscribe",
                             "hub.verify_token": "Victtorino2026",
                             "hub.challenge": "test123"},
                     timeout=10)
    ok = chk(r.status_code == 200 and "test123" in r.text,
             f"GET /webhook/meta con verify_token correcto → {r.status_code}: {r.text[:50]}")
    return ok


# ────────────────────────────────────────────────────────
# 4-7. Brain — Casos especiales conversacionales
# ────────────────────────────────────────────────────────
async def test_casos_brain():
    """Llama directamente al brain.py de victoria-agente con casos especiales."""
    header("4. BRAIN — CASOS ESPECIALES")
    import os
    os.chdir(ROOT / "victoria-agente")  # cwd correcto para cargar config/prompts.yaml
    sys.path.insert(0, str(ROOT / "victoria-agente"))
    from agent.brain import generar_respuesta

    casos = [
        {
            "id": "granito",
            "mensaje": "Tienen lavaplatos de granito?",
            "debe_contener": ["no trabajamos", "granito", "acero inox"],
            "no_debe_contener": ["sí tenemos granito"],
            "descripcion": "Debe rechazar granito y ofrecer alternativa acero inox",
        },
        {
            "id": "no_mencionar_ml",
            "mensaje": "Donde puedo comprar online?",
            "debe_contener": ["victtorino.cl"],
            "no_debe_contener": ["mercadolibre", "mercado libre", "falabella", "paris", "walmart"],
            "descripcion": "Solo debe mencionar victtorino.cl, NUNCA ML/Falabella/etc",
        },
        {
            "id": "precio_envio",
            "mensaje": "Cuanto cuesta el envio a la region metropolitana?",
            "debe_contener": ["2.490", "50.000"],
            "no_debe_contener": [],
            "descripcion": "Debe dar precio RM y mencionar envio gratis sobre $50.000",
        },
        {
            "id": "objecion_precio",
            "mensaje": "Esta muy caro. Lo vi mas barato en otro lugar.",
            "debe_contener": ["garantía", "calidad"],
            "no_debe_contener": ["te hago descuento", "te lo dejo en", "bajamos el precio"],
            "descripcion": "No debe bajar precio; debe destacar valor",
        },
        {
            "id": "tienda_fisica",
            "mensaje": "Tienen tienda fisica? Donde queda?",
            "debe_contener": ["Madame Adriana Bolland", "Cisterna"],
            "no_debe_contener": [],
            "descripcion": "Debe dar direccion de tienda fisica",
        },
        {
            "id": "horario",
            "mensaje": "Cual es su horario de atencion?",
            "debe_contener": ["lunes", "viernes", "9", "6"],
            "no_debe_contener": [],
            "descripcion": "Debe dar horario L-V 9-18",
        },
        {
            "id": "producto_top",
            "mensaje": "Tienen lavaplatos empotrados?",
            "debe_contener": ["lavaplatos"],
            "no_debe_contener": [],
            "descripcion": "Debe mencionar al menos un lavaplatos del catalogo",
        },
        {
            "id": "medios_pago",
            "mensaje": "Como puedo pagar?",
            "debe_contener": ["tarjeta", "Webpay"],
            "no_debe_contener": ["transferencia bancaria"],
            "descripcion": "Debe mencionar Webpay/tarjetas, NUNCA transferencia",
        },
    ]

    resultados = []
    for c in casos:
        try:
            respuesta = await generar_respuesta(c["mensaje"], [])
            resp_lower = respuesta.lower()
            falta = [w for w in c["debe_contener"] if w.lower() not in resp_lower]
            prohibido = [w for w in c["no_debe_contener"] if w.lower() in resp_lower]
            ok = not falta and not prohibido
            print(f"\n  [{c['id']}] {c['descripcion']}")
            print(f"    Q: {c['mensaje']}")
            print(f"    R: {respuesta[:180]}{'...' if len(respuesta)>180 else ''}")
            if falta: print(f"    ⚠ FALTA: {falta}")
            if prohibido: print(f"    ✗ PROHIBIDO presente: {prohibido}")
            chk(ok, f"caso {c['id']}: {'OK' if ok else 'FALLA'}")
            resultados.append(ok)
        except Exception as e:
            print(f"\n  [{c['id']}] ERROR: {e}")
            resultados.append(False)

    return all(resultados)


# ────────────────────────────────────────────────────────
# 5. ML — Preguntas pendientes (snapshot via API)
# ────────────────────────────────────────────────────────
def test_ml_estado():
    header("5. ESTADO ML")
    for n in (1, 2, 3):
        creds = json.loads((ROOT / f"tokens_cuenta{n}.json").read_text())
        token = creds["access_token"]; uid = creds["user_id"]
        r = requests.get("https://api.mercadolibre.com/my/received_questions/search",
                         headers={"Authorization": f"Bearer {token}"},
                         params={"status": "UNANSWERED", "limit": 1}, timeout=10)
        preg = r.json().get("total", "?") if r.status_code == 200 else "ERR"
        from datetime import datetime, timedelta, timezone
        desde = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.000-00:00")
        r2 = requests.get("https://api.mercadolibre.com/orders/search",
                          headers={"Authorization": f"Bearer {token}"},
                          params={"seller": uid, "order.date_created.from": desde,
                                  "limit": 1}, timeout=10)
        ord24 = r2.json().get("paging", {}).get("total", "?") if r2.status_code == 200 else "ERR"
        chk(preg != "ERR" and ord24 != "ERR",
            f"C{n}: {preg} pregs pendientes | {ord24} ord 24h")


# ────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────
async def main():
    print("════════════════════════════════════════════════════════")
    print("  TEST INTEGRAL DE VICTORIA")
    print("════════════════════════════════════════════════════════")

    resultados = {}
    resultados["health"]     = test_health()
    resultados["tokens_ml"]  = test_tokens_ml()
    resultados["webhook"]    = test_webhook_verify()
    test_ml_estado()  # informativo
    resultados["brain"]      = await test_casos_brain()

    print(f"\n{'='*70}\n  RESUMEN\n{'='*70}")
    for k, v in resultados.items():
        print(f"  {'✓' if v else '✗'} {k}")
    todos = all(resultados.values())
    print(f"\n  >>> {'TODOS OK ✓' if todos else 'HAY FALLAS ✗'} <<<")


if __name__ == "__main__":
    asyncio.run(main())
