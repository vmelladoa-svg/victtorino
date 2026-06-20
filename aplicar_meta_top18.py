"""Aplica títulos optimizados con CTR boosters a los 18 productos top."""
import sys, io, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

PROPUESTAS = [
    (1814, "Sifón Desagüe Ducha 90mm Original [Top Ventas] | Victtorino"),
    (2734, "Desagüe Lavaplatos 3 1/2 con Rebalse [Inox] | Victtorino"),
    (3152, "Lavaplatos Empotrado 80x44 Izquierdo Inox | Victtorino"),
    (1582, "Ducha Fija Muro Difusor Cromado [Best Seller] | Victtorino"),
    (2615, "Basurero Pedal 5L Acero Inox [Cierre Suave] | Victtorino"),
    (946, "Plato Ducha 25cm Schwartz Negro [Premium] | Victtorino"),
    (2963, "Lavaplatos 80x44 Inox Derecho [Pack Disponible] | Victtorino"),
    (1261, "Lavaplatos Empotrado 100x44 Izquierdo Inox | Victtorino"),
    (3163, "Llave Doble Lavadora 2 Salidas Bronce | Victtorino"),
    (1235, "Llave Temporizada Baño Muro [Ahorro 60%] | Victtorino"),
    (3009, "Barra Ducha Deslizable 65cm Inox [Familia] | Victtorino"),
    (2578, "Llave Temporizada Urinario [Ahorro Agua] | Victtorino"),
    (3173, "Lavaplatos Empotrado 100x44 Derecho Inox | Victtorino"),
    (3117, "Llave Monomando Lavatorio Modern [Premium] | Victtorino"),
    (2739, "Dispensador Papel Higiénico [Industrial] | Victtorino"),
    (2783, "Brazo Ducha al Muro 30cm Inox Flexible | Victtorino"),
    (3084, "Dispensador Jabón Pared 500ml Täumm [Inox] | Victtorino"),
    (2607, "Agarradera Baño 135° con Jabonera [Seguridad] | Victtorino"),
]

# Verificar longitudes
print("Verificación longitudes (máx 60):")
ok_count = 0
for pid, mt in PROPUESTAS:
    flag = "✅" if len(mt) <= 60 else "❌"
    print(f"  {pid} ({len(mt)}) {flag}  {mt}")
    if len(mt) <= 60:
        ok_count += 1
print(f"\n{ok_count}/{len(PROPUESTAS)} dentro de límite\n")
if ok_count < len(PROPUESTAS):
    print("ABORTO: algunos exceden 60 chars.")
    sys.exit(1)


def safe_put(pid, body):
    for n in range(1, 5):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/products/{pid}", json=body, params=P, timeout=120)
            if r.status_code == 503:
                time.sleep(10 * n); continue
            if r.status_code >= 400:
                return None
            try:
                return r.json()
            except Exception:
                time.sleep(5 * n); continue
        except Exception:
            time.sleep(5 * n)
    return None


# Aplicar: solo cambiar rank_math_title (mantener description y focus keyword)
print("Aplicando títulos optimizados...\n")
ok = 0
for pid, mt in PROPUESTAS:
    # Leer meta actual para preservar description y focus
    r = requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30).json()
    meta_actual = {m["key"]: m["value"] for m in r.get("meta_data", []) if "rank_math" in m["key"]}
    # Build meta_data manteniendo description y focus_keyword
    nuevo_meta = [
        {"key": "rank_math_title", "value": mt},
        {"key": "rank_math_description", "value": meta_actual.get("rank_math_description", "")},
        {"key": "rank_math_focus_keyword", "value": meta_actual.get("rank_math_focus_keyword", "")},
    ]
    res = safe_put(pid, {"meta_data": nuevo_meta})
    if res:
        new_mt = next((m["value"] for m in res.get("meta_data", []) if m["key"] == "rank_math_title"), "")
        print(f"  {pid} ({len(new_mt):2})  {new_mt}")
        ok += 1
    else:
        print(f"  {pid} FALLO")
    time.sleep(1.2)

print(f"\n{ok}/{len(PROPUESTAS)} títulos optimizados aplicados")
