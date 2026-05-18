import pandas as pd
from pathlib import Path
from config import DATA_DIR


def _is_html_file(path: Path) -> bool:
    """Detecta si un archivo es en realidad HTML (como exporta Defontana)."""
    try:
        with open(path, "rb") as f:
            header = f.read(16)
        return header.lstrip().startswith(b"<")
    except Exception:
        return False


def _load_defontana_ventas(path: Path) -> dict[str, pd.DataFrame]:
    """
    Carga el informe de ventas exportado desde Defontana.
    Defontana exporta archivos .xls/.xlsx que son en realidad HTML.
    Retorna un dict con una hoja 'Ventas' ya limpia.
    """
    tables = pd.read_html(str(path), encoding="iso-8859-1")
    if len(tables) < 2:
        return {}

    df = tables[1].copy()

    # La fila 0 tiene encabezados de grupo (Margen de Contribución…)
    # La fila 1 tiene los nombres reales de columna
    df.columns = df.iloc[1]
    df = df.iloc[2:].reset_index(drop=True)

    # Renombrar a nombres limpios
    df.columns = [
        "Articulo",
        "Cantidad",
        "Venta_Neta_Esperada",
        "Venta_Neta_Real",
        "Descuento",
        "Costo_Articulo",
        "Margen_Valor",
        "Margen_Pct",
        "Margen_Sobre_Costos",
    ]

    # Eliminar fila de totales y filas vacías
    df = df[df["Articulo"].notna()]
    df = df[df["Articulo"] != "Artículo"]
    df = df[~df["Articulo"].str.startswith("TOTAL", na=False)]
    df = df.reset_index(drop=True)

    # Convertir columnas numéricas
    for col in ["Cantidad", "Venta_Neta_Esperada", "Venta_Neta_Real",
                "Descuento", "Costo_Articulo", "Margen_Valor"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return {"Ventas": df}


def load_excel(filename: str) -> dict[str, pd.DataFrame]:
    """
    Carga todas las hojas de un archivo Excel en DATA_DIR.

    Maneja dos casos:
    - Archivos .xlsx reales (inventario, finanzas, etc.)
    - Archivos .xls exportados por Defontana (son HTML disfrazados)
    """
    # Buscar el archivo sin importar mayúsculas/minúsculas
    path = DATA_DIR / filename
    if not path.exists():
        # Intentar variaciones de nombre (Ventas.xls vs ventas.xlsx)
        for candidate in DATA_DIR.iterdir():
            if candidate.stem.lower() == Path(filename).stem.lower():
                path = candidate
                break
        else:
            return {}

    try:
        if _is_html_file(path):
            return _load_defontana_ventas(path)
        else:
            xl = pd.ExcelFile(path)
            return {sheet: xl.parse(sheet) for sheet in xl.sheet_names}
    except Exception as e:
        print(f"[loader] Error cargando {filename}: {e}")
        return {}


def _dedup_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas duplicadas agregando sufijo numérico (_1, _2…)."""
    from collections import Counter
    counts = Counter(str(c) for c in df.columns)
    seen: dict[str, int] = {}
    new_cols = []
    for col in df.columns:
        col = str(col)
        if counts[col] > 1:
            seen[col] = seen.get(col, 0) + 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            new_cols.append(col)
    df = df.copy()
    df.columns = new_cols
    return df


def format_data(sheets: dict[str, pd.DataFrame], max_rows: int = 60) -> str:
    """Convierte hojas de Excel a texto legible para el LLM."""
    if not sheets:
        return (
            "Sin datos cargados. "
            "Carga el archivo Excel correspondiente en data/excel/ "
            "o ejecuta: python tools/create_samples.py"
        )

    parts = []
    for name, df in sheets.items():
        if df.empty:
            continue
        df = _dedup_cols(df)
        parts.append(f"### Hoja: {name}")
        parts.append(f"Total filas: {len(df)}")
        parts.append(df.head(max_rows).to_string(index=False))

    return "\n\n".join(parts) if parts else "Archivo vacío."
