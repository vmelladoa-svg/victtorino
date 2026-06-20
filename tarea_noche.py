"""
tarea_noche.py — Trabajo autónomo nocturno NOVAGRIFERIAS3
Reglas críticas: NUNCA activar sin stock | NUNCA modificar precios
                 NUNCA cancelar ventas   | NUNCA responder preguntas
"""

import requests, json, time, re, sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
TOKENS_FILE  = BASE_DIR / "tokens_cuenta3.json"
REPORT_FILE  = BASE_DIR / "reporte_noche.txt"
ACTIVAS_FILE = BASE_DIR / "publicaciones_activas.json"
TODAS_FILE   = BASE_DIR / "publicaciones.json"
PEND_FILE    = BASE_DIR / "atributos_pendientes.json"
BASE_URL     = "https://api.mercadolibre.com"

reporte       = []
alertas       = []
acciones      = []
decisiones    = []
metricas      = {}
cat_cache     = {}
inicio        = datetime.now()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def log(msg):
    ts  = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    reporte.append(line)
    print(line)

def alerta(msg):
    alertas.append(msg)
    log(f"*** ALERTA: {msg}")

def accion(msg):
    acciones.append(msg)
    log(f"    ACCION: {msg}")

def decision(msg):
    decisiones.append(msg)
    log(f"    DECISION PENDIENTE: {msg}")

def token():
    return json.loads(TOKENS_FILE.read_text())["access_token"]

def headers(json_ct=False):
    h = {"Authorization": f"Bearer {token()}"}
    if json_ct:
        h["Content-Type"] = "application/json"
    return h

def get(url, params=None):
    try:
        r = requests.get(url, headers=headers(), params=params, timeout=15)
        return r.json() if r.ok else None
    except Exception as e:
        log(f"GET error {url}: {e}")
        return None

def put(url, body):
    try:
        r = requests.put(url, headers=headers(True), json=body, timeout=15)
        return r.ok, r.json()
    except Exception as e:
        return False, {"error": str(e)}

def refresh_token():
    data = json.loads(TOKENS_FILE.read_text())
    r = requests.post(f"{BASE_URL}/oauth/token", data={
        "grant_type":    "refresh_token",
        "client_id":     "3959231945649654",
        "client_secret": "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG",
        "refresh_token": data["refresh_token"],
    }, timeout=15)
    if r.ok:
        TOKENS_FILE.write_text(json.dumps(r.json(), indent=2))
        log("Token renovado OK")
    else:
        log(f"Error renovando token: {r.text}")

def cat_attrs(cat_id):
    if cat_id in cat_cache:
        return cat_cache[cat_id]
    data = get(f"{BASE_URL}/categories/{cat_id}/attributes") or []
    cat_cache[cat_id] = {a["id"]: a for a in data}
    time.sleep(0.15)
    return cat_cache[cat_id]

def save_report():
    lineas = "\n".join(reporte)
    REPORT_FILE.write_text(lineas, encoding="utf-8")

# ── AUTO-DEDUCCIÓN DE ATRIBUTOS ───────────────────────────────────────────────
def deducir_valor(attr_id, titulo, categoria, cat_attrs_map):
    t = titulo.lower()
    a = cat_attrs_map.get(attr_id, {})
    allowed = {v["name"].lower(): v for v in a.get("values", []) or a.get("allowed_values", [])}

    def match_allowed(candidates):
        for c in candidates:
            if c.lower() in allowed:
                v = allowed[c.lower()]
                return v.get("id"), v.get("name", c)
        return None, None

    # Fuente / Origen
    if attr_id in ("PRODUCT_DATA_SOURCE", "PRODUCT_ORIGIN"):
        vid, vname = match_allowed(["Importado", "Nacional", "Fabricante"])
        return vid, vname or "Importado"

    # Materiales / Material
    if attr_id in ("MATERIALS", "MATERIAL"):
        if any(x in t for x in ["inox", "inoxidable", "acero"]):
            vid, vname = match_allowed(["Acero inoxidable", "Acero"])
            return vid, vname or "Acero inoxidable"
        if "plastico" in t or "plástico" in t or "abs" in t or "pvc" in t:
            vid, vname = match_allowed(["Plástico", "ABS", "PVC"])
            return vid, vname or "Plástico"
        if "vidrio" in t:
            return match_allowed(["Vidrio"]) or (None, "Vidrio")
        if "laton" in t or "latón" in t or "bronce" in t:
            vid, vname = match_allowed(["Latón", "Bronce"])
            return vid, vname or "Latón"
        if "goma" in t or "caucho" in t:
            vid, vname = match_allowed(["Goma", "Caucho"])
            return vid, vname or "Goma"
        if "cromo" in t or "cromado" in t:
            return None, "Cromado"
        return None, "Acero inoxidable"

    # Acabado / Finish
    if attr_id in ("FINISH", "ACABADO"):
        if "plateado" in t:  return match_allowed(["Plateado", "Cromado"])  or (None, "Plateado")
        if "negro" in t:     return match_allowed(["Negro", "Mate negro"])  or (None, "Negro")
        if "blanco" in t:    return match_allowed(["Blanco"])               or (None, "Blanco")
        if "dorado" in t:    return match_allowed(["Dorado"])               or (None, "Dorado")
        return None, "Cromado"

    # Color
    if attr_id == "COLOR":
        if "negro" in t:    return match_allowed(["Negro"])    or (None, "Negro")
        if "blanco" in t:   return match_allowed(["Blanco"])   or (None, "Blanco")
        if "dorado" in t:   return match_allowed(["Dorado"])   or (None, "Dorado")
        return None, "Plateado"

    # Voltaje
    if attr_id == "VOLTAGE":
        if any(x in t for x in ["luz", "led", "luces", "espejo"]):
            vid, vname = match_allowed(["220V", "220 V", "100-240V"])
            return vid, vname or "220V"
        return None, "No aplica"

    # Lugar / Instalación
    if attr_id in ("INSTALLATION_PLACEMENT", "LUGAR_COLOCACION"):
        if "urinario" in t:                              return None, "Urinario"
        if any(x in t for x in ["lavaplatos","bacha"]): return None, "Cocina"
        if any(x in t for x in ["lavatorio","lavamanos"]): return None, "Baño"
        if any(x in t for x in ["tina","bañera"]):      return None, "Baño"
        return None, "Baño"

    # Consistencia jabón
    if attr_id in ("SOAP_CONSISTENCY", "CONSISTENCIAS_PRODUCTO"):
        vid, vname = match_allowed(["Líquido", "Liquido"])
        return vid, vname or "Líquido"

    # Tipo dosificación
    if attr_id in ("DISPENSING_TYPE", "TIPO_DOSIFICACION"):
        vid, vname = match_allowed(["Presión", "Presion", "Push"])
        return vid, vname or "Presión"

    # Habitaciones
    if attr_id in ("RECOMMENDED_INSTALLATION_ROOMS",):
        vid, vname = match_allowed(["Baño", "Bano"])
        return vid, vname or "Baño"

    # Tamaño / diámetro desde título
    if attr_id in ("SIZE", "TAMAÑO", "TAMA_O"):
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:\"|\"|pulgadas?|mm|cm)', t)
        if m: return None, m.group(1)
        m = re.search(r'(\d/\d)', t)
        if m: return None, m.group(1)

    # Diámetro conexión desde título
    if "DIAMETER" in attr_id or "DIAMETRO" in attr_id:
        m = re.search(r'(\d/\d)', t)
        if m: return None, m.group(1)
        m = re.search(r'(\d+)\s*mm', t)
        if m: return None, m.group(1)

    # Largo/Ancho/Alto desde título
    dims = re.findall(r'(\d+)[xX×](\d+)(?:[xX×](\d+))?', titulo)
    if attr_id in ("LENGTH", "LARGO") and dims:
        return None, dims[0][0]
    if attr_id in ("WIDTH", "ANCHO") and dims:
        return None, dims[0][1]
    if attr_id in ("DEPTH", "PROFUNDIDAD") and dims and dims[0][2]:
        return None, dims[0][2]
    if attr_id in ("HEIGHT", "ALTURA"):
        m = re.search(r'(\d+)\s*cm', t)
        if m: return None, m.group(1)

    # Temperatura agua
    if "WATER_TEMP" in attr_id:
        vid, vname = match_allowed(["Fría y caliente", "Fria y caliente"])
        return vid, vname or "Fría y caliente"

    return None, None


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 1 — ATRIBUTOS
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_atributos():
    log("=" * 60)
    log("TAREA 1: ATRIBUTOS")
    log("=" * 60)

    if not PEND_FILE.exists():
        log("No se encontró atributos_pendientes.json")
        return

    pendientes = json.loads(PEND_FILE.read_text(encoding="utf-8"))
    activas_raw = json.loads(ACTIVAS_FILE.read_bytes().decode("latin-1")) if ACTIVAS_FILE.exists() else []
    activas_idx = {i["id"]: i for i in activas_raw}

    skip_dims_fisicas = {
        "BATHTUBS_FAUCET_HEIGHT","BATHTUBS_FAUCET_LENGTH","BATHTUBS_FAUCET_WIDTH",
        "BIDET_FAUCET_WIDTH","HANDHELD_SHOWER_LENGTH","MAX_WATER_PRESSURE",
        "SINK_FAUCET_HEIGHT","SINK_FAUCET_LENGTH","SINK_FAUCET_WIDTH",
        "INSTALLATION_HOLE_DIAMETER","VALVE_WEIGHT","PACKAGE_HEIGHT",
        "PACKAGE_LENGTH","PACKAGE_WIDTH","PACKAGE_WEIGHT",
    }

    completados_cat  = defaultdict(int)
    pendientes_cat   = defaultdict(list)
    errores_aplicar  = []

    for item in pendientes:
        item_id   = item["id"]
        titulo    = item["titulo"]
        categoria = item["categoria"]
        full_item = activas_idx.get(item_id, {})

        cat_map = cat_attrs(categoria)

        for a in item["atributos"]:
            if a.get("value_to_set") and not str(a["value_to_set"]).startswith("ELEGIR"):
                continue
            if a["id"] in skip_dims_fisicas:
                continue

            vid, val = deducir_valor(a["id"], titulo, categoria, cat_map)
            if val:
                a["value_to_set"] = val
                a["_value_id"]    = vid
                completados_cat[categoria] += 1

    # Guardar JSON actualizado
    PEND_FILE.write_text(json.dumps(pendientes, indent=2, ensure_ascii=False), encoding="utf-8")
    total_auto = sum(completados_cat.values())
    log(f"Atributos auto-completados esta noche: {total_auto}")

    # Aplicar vía API en lotes
    aplicados = errores = 0
    for item in pendientes:
        attrs_enviar = []
        for a in item["atributos"]:
            val = a.get("value_to_set")
            if not val or str(val).startswith("ELEGIR"):
                continue
            entry = {"id": a["id"], "value_name": str(val)}
            if a.get("_value_id"):
                entry["value_id"] = a["_value_id"]
            attrs_enviar.append(entry)

        if not attrs_enviar:
            continue

        ok, resp = put(f"{BASE_URL}/items/{item['id']}", {"attributes": attrs_enviar})
        if ok:
            aplicados += len(attrs_enviar)
            accion(f"Atributos aplicados: {item['id']} ({len(attrs_enviar)} attrs) — {item['titulo'][:50]}")
        else:
            errores += 1
            msg = resp.get("message","")
            errores_aplicar.append({"id": item["id"], "error": msg})
            log(f"Error atributo {item['id']}: {msg}")
        time.sleep(0.3)

    log(f"Atributos aplicados: {aplicados} | Errores: {errores}")
    metricas["atributos_aplicados"] = aplicados
    metricas["atributos_errores"]   = errores

    # Atributos aún sin valor (dimensiones físicas y datos desconocidos)
    sin_valor = []
    for item in pendientes:
        for a in item["atributos"]:
            if not a.get("value_to_set") or str(a["value_to_set"]).startswith("ELEGIR"):
                if a["id"] not in skip_dims_fisicas:
                    sin_valor.append(f"{item['id']} / {a['name']} ({item['titulo'][:40]})")

    if sin_valor:
        decision(f"Atributos sin completar que requieren datos reales ({len(sin_valor)}):")
        for s in sin_valor[:20]:
            decision(f"  - {s}")
        if len(sin_valor) > 20:
            decision(f"  ... y {len(sin_valor)-20} más")


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 2 — PUBLICACIONES
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_publicaciones(user_id):
    log("=" * 60)
    log("TAREA 2: PUBLICACIONES")
    log("=" * 60)

    # Obtener todos los items frescos
    log("Descargando estado actual de publicaciones...")
    all_ids = []
    offset, limit = 0, 50
    while True:
        r = get(f"{BASE_URL}/users/{user_id}/items/search", {"offset": offset, "limit": limit})
        if not r: break
        all_ids.extend(r.get("results", []))
        offset += limit
        if offset >= r.get("paging", {}).get("total", 0): break

    # Descargar detalle en lotes de 20
    items_frescos = []
    for i in range(0, len(all_ids), 20):
        chunk = ",".join(all_ids[i:i+20])
        r = get(f"{BASE_URL}/items", {"ids": chunk})
        if r:
            for entry in r:
                if entry.get("code") == 200:
                    items_frescos.append(entry["body"])
        time.sleep(0.2)

    log(f"Publicaciones obtenidas: {len(items_frescos)}")

    pausadas_con_stock  = [i for i in items_frescos if i.get("status") == "paused"  and i.get("available_quantity", 0) > 0]
    activas_sin_stock   = [i for i in items_frescos if i.get("status") == "active"  and i.get("available_quantity", 0) == 0]
    todas_activas       = [i for i in items_frescos if i.get("status") == "active"]

    log(f"Pausadas con stock > 0: {len(pausadas_con_stock)}")
    log(f"Activas con stock = 0 : {len(activas_sin_stock)}")
    log(f"Total activas         : {len(todas_activas)}")

    metricas["total_publicaciones"]   = len(items_frescos)
    metricas["activas"]               = len(todas_activas)
    metricas["pausadas_con_stock"]    = len(pausadas_con_stock)
    metricas["activas_sin_stock"]     = len(activas_sin_stock)

    if activas_sin_stock:
        alerta(f"{len(activas_sin_stock)} publicaciones ACTIVAS con stock 0 — se pausarán ahora")

    # Reactivar pausadas con stock > 0
    reactivadas = 0
    for item in pausadas_con_stock:
        ok, resp = put(f"{BASE_URL}/items/{item['id']}", {"status": "active"})
        if ok:
            reactivadas += 1
            accion(f"REACTIVADA: {item['id']} stock={item['available_quantity']} — {item['title'][:50]}")
        else:
            log(f"Error reactivando {item['id']}: {resp.get('message','')}")
        time.sleep(0.3)

    # Pausar activas con stock 0
    pausadas = 0
    for item in activas_sin_stock:
        ok, resp = put(f"{BASE_URL}/items/{item['id']}", {"status": "paused"})
        if ok:
            pausadas += 1
            accion(f"PAUSADA (sin stock): {item['id']} — {item['title'][:50]}")
        else:
            log(f"Error pausando {item['id']}: {resp.get('message','')}")
        time.sleep(0.3)

    log(f"Reactivadas: {reactivadas} | Pausadas por sin stock: {pausadas}")
    metricas["reactivadas"]   = reactivadas
    metricas["pausadas_hoy"]  = pausadas

    # Preguntas sin responder (para Task 8 también)
    log("Consultando preguntas sin responder...")
    q = get(f"{BASE_URL}/questions/search", {"seller_id": user_id, "status": "UNANSWERED", "limit": 50})
    preguntas = q.get("questions", []) if q else []
    log(f"Preguntas sin responder: {len(preguntas)}")
    metricas["preguntas_sin_responder"] = len(preguntas)

    return items_frescos, preguntas


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 3 — REPUTACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_reputacion(user_id):
    log("=" * 60)
    log("TAREA 3: REPUTACIÓN")
    log("=" * 60)

    r = get(f"{BASE_URL}/users/{user_id}/seller_reputation")
    if not r:
        log("No se pudo obtener reputación")
        return

    nivel        = r.get("level_id", "?")
    poder_venta  = r.get("power_seller_status", "?")
    transacciones = r.get("transactions", {})
    metricas_rep  = r.get("metrics", {})

    total_t   = transacciones.get("total", 0)
    canceladas = transacciones.get("canceled", {})
    pct_cancel = canceladas.get("rate", 0) * 100
    pct_reclamos = (metricas_rep.get("claims", {}).get("rate", 0) or 0) * 100
    pct_envios   = (metricas_rep.get("delayed_handling_time", {}).get("rate", 0) or 0) * 100

    colores = {
        "1_red": "ROJO", "2_orange": "NARANJA", "3_yellow": "AMARILLO",
        "4_light_green": "VERDE CLARO", "5_green": "VERDE"
    }
    color = colores.get(nivel, nivel)

    log(f"Nivel: {color} | Vendedor: {poder_venta}")
    log(f"Transacciones totales: {total_t}")
    log(f"% Cancelaciones  : {pct_cancel:.2f}%  (límite 2%)")
    log(f"% Reclamos       : {pct_reclamos:.2f}%  (límite 2%)")
    log(f"% Envíos tardíos : {pct_envios:.2f}%  (límite 10%)")

    metricas["reputacion_nivel"]      = color
    metricas["reputacion_cancelaciones"] = f"{pct_cancel:.2f}%"
    metricas["reputacion_reclamos"]   = f"{pct_reclamos:.2f}%"
    metricas["reputacion_envios_tardios"] = f"{pct_envios:.2f}%"

    if pct_cancel > 1.5:
        alerta(f"Cancelaciones en {pct_cancel:.2f}% — cercano al límite del 2%")
    if pct_reclamos > 1.5:
        alerta(f"Reclamos en {pct_reclamos:.2f}% — cercano al límite del 2%")
    if pct_envios > 8:
        alerta(f"Envíos tardíos en {pct_envios:.2f}% — cercano al límite del 10%")

    en_riesgo = pct_cancel > 1.5 or pct_reclamos > 1.5 or pct_envios > 8
    metricas["reputacion_en_riesgo"] = "SÍ" if en_riesgo else "NO"
    if not en_riesgo:
        log("Reputación estable — sin riesgo de bajar de nivel")


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 4 — VENTAS
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_ventas(user_id):
    log("=" * 60)
    log("TAREA 4: VENTAS ÚLTIMAS 24 HORAS")
    log("=" * 60)

    ahora    = datetime.utcnow()
    hace_24h = (ahora - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.000-00:00")
    ayer_24h = (ahora - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%S.000-00:00")

    def get_orders(desde, hasta_str=None):
        params = {"seller": user_id, "sort": "date_asc",
                  "order.date_created.from": desde, "limit": 50}
        ordenes, offset = [], 0
        while True:
            params["offset"] = offset
            r = get(f"{BASE_URL}/orders/search", params)
            if not r: break
            batch = r.get("results", [])
            ordenes.extend(batch)
            offset += 50
            if offset >= r.get("paging", {}).get("total", 0): break
            time.sleep(0.2)
        return ordenes

    ordenes_hoy  = get_orders(hace_24h)
    ordenes_ayer = get_orders(ayer_24h, hace_24h)

    def calcular(ordenes):
        gmv = sum(o.get("total_amount", 0) for o in ordenes)
        tickets = [o.get("total_amount", 0) for o in ordenes if o.get("total_amount", 0) > 0]
        ticket_prom = sum(tickets) / len(tickets) if tickets else 0

        por_hora = defaultdict(float)
        ventas_items = defaultdict(lambda: {"titulo": "", "qty": 0, "monto": 0})
        for o in ordenes:
            fecha = o.get("date_created", "")[:13]
            hora  = fecha[11:13] if len(fecha) >= 13 else "00"
            por_hora[hora] += o.get("total_amount", 0)
            for item in o.get("order_items", []):
                iid = item.get("item", {}).get("id", "")
                ventas_items[iid]["titulo"] = item.get("item", {}).get("title", "")[:40]
                ventas_items[iid]["qty"]   += item.get("quantity", 0)
                ventas_items[iid]["monto"] += item.get("unit_price", 0) * item.get("quantity", 0)
        return gmv, ticket_prom, len(ordenes), por_hora, ventas_items

    gmv_hoy,  tp_hoy,  n_hoy,  xhora_hoy,  vitems_hoy  = calcular(ordenes_hoy)
    gmv_ayer, tp_ayer, n_ayer, xhora_ayer, vitems_ayer  = calcular(ordenes_ayer)

    log(f"Pedidos hoy  : {n_hoy}  | GMV: ${gmv_hoy:,.0f} CLP | Ticket prom: ${tp_hoy:,.0f}")
    log(f"Pedidos ayer : {n_ayer} | GMV: ${gmv_ayer:,.0f} CLP | Ticket prom: ${tp_ayer:,.0f}")
    var_gmv = ((gmv_hoy - gmv_ayer) / gmv_ayer * 100) if gmv_ayer else 0
    log(f"Variación GMV vs ayer: {var_gmv:+.1f}%")

    if xhora_hoy:
        pico  = max(xhora_hoy, key=xhora_hoy.get)
        valle = min(xhora_hoy, key=xhora_hoy.get)
        log(f"Hora pico  : {pico}h — ${xhora_hoy[pico]:,.0f}")
        log(f"Hora valle : {valle}h — ${xhora_hoy[valle]:,.0f}")
        metricas["hora_pico"]  = f"{pico}h"
        metricas["hora_valle"] = f"{valle}h"

    top5 = sorted(vitems_hoy.values(), key=lambda x: x["qty"], reverse=True)[:5]
    log("Top 5 productos hoy:")
    for i, p in enumerate(top5, 1):
        log(f"  {i}. {p['titulo']} — {p['qty']} uds — ${p['monto']:,.0f}")

    metricas["gmv_hoy"]        = f"${gmv_hoy:,.0f} CLP"
    metricas["pedidos_hoy"]    = n_hoy
    metricas["ticket_promedio"] = f"${tp_hoy:,.0f} CLP"
    metricas["var_gmv_vs_ayer"] = f"{var_gmv:+.1f}%"

    if var_gmv < -20:
        alerta(f"GMV cayó {var_gmv:.1f}% vs ayer — revisar campañas y stock")

    return vitems_hoy


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 5 — STOCK Y ALERTAS
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_stock(items_frescos):
    log("=" * 60)
    log("TAREA 5: STOCK Y ALERTAS")
    log("=" * 60)

    critico    = [i for i in items_frescos if i.get("status") == "active" and 0 < i.get("available_quantity",0) <= 3]
    sin_mov    = [i for i in items_frescos if i.get("status") == "active"
                  and i.get("sold_quantity", 0) == 0
                  and i.get("available_quantity", 0) > 0]
    valor_inv  = sum(i.get("price", 0) * i.get("available_quantity", 0)
                     for i in items_frescos if i.get("status") == "active")

    log(f"Stock crítico (1-3 uds activos) : {len(critico)}")
    log(f"Sin movimiento (0 ventas)       : {len(sin_mov)}")
    log(f"Valor inventario publicado      : ${valor_inv:,.0f} CLP")

    metricas["stock_critico"]   = len(critico)
    metricas["sin_movimiento"]  = len(sin_mov)
    metricas["valor_inventario"] = f"${valor_inv:,.0f} CLP"

    if critico:
        alerta(f"{len(critico)} productos con stock crítico (1-3 unidades):")
        for i in sorted(critico, key=lambda x: x.get("available_quantity", 0))[:10]:
            alerta(f"  - {i['id']} stock={i['available_quantity']} — {i['title'][:50]}")

    return critico


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 6 — PUBLICIDAD
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_publicidad(user_id):
    log("=" * 60)
    log("TAREA 6: PUBLICIDAD")
    log("=" * 60)

    r = get(f"{BASE_URL}/advertising/product_ads/{user_id}/campaigns")
    if not r or "error" in r:
        log("API de publicidad no disponible con el token actual (requiere scope ads_read)")
        decision("Publicidad: revisar campañas manualmente en el Panel de Publicidad de MercadoLibre")
        metricas["publicidad"] = "No disponible via API — revisar panel"
        return

    campanas = r.get("results", [])
    log(f"Campañas activas: {len(campanas)}")
    bajo_roas = []
    for c in campanas:
        nombre  = c.get("name", "?")
        roas    = c.get("roas", 0)
        acos    = c.get("acos", 0)
        ctr     = c.get("ctr", 0)
        gastado = c.get("total_amount", 0)
        presup  = c.get("daily_budget", 0)
        log(f"  {nombre}: ROAS={roas:.1f}x ACOS={acos:.1f}% CTR={ctr:.2f}% Gasto=${gastado:,.0f}")
        if roas < 3:
            bajo_roas.append(nombre)

    if bajo_roas:
        decision(f"Campañas con ROAS < 3x (requieren tu decisión para pausar): {', '.join(bajo_roas)}")
        alerta(f"{len(bajo_roas)} campaña(s) con ROAS bajo 3x — ver sección DECISIONES PENDIENTES")


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 7 — COMPETENCIA
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_competencia(top_items):
    log("=" * 60)
    log("TAREA 7: COMPETENCIA — TOP 5 PRODUCTOS")
    log("=" * 60)

    if not top_items:
        log("Sin datos de ventas para comparar competencia")
        return

    top5_ids = list(top_items.keys())[:5]

    for item_id in top5_ids:
        info   = top_items[item_id]
        titulo = info["titulo"]

        # Buscar competidores por palabras clave del título
        keywords = " ".join(titulo.split()[:5])
        r = get(f"{BASE_URL}/sites/MLC/search", {"q": keywords, "limit": 5})
        if not r:
            continue

        resultados = r.get("results", [])
        precios_comp = [
            x.get("price", 0) for x in resultados
            if x.get("id") != item_id and x.get("available_quantity", 0) > 0
        ]

        if precios_comp:
            minimo = min(precios_comp)
            log(f"  {item_id} — {titulo}")
            log(f"    Precio más bajo competencia: ${minimo:,.0f} CLP")
        time.sleep(0.3)


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 8 — PREGUNTAS
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_preguntas(preguntas):
    log("=" * 60)
    log("TAREA 8: PREGUNTAS SIN RESPONDER")
    log("=" * 60)
    log(f"Total preguntas sin responder: {len(preguntas)}")

    ahora = datetime.utcnow()
    for p in preguntas:
        fecha_str = p.get("date_created", "")[:10]
        try:
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
            dias     = (ahora - fecha_dt).days
        except:
            dias = 0
        urgencia = "ALTA" if dias >= 2 else "MEDIA" if dias == 1 else "BAJA"
        item_id  = p.get("item_id", "?")
        texto    = p.get("text", "")[:80]
        log(f"  [{urgencia}] {item_id} ({fecha_str}) — {texto}")

    if any(p for p in preguntas if (ahora - datetime.strptime(p.get("date_created","")[:10], "%Y-%m-%d")).days >= 2
                                    if p.get("date_created","")):
        alerta("Hay preguntas con más de 48h sin responder — responder afecta reputación")

    decision(f"Responder {len(preguntas)} pregunta(s) pendiente(s) — NUNCA lo hago autónomamente")


# ═══════════════════════════════════════════════════════════════════════════════
# TAREA 9 — SEO Y OPTIMIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
def tarea_seo(items_frescos):
    log("=" * 60)
    log("TAREA 9: SEO Y OPTIMIZACIÓN")
    log("=" * 60)

    activos = [i for i in items_frescos if i.get("status") == "active"]

    # Identificar publicaciones sin descripción
    log("Verificando descripciones...")
    sin_desc = []
    for item in activos[:50]:  # Muestra de 50 para no saturar la API
        r = get(f"{BASE_URL}/items/{item['id']}/description")
        if r:
            texto = r.get("plain_text", "").strip()
            if len(texto) < 30:
                sin_desc.append(item)
        time.sleep(0.15)

    log(f"Publicaciones sin descripción (muestra 50): {len(sin_desc)}")
    if sin_desc:
        decision(f"Agregar descripción a {len(sin_desc)} publicaciones detectadas en muestra:")
        for i in sin_desc[:5]:
            decision(f"  - {i['id']} — {i['title'][:50]}")

    # 5 publicaciones con menor conversión (sold_quantity / visitas estimadas por health)
    candidatas = sorted(
        [i for i in activos if i.get("sold_quantity", 0) == 0 and i.get("available_quantity", 0) > 0],
        key=lambda x: x.get("health", 0) or 0
    )[:5]

    log("Top 5 con menor conversión — sugerencias de título:")
    for item in candidatas:
        titulo   = item.get("title", "")
        palabras = len(titulo.split())
        fotos    = len(item.get("pictures", []))
        health   = int((item.get("health") or 0) * 100)

        sugerencias = []
        if palabras < 7:
            sugerencias.append("título muy corto — agregar marca, modelo y material")
        if fotos < 5:
            sugerencias.append(f"pocas fotos ({fotos}) — agregar hasta 8")
        if health < 60:
            sugerencias.append(f"health {health}% — completar atributos")

        log(f"  {item['id']} health={health}% fotos={fotos}")
        log(f"    Título: {titulo}")
        for s in sugerencias:
            log(f"    → {s}")

    metricas["sin_descripcion_muestra"] = len(sin_desc)


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTE FINAL
# ═══════════════════════════════════════════════════════════════════════════════
def generar_reporte():
    fin      = datetime.now()
    duracion = fin - inicio

    sep  = "═" * 65
    sep2 = "─" * 65

    lineas = [
        sep,
        "  REPORTE NOCTURNO — NOVAGRIFERIAS3",
        f"  Inicio : {inicio.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Fin    : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Duración: {str(duracion).split('.')[0]}",
        sep,
        "",
        "1. RESUMEN EJECUTIVO",
        sep2,
    ]
    lineas += [l for l in reporte if not l.startswith("[") or "TAREA" in l or "Total" in l or "Error" in l]

    lineas += ["", "2. ALERTAS CRÍTICAS", sep2]
    if alertas:
        lineas += [f"  ⚠  {a}" for a in alertas]
    else:
        lineas.append("  Sin alertas críticas.")

    lineas += ["", "3. ACCIONES EJECUTADAS", sep2]
    if acciones:
        lineas += [f"  ✓  {a}" for a in acciones]
    else:
        lineas.append("  Sin acciones ejecutadas.")

    lineas += ["", "4. DECISIONES PENDIENTES — REQUIEREN TU APROBACIÓN", sep2]
    if decisiones:
        lineas += [f"  →  {d}" for d in decisiones]
    else:
        lineas.append("  Sin decisiones pendientes.")

    lineas += ["", "5. MÉTRICAS CLAVE", sep2]
    for k, v in metricas.items():
        lineas.append(f"  {k:<35} {v}")

    lineas += ["", sep, "  FIN DEL REPORTE", sep]

    contenido = "\n".join(lineas)
    REPORT_FILE.write_text(contenido, encoding="utf-8")
    print(f"\nReporte guardado en: {REPORT_FILE}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log("Iniciando trabajo nocturno NOVAGRIFERIAS3")
    log(f"Fecha: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")

    # Renovar token primero
    refresh_token()

    # Obtener user_id
    me = get(f"{BASE_URL}/users/me")
    if not me:
        log("ERROR: No se pudo conectar a la API")
        generar_reporte()
        sys.exit(1)

    user_id  = me["id"]
    nickname = me["nickname"]
    log(f"Conectado como: {nickname} (ID: {user_id})")

    try:
        tarea_atributos()
        save_report()
    except Exception as e:
        log(f"Error en tarea_atributos: {e}")

    items_frescos = []
    preguntas     = []
    try:
        items_frescos, preguntas = tarea_publicaciones(user_id)
        save_report()
    except Exception as e:
        log(f"Error en tarea_publicaciones: {e}")

    try:
        tarea_reputacion(user_id)
        save_report()
    except Exception as e:
        log(f"Error en tarea_reputacion: {e}")

    top_items = {}
    try:
        top_items = tarea_ventas(user_id)
        save_report()
    except Exception as e:
        log(f"Error en tarea_ventas: {e}")

    try:
        tarea_stock(items_frescos)
        save_report()
    except Exception as e:
        log(f"Error en tarea_stock: {e}")

    try:
        tarea_publicidad(user_id)
        save_report()
    except Exception as e:
        log(f"Error en tarea_publicidad: {e}")

    try:
        tarea_competencia(top_items)
        save_report()
    except Exception as e:
        log(f"Error en tarea_competencia: {e}")

    try:
        tarea_preguntas(preguntas)
        save_report()
    except Exception as e:
        log(f"Error en tarea_preguntas: {e}")

    try:
        tarea_seo(items_frescos)
        save_report()
    except Exception as e:
        log(f"Error en tarea_seo: {e}")

    generar_reporte()
    log("Trabajo nocturno COMPLETADO")
