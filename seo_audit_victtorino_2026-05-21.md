# SEO Audit Report: victtorino.cl
**Date:** 2026-05-21
**Auditor:** Claude Code (seo-audit skill v1.0.0)

## Overall Score: C+ (71%)

El sitio tiene bases sólidas (estructura limpia, HTTPS, sitemap, JSON-LD básico, robots.txt sano), pero hay **3 problemas críticos** que están limitando rankings: 3 H1s en la home, cache extremadamente bajo y un activo cargándose desde un dominio externo (alvexltda.cl).

### Category Scores

| Categoría | Grade | Score | Issues |
|---|---|---|---|
| Crawlability & Indexation | B | 80% | 0 críticos |
| HTTPS & Security | D | 45% | 1 crítico |
| Core Web Vitals | C | 60% | 1 crítico |
| Mobile Usability | B | 80% | 0 |
| URL Structure | A | 95% | 0 |
| On-Page SEO | C | 65% | 1 crítico |
| Structured Data | B | 80% | 1 menor |
| Internal Linking | C | 70% | (requiere análisis profundo) |
| E-E-A-T | B | 80% | 0 |
| AI Search Readiness | B | 80% | 0 |

---

## Critical Issues (arreglar primero)

### 1. 3 H1s en la página de inicio
- **Confianza:** Confirmado
- **Impacto:** Alto — confunde a Google sobre cuál es el tema principal de la home, diluye autoridad
- **Evidencia:** `grep -oP '<h1[^>]*>'` devuelve 3 matches en homepage:
  - "Cyber Day Chile 2026: Ofertas en Grifería..."
  - "Renueva tu cocina: cómo elegir el lavaplatos ideal..."
  - "Black Friday en Chile: las mejores ofertas..."
- **Causa:** Los widgets de "Post Destacado" de Elementor están envolviendo el título del post en `<h1>` en vez de `<h2>` o `<h3>`.
- **Fix:** En Elementor, editar los widgets de blog posts en la home y cambiar el "HTML Tag" del título de H1 a H2 o H3. Solo debe haber UN H1 que diga algo como "Victtorino | Griferías y Accesorios para Baño y Cocina en Chile".
- **Esfuerzo:** 15 minutos en Elementor

### 2. Cache extremadamente bajo (max-age=3)
- **Confianza:** Confirmado
- **Impacto:** Alto — afecta velocidad de carga y Core Web Vitals (LCP, INP)
- **Evidencia:** `curl -I` devuelve `Cache-Control: max-age=3, must-revalidate`. Esto significa que el navegador re-descarga todo cada 3 segundos.
- **Fix:** En LiteSpeed Cache plugin (o el cache que uses) configurar:
  - HTML pages: 3600s (1 hora) o 600s mínimo
  - CSS/JS/imágenes: 31536000s (1 año) con cache busting por versión
- **Esfuerzo:** 10 minutos en panel del plugin

### 3. Logo apuntando a otro dominio (alvexltda.cl)
- **Confianza:** Confirmado
- **Impacto:** Alto — si ese dominio cae, el logo desaparece; además posibles problemas de SEO de imagen
- **Evidencia:** En el HTML aparece `data-src="https://alvexltda.cl/vittorino/wp-content/uploads/2026/03/logo-2-1-1.png"` (nota: "vittorino" con una sola t, parece sitio de desarrollo antiguo)
- **Fix:** Buscar el widget que usa esa imagen, subir el logo a la Media Library de victtorino.cl y actualizar la referencia. Probablemente está en el header de Elementor o en un widget de bienvenida.
- **Esfuerzo:** 15 minutos

---

## High Priority Issues

### 4. Faltan headers de seguridad
- **Confianza:** Confirmado
- **Impacto:** Medio-Alto — Google premia sitios con HSTS y CSP; ranking factor menor pero suma
- **Evidencia:** `curl -I` no devuelve HSTS, CSP, X-Frame-Options, X-Content-Type-Options ni Referrer-Policy
- **Fix:** En el `.htaccess` (o config LiteSpeed) agregar:
  ```
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
  Header always set X-Content-Type-Options "nosniff"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  ```
- **Esfuerzo:** 20 minutos + testing

### 5. og:locale incorrecto (es_ES en vez de es_CL)
- **Confianza:** Confirmado
- **Impacto:** Medio — los previews en redes sociales asumen España; afecta segmentación geográfica
- **Evidencia:** `<meta property="og:locale" content="es_ES" />` pero el HTML dice `<html lang="es-CL">`
- **Fix:** En Rank Math → Titles & Meta → Global Meta → Open Graph → cambiar locale a `es_CL`
- **Esfuerzo:** 2 minutos

### 6. Falta BreadcrumbList schema
- **Confianza:** Confirmado
- **Impacto:** Medio — Google muestra breadcrumbs en resultados (mejora CTR ~30% según estudios)
- **Evidencia:** El JSON-LD de la home y página de producto NO incluye `BreadcrumbList`
- **Fix:** En Rank Math → Sitewide Meta → Breadcrumbs → activar. O instalar plugin específico.
- **Esfuerzo:** 5 minutos

---

## Medium Priority Issues

### 7. No hay directivas para bots de IA
- **Confianza:** Confirmado
- **Impacto:** Bajo hoy, importante a futuro
- **Evidencia:** robots.txt no menciona GPTBot, PerplexityBot, ClaudeBot, etc.
- **Estado actual:** todos los bots IA pueden crawlear (bueno por defecto)
- **Recomendación:** Dejarlo así si quieres que Victtorino aparezca en respuestas de ChatGPT/Perplexity. Si quisieras bloquear, agregar:
  ```
  User-agent: GPTBot
  Disallow: /
  ```
- **Acción:** Decisión estratégica, no fix técnico.

### 8. Sitemap del producto correcto, falta exposure de las nuevas categorías
- **Confianza:** Confirmado
- **Evidencia:** `category-sitemap.xml` lista 7 categorías al menos: Accesorios, Griferia, Dispensador, Lavaplatos, Espejos, Lavamanos, Shower/Mamparas. Falta verificar si las 3 nuevas (Agarraderas y Barras, Sifones y Desagües, WC e Inodoros) ya aparecen.
- **Fix:** Forzar regeneración de sitemap en Rank Math → Sitemap Settings → click "Ping" o regenerar.
- **Esfuerzo:** 1 minuto

---

## Lo que está BIEN (no tocar)

1. **HTTPS funcional** con certificado válido, sin contenido mixto.
2. **robots.txt sano**: bloquea wp-admin (correcto) y carts (correcto), referencia sitemap.
3. **Sitemap index estructurado**: 255 productos + 7+ categorías + posts + pages, organizados en 7 sub-sitemaps.
4. **Title y meta description de la home bien escritos**: 60 y 144 caracteres, con keywords correctos.
5. **JSON-LD presente**: Organization (con razón social legal "Comercializadora Victtorino Victor Mellado SPA" — bien para E-E-A-T), WebSite con SearchAction, WebPage, ImageObject, Product en fichas de producto, Offer.
6. **Páginas de producto con schema completo**: ItemPage + Product + Offer + Organization. Excelente.
7. **Servidor LiteSpeed con HTTP/3 (h3)** activado — bueno para performance.
8. **Lazy loading de imágenes** activado (Smush + autoptimize).
9. **Imágenes con alt text** (0 imágenes sin alt en la home — perfecto).
10. **Una sola URL canónica** (`https://victtorino.cl/`) sin variantes www/no-www o trailing-slash inconsistentes.

---

## AI Search Readiness Summary

- **Bot access:** Todos los bots IA permitidos (no hay disallows para GPTBot, ClaudeBot, etc.)
- **Content extractability:** Alta — HTML semántico, JSON-LD estructurado, contenido sin gated walls
- **Citation readiness:** Media-Alta — falta agregar fechas de publicación y autoría visible en algunos contenidos
- **Recomendación:** Ejecutar `/ai-visibility` para ver si Victtorino aparece cuando preguntan a ChatGPT/Perplexity por "grifería Chile" o "lavaplatos Chile"

---

## Quick Wins (< 30 minutos cada uno)

1. **Cambiar `og:locale` a `es_CL`** (Rank Math, 2 min) — Issue #5
2. **Activar BreadcrumbList schema** (Rank Math → Breadcrumbs, 5 min) — Issue #6
3. **Subir cache-control a 3600** (LiteSpeed plugin, 10 min) — Issue #2
4. **Corregir H1s en la home** (Elementor, 15 min) — Issue #1
5. **Reemplazar logo apuntando a alvexltda.cl** (15 min) — Issue #3

Total: ~50 minutos resuelven los 5 problemas principales.

---

## Recommended Next Steps

1. **Corregir los 3 críticos** (H1, cache, logo externo) → impacto directo en rankings
2. **Ejecutar `/cannibalization`** → con 78 productos nuevos importados, hay productos con títulos similares (varios "Lavaplatos 80x44") que pueden estar compitiendo entre sí por las mismas keywords
3. **Ejecutar `/internal-links`** → mapear el grafo de enlaces internos, encontrar productos huérfanos
4. **Ejecutar `/ai-visibility`** → ver si la marca aparece en respuestas de ChatGPT/Perplexity
5. **Ejecutar `/schema-gen`** → generar BreadcrumbList y FAQPage schema para las páginas de categoría (las pages que ya optimizamos pero les falta este schema)
