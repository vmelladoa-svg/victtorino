"""
Aplica en bloque:
1. Elimina los 4 duplicados decididos por Victor (suma stock al sobreviviente):
   - Par A: trash 3024, mantener 2909 (40cm 2,5cm)
   - Par B: trash 2885, mantener 2983 (60cm 3,2cm)
   - Par C: trash 2876, mantener 2828 (sobreponer 80x50)
   - Par D: trash 2568, mantener 2739 (acrílico)
2. Aplica focus únicos a los 41 productos restantes con focus duplicado.
3. Reporta los 4 nuevos redirects.
"""
import json
import sys
import io
import time
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}


def get(pid):
    return requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30).json()


def put(pid, body):
    r = requests.put(f"{WC}/wp-json/wc/v3/products/{pid}", json=body, params=P, timeout=60)
    return r.json(), r.status_code


def trash(pid):
    return requests.delete(f"{WC}/wp-json/wc/v3/products/{pid}",
                           params={**P, "force": "false"}, timeout=60).json()


# ============================================================
# FASE 1: ELIMINAR DUPLICADOS + SUMAR STOCKS
# ============================================================
PARES = [
    # (eliminar, mantener)
    (3024, 2909),  # A
    (2885, 2983),  # B
    (2876, 2828),  # C
    (2568, 2739),  # D
]

print("=" * 80)
print("FASE 1 — Eliminar 4 duplicados y consolidar stock")
print("=" * 80)
redirects_nuevos = []
for elim_id, mant_id in PARES:
    elim = get(elim_id)
    mant = get(mant_id)
    elim_stock = elim.get("stock_quantity") or 0
    mant_stock = mant.get("stock_quantity") or 0
    new_stock = elim_stock + mant_stock
    elim_slug = elim.get("slug", "")
    mant_link = mant.get("permalink", "")

    # Sumar stock al mantenido
    if elim_stock > 0:
        put(mant_id, {"stock_quantity": new_stock, "manage_stock": True})
        print(f"  {mant_id}: stock {mant_stock} + {elim_stock} = {new_stock}")
    else:
        print(f"  {mant_id}: stock sin cambios ({mant_stock}, eliminado tenía {elim_stock})")
    # Trash al duplicado
    trash(elim_id)
    print(f"  {elim_id} -> trash ({elim.get('name','')[:50]})")
    # Acumular redirect
    redirects_nuevos.append({
        "source": f"/producto/{elim_slug}/",
        "destination": mant_link,
        "origen": f"par eliminado {elim_id} → {mant_id}",
    })
    print()

# ============================================================
# FASE 2: APLICAR FOCUS ÚNICOS
# ============================================================
print("=" * 80)
print("FASE 2 — Aplicar focus únicos a 41 productos")
print("=" * 80)

# Lista final de (pid, nuevo_focus, meta_title, meta_desc)
# Para los sobrevivientes de pares conflictivos, simplifico el focus porque ya no hay competidor.
def mt(focus, brand_suffix="| Victtorino"):
    t = f"{focus.title()} {brand_suffix}"
    if len(t) > 60:
        t = f"{focus.title()[:60 - len(brand_suffix) - 1]} {brand_suffix}"
    return t


def md(focus):
    return (f"{focus.capitalize()}. Calidad Victtorino, diseño moderno y "
            "materiales resistentes. Despacho a todo Chile.")[:155]


UPDATES = [
    # llave grifería (9)
    (3129, "llave monomando lavaplato"),
    (3126, "mezcladora baño cromado"),
    (3095, "llave lavatorio victtorino"),
    (2838, "llave lavacopas plateado"),
    (2803, "llave lavacopas notte negro"),
    (2797, "llave temporizada lavatorio"),
    (2778, "llave monomando lavatorio modern"),
    (2765, "flexible agua 35 cm"),
    (2727, "llave monomando domenica"),

    # agarradera baño (6 → 4 tras eliminación)
    (3088, "agarradera esquinera 3 apoyos"),
    (2762, "barra seguridad recta 30 cm"),
    (2909, "barra seguridad recta 40 cm"),
    (2983, "barra seguridad recta 60 cm"),

    # accesorios baño (3)
    (2999, "plato ducha redondo 20 cm"),
    (2873, "brazo ducha al muro 30 cm"),
    (2770, "brazo ducha al muro 40 cm"),

    # lavaplatos cocina (7 → 6 tras eliminación)
    (2992, "pack lavaplatos 80x44 domenica"),
    (2960, "pack lavaplatos 80x44 izquierdo"),
    (2938, "pack lavaplatos 80x44 colomba"),
    (2923, "lavaplatos empotrable 80x50 hannover"),
    (2828, "lavaplatos sobreponer 80x50"),
    (2793, "lavaplatos simple 80x44 derecho"),

    # dispensador de jabón (4)
    (2968, "dispensador jabón acero inoxidable 800ml"),
    (2852, "dispensador jabón acero inoxidable 500ml"),
    (2816, "dispensador jabón täumm 500ml"),
    (2551, "dispensador jabón negro schwartz"),

    # dispensador papel higiénico (5 → 4 tras eliminación)
    (2926, "papel higiénico industrial 216 metros"),
    (2865, "dispensador papel toalla interfoliada"),
    (2824, "dispensador papel higiénico acero inoxidable"),
    (2739, "dispensador papel higiénico acrílico"),

    # sifón desagüe (6)
    (2914, "sifón codo 90"),
    (2896, "sifón botella 1 1/4"),
    (2892, "sifón codo 1 1/4 lavatorio"),
    (2857, "sifón desagüe 1 1/2"),
    (2844, "accesorios desagüe lavatorio"),
    (2834, "sifón tina receptáculo 1 1/2"),

    # basurero pedal baño (3)
    (2634, "basurero pedal 12 litros"),
    (2620, "basurero pedal 5 litros gris"),
    (2615, "basurero pedal 5 litros plateado"),

    # espejo doble cara aumento (2)
    (2611, "espejo doble cara aumento muro"),
    (2590, "espejo doble cara aumento pedestal"),
]

print(f"\nAplicando focus a {len(UPDATES)} productos...\n")
ok = 0
for pid, focus in UPDATES:
    body = {
        "meta_data": [
            {"key": "rank_math_title", "value": mt(focus)},
            {"key": "rank_math_description", "value": md(focus)},
            {"key": "rank_math_focus_keyword", "value": focus},
        ],
    }
    d, code = put(pid, body)
    if code < 400:
        new_fk = next((m["value"] for m in d.get("meta_data", [])
                       if m["key"] == "rank_math_focus_keyword"), "")
        print(f"  {pid}  -> \"{new_fk}\"")
        ok += 1
    else:
        print(f"  {pid}  ERR {code}")
    time.sleep(0.3)

print(f"\n{ok}/{len(UPDATES)} focus actualizados\n")

# Reportar redirects
print("=" * 80)
print(f"NUEVOS REDIRECTS (agregar a redirects_pendientes.md):")
print("=" * 80)
for r in redirects_nuevos:
    print(f"  Source:      {r['source']}")
    print(f"  Destination: {r['destination']}")
    print(f"  Origen:      {r['origen']}")
    print()

# Guardar
with open(r"C:\Users\dell\victtorino\focus_diferenciados_resultado.json", "w", encoding="utf-8") as f:
    json.dump({"eliminados": [p[0] for p in PARES],
               "mantenidos": [p[1] for p in PARES],
               "focus_aplicados": UPDATES,
               "redirects_nuevos": redirects_nuevos}, f, ensure_ascii=False, indent=2)
print("Detalle guardado en focus_diferenciados_resultado.json")
