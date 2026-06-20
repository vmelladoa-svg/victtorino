# Convención de UTMs — Victtorino

Estándar único para que GA4 (`G-HNMY9BH35K`) atribuya tráfico de forma limpia y consistente
entre Meta, Google y MercadoLibre. **Regla de oro: todo en minúsculas, sin tildes, sin espacios
(usar guiones).** Un UTM mal escrito crea una fuente nueva en GA4 y ensucia la atribución.

## Parámetros

| Parámetro | Qué es | Valores permitidos |
|---|---|---|
| `utm_source` | De dónde viene | `facebook`, `instagram`, `google`, `mercadolibre`, `email`, `whatsapp`, `bing` |
| `utm_medium` | Tipo de canal | `cpc` (pago búsqueda), `paid-social` (pago social), `social` (orgánico), `email`, `referral` |
| `utm_campaign` | Campaña | nombre-corto-en-guiones, ej: `cyber-griferia-cocina`, `remarketing-carrito` |
| `utm_content` | Variante de anuncio/creativo | ej: `video-15s`, `carrusel-cocina`, `static-azul` |
| `utm_term` | Palabra clave (solo Google búsqueda) | la keyword o `{keyword}` dinámica |

## Reglas por plataforma

### Google Ads
- **NO poner UTMs manuales en Search.** Activar **auto-tagging (`gclid`)** en Google Ads → Configuración → Seguimiento. Esto alimenta GA4 automáticamente y es más preciso.
- Confirmar que GA4 y Google Ads estén **vinculados** (hoy `adsLinked: false` en Site Kit → falta vincular).
- Solo usar UTMs manuales si auto-tagging está desactivado.

### Meta Ads (Facebook / Instagram)
Meta NO auto-taggea. En cada anuncio, campo **"Parámetros de URL"**, pegar (con macros dinámicas de Meta):
```
utm_source=facebook&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```
(usar `instagram` como source si la colocación es solo IG). Las `{{...}}` las rellena Meta solo.

### MercadoLibre / otros
- Enlaces salientes a la web desde ML o campañas externas:
  `?utm_source=mercadolibre&utm_medium=referral&utm_campaign=ficha-producto`

## Ejemplos completos
```
https://victtorino.cl/tienda/?utm_source=facebook&utm_medium=paid-social&utm_campaign=remarketing-carrito&utm_content=video-15s
https://victtorino.cl/producto/grifo-monomando/?utm_source=email&utm_medium=email&utm_campaign=newsletter-junio
```

## Checklist de verificación
- [ ] Auto-tagging (`gclid`) activado en Google Ads
- [ ] GA4 ↔ Google Ads vinculados (hoy NO)
- [ ] Plantilla de URL de Meta aplicada en todos los anuncios activos
- [ ] En GA4 → Adquisición → Adquisición de tráfico, revisar que no aparezcan fuentes
      duplicadas por mayúsculas/tildes (ej. `Facebook` vs `facebook`)
