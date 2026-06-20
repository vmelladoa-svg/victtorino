# Meta Pixel — Victtorino Web

**Pixel ID:** `1361965342502798`
**Cuenta publicitaria:** act_2087839325471724 (Victtorino Ads)
**Creado:** 2026-05-16

---

## Código del Pixel (instalar en <head> de todas las páginas)

```html
<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');

fbq('init', '1361965342502798');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1361965342502798&ev=PageView&noscript=1"
/></noscript>
<!-- End Facebook Pixel Code -->
```

---

## Opción A — Plugin "Meta for WooCommerce" (RECOMENDADO)

Plugin oficial de Meta para WooCommerce. Instala el pixel Y rastrea eventos automáticamente:
- PageView, ViewContent, AddToCart, InitiateCheckout, **Purchase** (crítico para ROAS)

### Pasos:
1. WordPress Admin → Plugins → Añadir nuevo
2. Buscar: **"Meta for WooCommerce"** (autor: Meta)
3. Instalar → Activar
4. WooCommerce → Settings → Integration → Facebook
5. "Get Started" → Conectar con Facebook
6. Seleccionar Business Manager: **victtorino_griferias**
7. Seleccionar Pixel: **Victtorino Web (1361965342502798)**
8. Seleccionar Catálogo → Crear nuevo si no existe
9. Guardar

**Ventaja:** Configura automáticamente el Catálogo de Productos para Advantage+ Shopping.

---

## Opción B — Plugin "Insert Headers and Footers" (más simple)

Solo instala PageView. No rastrea eventos de WooCommerce automáticamente.

### Pasos:
1. WordPress Admin → Plugins → Añadir nuevo
2. Buscar: **"Insert Headers and Footers"** (autor: WPBeginner)
3. Instalar → Activar
4. Settings → Insert Headers and Footers
5. Pegar el código del pixel en la sección **Header**
6. Guardar

**Limitación:** Solo registra visitas. No registra compras automáticamente → ROAS no calculable sin eventos adicionales.

---

## Eventos a configurar (después del plugin)

| Evento | Cuándo | Importancia |
|--------|--------|-------------|
| PageView | Todas las páginas | Remarketing general |
| ViewContent | Páginas de producto | Remarketing producto específico |
| AddToCart | Al agregar al carrito | Funnel |
| InitiateCheckout | Al entrar al checkout | Funnel |
| **Purchase** | Confirmación de compra | **ROAS — crítico** |

---

## Verificación post-instalación

1. Instalar extensión Chrome: **Meta Pixel Helper**
2. Abrir victtorino.cl → debe aparecer PageView verde
3. Abrir una página de producto → debe aparecer ViewContent
4. Agregar al carrito → AddToCart
5. Iniciar checkout → InitiateCheckout
6. Hacer compra de prueba → Purchase

**En Meta Business Manager:** Eventos Manager → Victtorino Web → verificar eventos entrantes (puede tardar 20 min)

---

## Próximos pasos post-pixel

1. Pixel instalado y verificado ✅
2. Catálogo de productos conectado → Advantage+ Shopping (Ad Set 1C)
3. Con 50 conversiones → activar Advantage+ Shopping
4. Con datos de pixel 7+ días → activar Campaña 2 (Remarketing)
