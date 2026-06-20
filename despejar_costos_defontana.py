# -*- coding: utf-8 -*-
"""Aisla codigo + descripcion + costo de compra desde el Informe de Articulos de Defontana (.xls = HTML)."""
import pandas as pd
import re, io, warnings
warnings.filterwarnings('ignore')

SRC = r'C:\Users\dell\Downloads\Informe de artículos 20250627210343860887 11062026 0236.xls'
OUT_XLSX = r'C:\Users\dell\victtorino\costos_defontana_limpio.xlsx'
OUT_CSV  = r'C:\Users\dell\victtorino\costos_defontana_limpio.csv'

html = open(SRC, encoding='latin-1').read()
# La fila de encabezados reales esta en el indice 1 (la 0 es el titulo del informe)
df = pd.read_html(io.StringIO(html), header=1)[0]
df.columns = [str(c).strip() for c in df.columns]

col_art   = [c for c in df.columns if 'Art' in c and 'Descrip' in c][0]
col_costo = [c for c in df.columns if 'Costo Vigente' in c][0]
col_repo  = [c for c in df.columns if 'Reposici' in c][0]

def split_codigo(s):
    """Separa el codigo Defontana de la descripcion.
    '010102001-T-BARRA 135 JABONERA' -> ('010102001-T', 'BARRA 135 JABONERA')
    'TZ-5059-Lavamanos Marmol Blanco' -> ('TZ-5059', 'Lavamanos Marmol Blanco')
    '03012053-T-FLEXIBLE GAS HI-HI 1/2' -> ('03012053-T', 'FLEXIBLE GAS HI-HI 1/2')
    """
    s = str(s).strip()
    # codigo numerico + letra (T/C/K...), o prefijo alfabetico tipo TZ-5059
    m = re.match(r'^\s*(\d+-[A-Za-z]|[A-Za-z]{1,4}-\w+)\s*-\s*(.*)$', s)
    if m:
        return m.group(1), m.group(2).strip()
    # fallback: primer guion separa codigo del resto
    parts = s.split('-', 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else '')

def to_int(v):
    """'6,778' -> 6778 ; '0' -> 0 ; vacios -> None"""
    s = str(v).replace('\xa0', '').replace('&nbsp;', '').strip()
    s = s.replace('.', '').replace(',', '')  # quita separador de miles (formato del export)
    s = re.sub(r'[^0-9-]', '', s)
    if s in ('', '-'):
        return None
    return int(s)

rows = []
for _, r in df.iterrows():
    raw = str(r[col_art])
    # salta filas de encabezado que Defontana repite por pagina y vacios
    if 'Descrip' in raw or raw.strip().lower() in ('nan', ''):
        continue
    cod, desc = split_codigo(raw)
    if not cod or cod.lower() == 'nan':
        continue
    rows.append({
        'Codigo': cod,
        'Descripcion': desc,
        'Costo compra (CLP)': to_int(r[col_costo]),
        'Costo reposicion (CLP)': to_int(r[col_repo]),
    })

out = pd.DataFrame(rows)
out.to_excel(OUT_XLSX, index=False)
out.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')

# Diagnostico
tot = len(out)
sin_costo = out['Costo compra (CLP)'].isna().sum()
costo_cero = (out['Costo compra (CLP)'] == 0).sum()
print(f'Filas totales: {tot}')
print(f'Sin costo (vacio): {sin_costo}')
print(f'Costo = 0: {costo_cero}')
print(f'Codigos duplicados: {out["Codigo"].duplicated().sum()}')
print('\nPrimeras 5:')
print(out.head(5).to_string(index=False))
print('\nGenerado:')
print(' ', OUT_XLSX)
print(' ', OUT_CSV)
