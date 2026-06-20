import requests
import json
import time
from pathlib import Path

TOKENS_FILE = Path(__file__).parent / "tokens_cuenta3.json"
BASE_URL = "https://api.mercadolibre.com"


def load_access_token():
    return json.loads(TOKENS_FILE.read_text())["access_token"]


def get_headers():
    return {"Authorization": f"Bearer {load_access_token()}"}


def tiene_descripcion(item_id):
    r = requests.get(f"{BASE_URL}/items/{item_id}/description", headers=get_headers())
    if r.ok:
        texto = r.json().get("plain_text", "").strip()
        return len(texto) > 30
    return False


def analizar_item(item, con_descripcion):
    problemas = []

    fotos = len(item.get("pictures", []))
    atributos = item.get("attributes", [])
    titulo = item.get("title", "")
    health = item.get("health", 0)
    listing_type = item.get("listing_type_id", "")
    video = item.get("video_id")
    warranty = item.get("warranty", "")

    if fotos < 4:
        problemas.append(f"Pocas fotos ({fotos}/8 recomendadas)")
    elif fotos < 8:
        problemas.append(f"Fotos insuficientes ({fotos}/8 recomendadas)")

    if not con_descripcion:
        problemas.append("Sin descripcion")

    vacios = [a["name"] for a in atributos if not a.get("value_name")]
    if vacios:
        problemas.append(f"Atributos sin completar ({len(vacios)}): {', '.join(vacios[:4])}")

    if len(titulo) < 40:
        problemas.append(f"Titulo corto ({len(titulo)} caracteres, minimo 40)")

    if not video:
        problemas.append("Sin video")

    if listing_type != "gold_pro":
        problemas.append(f"Tipo de publicacion: {listing_type} (recomendado: gold_pro)")

    if not warranty or len(warranty.strip()) < 5:
        problemas.append("Sin garantia declarada")

    return problemas


def score_label(score):
    if score is None:
        return "Sin datos"
    if score >= 0.8:
        return "Buena"
    if score >= 0.5:
        return "Regular"
    return "Critica"


def main():
    activas_file = Path(__file__).parent / "publicaciones_activas.json"
    if not activas_file.exists():
        print("Ejecuta mis_publicaciones.py primero.")
        return

    items = json.loads(activas_file.read_bytes().decode("latin-1"))
    total = len(items)
    print(f"\nAnalizando calidad de {total} publicaciones activas...\n")

    resultados = []

    for i, item in enumerate(items, 1):
        print(f"  [{i}/{total}] {item['id']}", end="\r")
        con_desc = tiene_descripcion(item["id"])
        problemas = analizar_item(item, con_desc)

        resultados.append({
            "id": item["id"],
            "titulo": item["title"],
            "precio": item.get("price", 0),
            "stock": item.get("available_quantity", 0),
            "vendidos": item.get("sold_quantity", 0),
            "health": item.get("health", 0),
            "score_label": score_label(item.get("health", 0)),
            "fotos": len(item.get("pictures", [])),
            "listing_type": item.get("listing_type_id", ""),
            "con_descripcion": con_desc,
            "problemas": problemas,
        })
        time.sleep(0.15)

    resultados.sort(key=lambda x: x["health"] if x["health"] is not None else -1)

    output = Path(__file__).parent / "calidad_fichas.json"
    output.write_text(json.dumps(resultados, indent=2, ensure_ascii=False))

    criticas  = [r for r in resultados if r["health"] is not None and r["health"] < 0.5]
    regulares = [r for r in resultados if r["health"] is not None and 0.5 <= r["health"] < 0.8]
    buenas    = [r for r in resultados if r["health"] is not None and r["health"] >= 0.8]

    print(f"\n{'='*70}")
    print(f"  RESUMEN DE CALIDAD DE FICHAS ({total} publicaciones activas)")
    print(f"{'='*70}")
    print(f"  Criticas  (< 50%): {len(criticas)}")
    print(f"  Regulares (50-79%): {len(regulares)}")
    print(f"  Buenas    (>= 80%): {len(buenas)}")
    print(f"{'='*70}\n")

    print(f"  LAS 20 FICHAS MAS DEBILES:\n")
    for r in resultados[:20]:
        pct = int((r["health"] or 0) * 100)
        print(f"  Health: {pct}% [{r['score_label']}]  Fotos: {r['fotos']}  Stock: {r['stock']}  Vendidos: {r['vendidos']}")
        print(f"  {r['titulo']}")
        print(f"  ID: {r['id']}  |  Precio: ${r['precio']:,.0f} CLP  |  {r['listing_type']}")
        for p in r["problemas"]:
            print(f"    ! {p}")
        print()

    print(f"Detalle completo guardado en: {output}")


if __name__ == "__main__":
    main()
