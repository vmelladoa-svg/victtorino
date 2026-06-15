# Banners promocionales — Victtorino

Plantillas HTML/CSS profesionales para promocionar productos en redes sociales.
Estilo **minimalista premium**, formato **Historia / Reel (9:16, 1080×1920 px)** —
ideal para Instagram Stories, TikTok y Reels.

## Archivos

| Archivo | Producto |
|---|---|
| `cocina-cromo.html`    | Mezcladora de cocina monomando cromo (fondo claro premium) |
| `bano-negro-mate.html` | Mezcladora de baño negro mate (fondo oscuro + dorado)      |

## Cómo usar

### 1. Vista previa
Abre cualquiera de los `.html` en tu navegador (doble clic). Se escala solo a tu
pantalla, pero internamente mide los 1080×1920 px reales.

### 2. Pon la foto de tu producto
1. Guarda la foto en la carpeta `img/` (lo mejor: **PNG con fondo transparente**).
2. En el HTML, busca el bloque `<div class="placeholder">…</div>` y reemplázalo por:
   ```html
   <img src="img/cocina-cromo.png" alt="Mezcladora">
   ```

### 3. Edita textos
Cambia libremente en el HTML: el `badge` (etiqueta superior), el `titulo`,
el `subtitulo`, el `cta` (llamado a la acción) y la `web`.

### 4. Exportar como imagen (1080×1920)
**Opción A — Captura del navegador (Chrome):**
1. Abre el HTML y pulsa `F12` (DevTools).
2. `Ctrl/Cmd + Shift + P` → escribe **"Capture node screenshot"**.
3. Selecciona el elemento `<div class="banner">` y captura. Sale el PNG exacto.

**Opción B — Modo dispositivo:**
DevTools → icono de móvil → tamaño personalizado `1080 × 1920` → captura de pantalla.

## Personalización rápida (marca)
Los colores están en `:root { … }` al inicio de cada archivo. Cambia ahí la
paleta para ajustarla a tu identidad de marca.
