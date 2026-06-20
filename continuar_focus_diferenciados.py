"""Reaplica focus único a los 21 productos que faltaron por el crash."""
import sys, io, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

PENDIENTES = [
    (2828, "lavaplatos sobreponer 80x50"),
    (2793, "lavaplatos simple 80x44 derecho"),
    (2968, "dispensador jabón acero inoxidable 800ml"),
    (2852, "dispensador jabón acero inoxidable 500ml"),
    (2816, "dispensador jabón täumm 500ml"),
    (2551, "dispensador jabón negro schwartz"),
    (2926, "papel higiénico industrial 216 metros"),
    (2865, "dispensador papel toalla interfoliada"),
    (2824, "dispensador papel higiénico acero inoxidable"),
    (2739, "dispensador papel higiénico acrílico"),
    (2914, "sifón codo 90"),
    (2896, "sifón botella 1 1/4"),
    (2892, "sifón codo 1 1/4 lavatorio"),
    (2857, "sifón desagüe 1 1/2"),
    (2844, "accesorios desagüe lavatorio"),
    (2834, "sifón tina receptáculo 1 1/2"),
    (2634, "basurero pedal 12 litros"),
    (2620, "basurero pedal 5 litros gris"),
    (2615, "basurero pedal 5 litros plateado"),
    (2611, "espejo doble cara aumento muro"),
    (2590, "espejo doble cara aumento pedestal"),
]


def mt(focus):
    t = f"{focus.title()} | Victtorino"
    if len(t) > 60:
        max_n = 60 - len(" | Victtorino")
        t = f"{focus.title()[:max_n].rstrip()} | Victtorino"
    return t


def md(focus):
    return (f"{focus.capitalize()}. Calidad Victtorino, diseño moderno y "
            "materiales resistentes. Despacho a todo Chile.")[:155]


def safe_put(pid, body):
    """PUT robusto: maneja respuestas no-JSON (503, HTML) con reintento."""
    for n in range(1, 6):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/products/{pid}",
                             json=body, params=P, timeout=120)
            if r.status_code == 503:
                espera = 10 * n
                print(f"    503 (intento {n}/5), espero {espera}s")
                time.sleep(espera)
                continue
            if r.status_code >= 400:
                print(f"    HTTP {r.status_code}: {r.text[:200]}")
                return None
            # Verificar si la respuesta es JSON válido
            try:
                return r.json()
            except Exception:
                print(f"    respuesta no-JSON (intento {n}/5), reintento")
                time.sleep(5 * n)
                continue
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"    {type(e).__name__} (intento {n}/5)")
            time.sleep(5 * n)
    return None


print(f"Continuando focus para {len(PENDIENTES)} productos pendientes...\n")
ok = 0
fallidos = []
for pid, focus in PENDIENTES:
    body = {
        "meta_data": [
            {"key": "rank_math_title", "value": mt(focus)},
            {"key": "rank_math_description", "value": md(focus)},
            {"key": "rank_math_focus_keyword", "value": focus},
        ],
    }
    res = safe_put(pid, body)
    if res:
        fk = next((m["value"] for m in res.get("meta_data", [])
                   if m["key"] == "rank_math_focus_keyword"), "")
        print(f"  {pid}  -> \"{fk}\"")
        ok += 1
    else:
        print(f"  {pid}  FALLO")
        fallidos.append(pid)
    time.sleep(1.5)

print(f"\n{ok}/{len(PENDIENTES)} aplicados, {len(fallidos)} fallidos")
if fallidos:
    print(f"fallidos: {fallidos}")
