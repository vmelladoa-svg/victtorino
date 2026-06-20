# -*- coding: utf-8 -*-
"""Indice maestro de fichas tecnicas Taumm desde los PDF de catalogo.
Captura TODOS los codigos de producto (9 caracteres, formato familia+codigo),
la descripcion/dimension adyacente y la seccion/familia."""
import os, re, subprocess, csv, json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

FAMILIAS = {
    "01": "Monomandos", "02": "Accesorios para Ducha", "03": "Accesorios para Bano",
    "04": "Griferia General", "05": "Flexibles Agua y Gas", "06": "Valvulas",
    "07": "Llaves", "08": "Fitting Bronce", "10": "Griferia Temporizada",
    "11": "Fitting de Laton", "12": "Piezas para Sanitarias", "13": "Repuestos",
    "14_15": "Shower Doors, Espejos y Bowls", "16": "Griferia Electronica",
    "17": "Teflones", "18": "Tinas y sus Accesorios", "19": "Lavaplatos y Accesorios",
    "21": "Accesorios WC",
}

# codigo = 9 chars: empieza con 2 digitos (familia), resto alfanumerico, >=6 digitos
CODE_RE = re.compile(r"\b\d{2}[0-9A-Z]{7}\b")
def is_code(tok):
    return len(tok) == 9 and tok[:2].isdigit() and sum(c.isdigit() for c in tok) >= 6

def pdf_files():
    out = []
    for fn in sorted(os.listdir(HERE)):
        if fn.lower().endswith(".pdf"):
            m = re.match(r"^(\d+(?:_\d+)?)_", fn)
            if m:
                out.append((m.group(1), fn))
    return out

def layout_text(pdf_path):
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", pdf_path, "-"],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def clean(s):
    return re.sub(r"\s+", " ", s).strip(" .,-\t")

rows = []
for code_key, fn in pdf_files():
    fam = FAMILIAS.get(code_key, code_key)
    text = layout_text(os.path.join(HERE, fn))
    seccion = ""
    for raw in text.splitlines():
        line = raw.rstrip()
        matches = [m for m in CODE_RE.finditer(line) if is_code(m.group())]
        if not matches:
            # posible encabezado de seccion: tiene letras, pocos digitos, no es pie
            letters = sum(c.isalpha() for c in line)
            digits = sum(c.isdigit() for c in line)
            s = clean(line)
            if letters >= 4 and digits <= 3 and 0 < len(s) <= 60 \
               and not s.lower().startswith(("unidades", "largo", "alto", "ancho", "despeje", "material", "medidas")):
                seccion = s
            continue
        # dividir la linea por posicion de cada codigo -> descripcion entre codigos
        for idx, m in enumerate(matches):
            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(line)
            desc = clean(line[start:end])
            rows.append({
                "codigo": m.group(),
                "familia": fam,
                "seccion": seccion,
                "descripcion": desc,
                "pdf": fn,
            })

# dedupe por codigo, combinando descripcion/seccion no vacias
agg = {}
for r in rows:
    c = r["codigo"]
    if c not in agg:
        agg[c] = {"codigo": c, "familia": r["familia"], "seccion": r["seccion"],
                  "descripcion": r["descripcion"], "pdf": r["pdf"],
                  "familias": {r["familia"]}}
    else:
        a = agg[c]
        a["familias"].add(r["familia"])
        if not a["descripcion"] and r["descripcion"]:
            a["descripcion"] = r["descripcion"]
        if not a["seccion"] and r["seccion"]:
            a["seccion"] = r["seccion"]

final = []
for c, a in agg.items():
    a["familias_todas"] = "; ".join(sorted(a.pop("familias")))
    final.append(a)
final.sort(key=lambda x: x["codigo"])

csv_path = os.path.join(HERE, "indice_fichas_taumm.csv")
cols = ["codigo", "familia", "seccion", "descripcion", "pdf", "familias_todas"]
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in final:
        w.writerow({k: r.get(k, "") for k in cols})

with open(os.path.join(HERE, "indice_fichas_taumm.json"), "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f"Codigos unicos: {len(final)}")
print(f"Apariciones totales: {len(rows)}")
cnt = Counter(r["familia"] for r in rows)
print("\nApariciones por familia:")
for fam, n in sorted(cnt.items(), key=lambda x: -x[1]):
    print(f"  {n:4d}  {fam}")
con_desc = sum(1 for r in final if r["descripcion"])
print(f"\nCon descripcion/dimension: {con_desc}/{len(final)}")
print(f"CSV: {csv_path}")
