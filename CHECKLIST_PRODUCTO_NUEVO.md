# Checklist — Producto Nuevo (orden de publicación)

> Regla base: **la web/Defontana es la fuente de la verdad del contenido; los marketplaces son el canal de venta.**
> La mejor versión de fotos y descripción vive siempre en la web y desde ahí baja al resto.
> No dejes pasar más de 1 día entre publicar en la web y replicar a ML/otros canales.

---

## 0. Antes de empezar (datos mínimos)
- [ ] SKU definitivo (formato Defontana, ej. `020101005-T`)
- [ ] Precio de venta + costo (para validar margen)
- [ ] Stock real disponible
- [ ] Categoría a la que pertenece
- [ ] Fotos en buena calidad (mínimo 4, idealmente fondo blanco + 1 de uso/ambiente)

## 1. Cargar en Defontana (maestro)
- [ ] Crear ficha con SKU, precio, costo, stock, categoría
- [ ] Verificar que el SKU no esté duplicado

## 2. Publicar en la WEB (victtorino.cl) — PRIMERO
- [ ] Título claro con palabra clave al inicio
- [ ] **Fotos buenas** (esta es la versión maestra que se replica)
- [ ] Descripción completa
- [ ] SEO: meta título + meta descripción + URL canónica `/categoria-producto/`
- [ ] Atributos/ficha técnica si aplica
- [ ] Categoría correcta asignada
- [ ] Publicar y revisar que se vea bien (ojo: cache LiteSpeed puede demorar)

## 3. Replicar a MARKETPLACES (mismo día) — vía Defontana
- [ ] **MercadoLibre** (C1 / C2 / C3 según corresponda)
  - [ ] Categoría ML correcta + atributos obligatorios (`family_name`, etc.)
  - [ ] Fotos = las mismas de la web
  - [ ] Revisar que no canibalice otra publicación propia
- [ ] **Walmart**
- [ ] **Paris**
- [ ] **Falabella**

## 4. Excepción — producto urgente/estacional
Si es un ofertón o stock que hay que liquidar rápido:
- [ ] Publicar **primero en ML** (la venta manda), web después el mismo día/siguiente.

## 5. Verificación final
- [ ] El producto aparece con fotos en TODOS los canales activados
- [ ] Precio y stock consistentes en todos lados
- [ ] Sin publicaciones duplicadas/canibalizando

---

## Herramientas de apoyo en este repo
- `fotos_ml_a_web.py` — copia fotos de ML a la web para productos web sin foto
  (`python fotos_ml_a_web.py` para ver el plan; `--apply-seguros` o `--apply <ids>` para aplicar).
- `importar_ml_a_woo.py` — importa un anuncio ML completo a la web como producto draft.
- Snapshots ML: `data/auditoria/snapshot_c{1,2,3}.json` — **regenerar antes** de cruzar si
  agregaste publicaciones ML nuevas (los actuales son del 2026-05-23).
