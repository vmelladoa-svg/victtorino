CREATE TABLE IF NOT EXISTS productos (
  codigo      TEXT PRIMARY KEY,
  descripcion TEXT NOT NULL,
  familia     TEXT,
  costo       INTEGER DEFAULT 0,
  activo      BOOLEAN DEFAULT TRUE,
  actualizado TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS movimientos (
  id       BIGSERIAL PRIMARY KEY,
  codigo   TEXT NOT NULL REFERENCES productos(codigo),
  tipo     TEXT NOT NULL,
  cantidad INTEGER NOT NULL,
  canal    TEXT,
  ref      TEXT,
  fecha    TIMESTAMPTZ DEFAULT now(),
  UNIQUE (canal, ref, codigo)
);

CREATE TABLE IF NOT EXISTS canal_map (
  canal       TEXT NOT NULL,
  sku_externo TEXT NOT NULL,
  codigo      TEXT NOT NULL REFERENCES productos(codigo),
  PRIMARY KEY (canal, sku_externo)
);
