<?php
/**
 * Plugin Name: VTR Victtorino Gone
 * Description: Cuando alguien entra por victtorino.cl, devuelve 410 (no disponible) en vez de redirigir a Trade. Corta el "puente" Victtorino -> Trade sin tocar DNS, correo ni redes sociales. tradeglobalchile.cl no se ve afectado.
 * Author: Trade
 */
if (!defined('ABSPATH')) exit;

// No actuar en consola (WP-CLI / cron) ni peticiones internas: solo navegadores reales.
if ((defined('WP_CLI') && WP_CLI) || php_sapi_name() === 'cli' || empty($_SERVER['REQUEST_METHOD'])) return;

if (!empty($_SERVER['HTTP_HOST']) && stripos($_SERVER['HTTP_HOST'], 'victtorino.cl') !== false) {
    if (!headers_sent()) {
        http_response_code(410); // Gone -> Google lo des-indexa
        header('X-Robots-Tag: noindex, nofollow', true);
        header('Cache-Control: no-store, max-age=0');
        header('Content-Type: text/html; charset=utf-8');
    }
    echo '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Sitio no disponible</title>'
       . '<style>body{font-family:system-ui,Arial,sans-serif;background:#0f1115;color:#cbd2db;display:grid;place-items:center;min-height:100vh;margin:0;text-align:center;padding:24px}h1{font-weight:700;font-size:26px;margin:0 0 8px;color:#fff}p{margin:0;color:#8b93a1}</style>'
       . '</head><body><div><h1>Este sitio ya no está disponible.</h1><p>Gracias por tu visita.</p></div></body></html>';
    exit;
}
