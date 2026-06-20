"""
Genera propuesta de focus keyword único por producto para los 45 canibalizados.
Lee canibalizacion_resultado.json. Para cada producto, deriva un focus único
basado en su título (extrae el atributo diferenciador: medida, modelo, color).
NO aplica nada — solo imprime la propuesta para validación.
"""
import json
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open(r"C:\Users\dell\victtorino\canibalizacion_resultado.json", encoding="utf-8") as f:
    data = json.load(f)


# Reglas de extracción por categoría de focus
def sugerir_focus(titulo, focus_actual):
    t = titulo.lower()

    # Medidas (80x44, 100x44, 65 cm, 30 cm, 5 lts, 800ml, etc.)
    medidas = re.findall(r"(\d{2,3}\s*x\s*\d{2,3}|\d{1,4}\s*(?:ml|lts?|l|cm|mm|metros)|\d+\s*1?/\d|\d+\s*piezas?)", t)
    medida = medidas[0].replace(" ", "") if medidas else ""

    # Modelo (palabras tipo Colomba, Domenica, Notte, Modern, Taumm, Schwartz, Modern, Hannover, Leonardo, Neue)
    modelos = []
    for m in ["colomba", "domenica", "notte", "modern", "taumm", "täumm", "schwartz",
              "hannover", "leonardo", "neue", "freiburg", "fuscher", "domenica"]:
        if m in t:
            modelos.append(m)
    modelo = modelos[0] if modelos else ""

    # Color/material distintivo
    colores = []
    for c in ["negro", "blanco", "plateado", "cromado", "cepillado", "inox",
              "bronce", "acrílico", "acrilico", "vidrio"]:
        if c in t:
            colores.append(c)
    color = colores[0] if colores else ""

    # Atributo funcional clave
    atributos = []
    for a in ["temporizad", "monomando", "sin brazo", "esquinera", "pedestal",
              "deslizable", "interfoliada", "industrial", "cuadrad", "redondo",
              "ducha", "lavatorio", "lavamanos", "lavaplato", "urinario",
              "tina", "receptaculo", "esquinero", "doble cara", "aumento",
              "ducha higi", "carga", "descarga", "fijacion", "pulsador",
              "papel toalla", "papel higi", "jabón", "jabon", "alcohol"]:
        if a in t:
            atributos.append(a.replace("temporizad", "temporizada")
                              .replace("cuadrad", "cuadrado")
                              .replace("ducha higi", "ducha higiénica")
                              .replace("papel higi", "papel higiénico")
                              .replace("jabon", "jabón")
                              .replace("fijacion", "fijaciones"))

    # Construcción del focus según el actual
    if "llave grifería" in focus_actual or focus_actual == "llave grifería":
        # Diferenciar por tipo de llave
        if "monomando" in atributos and "lavatorio" in atributos:
            return "llave monomando lavatorio " + (modelo or color or "").strip()
        if "monomando" in atributos and "lavamanos" in atributos:
            return "llave monomando lavamanos " + (modelo or color or "").strip()
        if "temporizada" in atributos and "urinario" in atributos:
            return "llave temporizada urinario"
        if "temporizada" in atributos and ("lavatorio" in atributos or "lavamanos" in atributos):
            return "llave temporizada lavatorio"
        if "lavacopas" in t:
            return "llave lavacopas " + (color or modelo or "").strip()
        if "flexible agua" in t or "flexible de agua" in t:
            return "flexible agua " + (medida or "").strip()
        if "mezcladora" in t:
            return "mezcladora baño " + (modelo or color or "").strip()
        if "doble" in t and "lavadora" in t:
            return "llave doble lavadora"
        if "monomando" in atributos and "lavaplato" in atributos:
            return "llave monomando lavaplato " + (color or modelo or "").strip()
        # genérico con modelo
        if modelo:
            return f"llave {modelo}".strip()
        return ("llave " + " ".join(atributos[:2])).strip()

    if focus_actual == "lavaplatos cocina":
        # diferenciar por medida + secador + modelo + pack
        secador = "izquierdo" if "izquierdo" in t else ("derecho" if "derecho" in t else "")
        es_pack = "pack" in t
        prefix = "pack lavaplatos" if es_pack else "lavaplatos"
        partes = [prefix, medida, secador, modelo]
        return " ".join(p for p in partes if p).strip()

    if focus_actual == "agarradera baño":
        # diferenciar por forma + medida
        if "esquinera" in t:
            return "agarradera esquinera baño"
        if "curva" in t:
            return f"agarradera curva {medida}".strip()
        if "recta" in t:
            return f"barra seguridad recta {medida}".strip()
        return f"barra seguridad {medida}".strip() or "barra seguridad baño"

    if focus_actual == "sifón desagüe":
        # diferenciar por tipo (codo, botella, tina, lavatorio) + medida
        if "tina" in t or "receptaculo" in t or "receptáculo" in t:
            return f"sifón tina receptáculo {medida}".strip()
        if "botella" in t:
            return f"sifón botella {medida}".strip()
        if "codo" in t:
            return f"sifón codo {medida}".strip()
        if "lavatorio" in t or "lavamanos" in t:
            return f"sifón lavatorio {medida}".strip()
        if "accesorios" in t:
            return "accesorios desagüe lavatorio"
        return f"sifón desagüe {medida}".strip()

    if focus_actual == "dispensador papel higiénico":
        # diferenciar por tipo (acrílico, acero, color)
        if "toalla" in t:
            return "dispensador papel toalla interfoliada"
        if "industrial" in t or "216" in t:
            return "rollos papel higiénico industrial"
        if "azul" in t or "acrilico" in t or "acrílico" in t:
            return f"dispensador papel higiénico acrílico"
        if "acero" in t:
            return "dispensador papel higiénico acero inoxidable"
        return "dispensador papel higiénico " + (color or "").strip()

    if focus_actual == "dispensador de jabón":
        # diferenciar por medida + modelo
        if "schwartz" in t or "schwarz" in t or "negro" in t:
            return "dispensador jabón negro schwartz"
        if "taumm" in t or "täumm" in t:
            return f"dispensador jabón täumm {medida}".strip()
        return f"dispensador jabón acero inoxidable {medida}".strip()

    if focus_actual == "accesorios baño":
        # estos son cosas distintas mal agrupadas
        if "brazo" in t and "ducha" in t:
            return f"brazo ducha al muro {medida}".strip()
        if "plato ducha" in t or "plato de ducha" in t:
            return f"plato ducha {medida}".strip()
        return "accesorios para baño"

    if focus_actual == "basurero pedal baño":
        return f"basurero pedal {medida}".strip()

    if focus_actual == "espejo doble cara aumento":
        if "pedestal" in t:
            return "espejo doble cara aumento pedestal"
        if "muro" in t:
            return "espejo doble cara aumento muro"
        return "espejo doble cara aumento"

    return focus_actual  # fallback


# Procesar
print("=" * 100)
print("PROPUESTA DE FOCUS KEYWORDS DIFERENCIADOS")
print("=" * 100)
propuestas = []
for grupo in data["focus_keyword_duplicados"]:
    fk_actual = grupo["focus"]
    print(f"\n### Focus actual: \"{fk_actual}\" ({grupo['count']} productos)")
    print(f"{'ID':6} {'NUEVO FOCUS':45} TÍTULO")
    print("-" * 110)
    for p in grupo["productos"]:
        nuevo = sugerir_focus(p["name"], fk_actual)
        nuevo = re.sub(r"\s+", " ", nuevo).strip()
        propuestas.append({"id": p["id"], "titulo": p["name"], "focus_viejo": fk_actual, "focus_nuevo": nuevo})
        print(f"{p['id']:6} {nuevo[:45]:45} {p['name'][:55]}")

# Detectar si quedan focus duplicados después de la propuesta
print("\n" + "=" * 100)
print("VERIFICACIÓN — ¿quedan focus duplicados tras la propuesta?")
print("=" * 100)
from collections import Counter
focus_count = Counter(p["focus_nuevo"] for p in propuestas)
dupes_post = {k: v for k, v in focus_count.items() if v > 1}
if dupes_post:
    print(f"⚠️  Quedan {len(dupes_post)} focus aún duplicados tras la propuesta:")
    for fk, n in dupes_post.items():
        print(f"   \"{fk}\" -> {n} productos")
        for p in propuestas:
            if p["focus_nuevo"] == fk:
                print(f"     {p['id']:5}  {p['titulo'][:60]}")
else:
    print("✅ Todos los 45 productos quedan con focus único.")

# Guardar
with open(r"C:\Users\dell\victtorino\propuesta_focus_diferenciados.json", "w", encoding="utf-8") as f:
    json.dump(propuestas, f, ensure_ascii=False, indent=2)
print(f"\nPropuesta guardada en propuesta_focus_diferenciados.json")
