<?php
/**
 * Plugin Name: Trade - Identidad de marca
 * Description: Colores de marca (cian/azul/navy) y ajustes minimalistas para Trade. 2026-06-09.
 */
if (!defined('ABSPATH')) exit;

add_action('wp_head', function () {
    ?>
<style id="trade-brand">
:root{ --t-cyan:#00B8E6; --t-blue:#0084B8; --t-navy:#003078; --t-ink:#23303B; }

/* enlaces */
a{ color:var(--t-blue); }
a:hover,a:focus{ color:var(--t-cyan); }

/* botones (Astra + WooCommerce) */
.ast-button,.button,button.button,input[type="submit"],
.wp-block-button__link,
.woocommerce a.button,.woocommerce button.button,.woocommerce input.button,
.woocommerce #respond input#submit,
.woocommerce .single_add_to_cart_button,
.woocommerce-cart .wc-proceed-to-checkout a.checkout-button{
  background-color:var(--t-blue)!important; color:#fff!important;
  border-color:var(--t-blue)!important; border-radius:6px!important;
  transition:background-color .2s ease!important;
}
.ast-button:hover,.button:hover,button.button:hover,
.woocommerce a.button:hover,.woocommerce button.button:hover,
.woocommerce .single_add_to_cart_button:hover,
.woocommerce-cart .wc-proceed-to-checkout a.checkout-button:hover{
  background-color:var(--t-navy)!important; color:#fff!important;
}

/* precios y badges */
.woocommerce span.price,.woocommerce .price,.woocommerce ul.products li.product .price{
  color:var(--t-navy)!important; font-weight:700!important;
}
.woocommerce span.onsale{ background-color:var(--t-cyan)!important; color:#fff!important; }

/* título del sitio (si se mostrara) */
.site-title a{ color:var(--t-navy)!important; }

/* footer navy minimalista */
.site-footer,.footer-sml-layout,footer.site-footer{ background-color:var(--t-navy)!important; }
.site-footer *,.footer-sml-layout *{ color:#dbeefb!important; }
.site-footer a:hover{ color:var(--t-cyan)!important; }

/* logo: tamaño cómodo y limpio */
.custom-logo{ max-height:54px!important; width:auto!important; }

/* toques minimalistas */
.woocommerce ul.products li.product,.woocommerce-page ul.products li.product{ text-align:left; }
.ast-separate-container .ast-article-post,.ast-separate-container .ast-article-single{ box-shadow:none; }
</style>
    <?php
}, 99);
