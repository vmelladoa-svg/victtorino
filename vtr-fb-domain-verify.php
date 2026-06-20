<?php
/**
 * Plugin Name: VTR Facebook Domain Verification
 * Description: Inyecta la meta-etiqueta de verificacion de dominio de Meta (Facebook) en el <head>. Necesaria para anclar el pixel/catalogo al dominio tradeglobalchile.cl y configurar eventos. Author: Trade
 */
if (!defined('ABSPATH')) exit;
add_action('wp_head', function () {
    echo '<meta name="facebook-domain-verification" content="qv26syruhcb31u5x7kaw21pogvdvag" />' . "\n";
}, 1);
