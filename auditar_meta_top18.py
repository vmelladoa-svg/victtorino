"""Audita meta title y meta description de los 18 productos top vendidos ML."""
import sys, io, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

# 18 productos top ML
IDS_TOP18 = [
    (1814, "Sifón Desagüe Ducha 90mm Receptáculo", "sifón desagüe ducha", 179),
    (2734, "Desagüe Lavaplatos 3 1/2 con Rebalse", "desagüe lavaplatos", 86),
    (3152, "Lavaplatos Empotrado 80x44 Izquierdo", "lavaplatos empotrado 80x44", 77),
    (1582, "Ducha Fija Difusor Muro", "ducha fija al muro", 137),  # 73+64
    (2615, "Basurero Pedal 5L Acero Inox", "basurero pedal baño", 71),
    (946, "Plato Ducha Cuadrado 25cm Schwartz Negro", "plato de ducha schwartz negro", 67),
    (2963, "Lavaplatos 80x44 Inox Secador Derecho", "lavaplatos 80x44 inoxidable", 66),
    (1261, "Lavaplatos Empotrado 100x44 Izquierdo", "lavaplatos empotrado 100x44", 66),
    (3163, "Llave Doble Lavadora Jardín 2 Salidas", "llave doble lavadora", 65),
    (1235, "Llave Lavatorio Temporizada Muro Larga", "llave temporizada baño", 50),
    (3009, "Barra Soporte Ducha Deslizable 65cm", "barra ducha deslizable", 49),
    (2578, "Llave Temporizada Urinario", "llave temporizada urinario", 41),
    (3173, "Lavaplatos Empotrado 100x44 Derecho", "lavaplatos empotrado 100x44 derecho", 36),
    (3117, "Llave Monomando Lavatorio Modern", "llave monomando lavatorio", 34),
    (2739, "Dispensador Papel Higiénico Acrílico", "dispensador papel higiénico", 31),
    (2783, "Brazo Plato Ducha 30cm Entrada Flexible", "brazo de ducha al muro", 30),
    (3084, "Dispensador Jabón Manual Täumm Pared", "dispensador jabón pared", 30),
    (2607, "Agarradera 135° con Jabonera", "agarradera baño con jabonera", 27),
]

print(f"Auditando meta de {len(IDS_TOP18)} productos top vendidos...\n")
print(f"{'ID':5} {'Ventas':>6}  {'MT chars':>8} {'MD chars':>8}  Meta Title (actual)")
print("-" * 110)

resultados = []
for pid, name_corto, focus, ventas in IDS_TOP18:
    r = requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30).json()
    meta = {m["key"]: m["value"] for m in r.get("meta_data", []) if "rank_math" in m["key"]}
    mt = meta.get("rank_math_title", "")
    md = meta.get("rank_math_description", "")
    actual_focus = meta.get("rank_math_focus_keyword", "")

    # Análisis
    mt_len = len(mt)
    md_len = len(md)
    issues = []
    if mt_len > 60:
        issues.append("MT_LARGO")
    if mt_len < 30:
        issues.append("MT_CORTO")
    if md_len > 155:
        issues.append("MD_LARGO")
    if md_len < 120:
        issues.append("MD_CORTO")
    # CTR boosters: detectar si tiene número, brackets, año
    tiene_numero = any(c.isdigit() for c in mt)
    tiene_bracket = "(" in mt or "[" in mt
    tiene_año = "2026" in mt or "2025" in mt
    if not tiene_numero:
        issues.append("sin_numero")
    if not tiene_bracket:
        issues.append("sin_bracket")
    # Power words
    power_words = ["nuevo", "premium", "profesional", "completo", "ideal", "mejor",
                   "exclusivo", "garantizado", "rápida", "fácil"]
    tiene_power = any(p in mt.lower() for p in power_words)

    print(f"{pid:5}  {ventas:>5}   {mt_len:>8} {md_len:>8}  {mt[:55]}")
    resultados.append({
        "id": pid, "name": name_corto, "focus": focus, "ventas": ventas,
        "mt": mt, "md": md, "mt_len": mt_len, "md_len": md_len,
        "tiene_numero": tiene_numero, "tiene_bracket": tiene_bracket,
        "tiene_año": tiene_año, "tiene_power": tiene_power, "issues": issues,
    })

# Resumen
print()
print(f"{'='*100}")
print("RESUMEN")
print(f"{'='*100}")
total = len(resultados)
print(f"Productos analizados: {total}")
print(f"  Title 50-60 chars (ideal): {sum(1 for r in resultados if 50<=r['mt_len']<=60)}")
print(f"  Title <30 (muy corto):     {sum(1 for r in resultados if r['mt_len']<30)}")
print(f"  Title >60 (truncado):      {sum(1 for r in resultados if r['mt_len']>60)}")
print(f"  Description 120-155 chars: {sum(1 for r in resultados if 120<=r['md_len']<=155)}")
print(f"  Description <120 (corta):  {sum(1 for r in resultados if r['md_len']<120)}")
print(f"  Description >155 (larga):  {sum(1 for r in resultados if r['md_len']>155)}")
print()
print(f"CTR boosters:")
print(f"  Con número en title:        {sum(1 for r in resultados if r['tiene_numero'])}/{total}")
print(f"  Con bracket/paréntesis:     {sum(1 for r in resultados if r['tiene_bracket'])}/{total}")
print(f"  Con año (2026):             {sum(1 for r in resultados if r['tiene_año'])}/{total}")
print(f"  Con power word:             {sum(1 for r in resultados if r['tiene_power'])}/{total}")

with open(r"C:\Users\dell\victtorino\meta_audit_top18.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
print(f"\nDetalle en meta_audit_top18.json")
