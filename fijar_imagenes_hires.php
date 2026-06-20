<?php
/**
 * Reemplaza las fotos de producto chicas (500px de ML) por la versión -F de
 * MercadoLibre (hasta 1200px), en su mismo path. Idempotente: salta las que ya
 * quedaron >=800px. Procesa hasta VTR_CAP por corrida (default 15).
 * Uso: VTR_CAP=15 wp eval-file fijar_imagenes_hires.php
 */
require_once ABSPATH . 'wp-admin/includes/image.php';
global $wpdb;
$pfx = $wpdb->prefix;
$cap = getenv('VTR_CAP') ? (int) getenv('VTR_CAP') : 15;

$ids = $wpdb->get_col(
    "SELECT DISTINCT product_id FROM {$pfx}gla_merchant_issues
     WHERE code='image_too_small_for_high_resolution'"
);

$done = 0; $skip = 0; $fail = 0;
foreach ($ids as $pid) {
    if ($done >= $cap) { echo "REACHED CAP $cap\n"; break; }
    $p = wc_get_product($pid);
    if (!$p) { continue; }
    $att = $p->get_image_id();
    if (!$att) { continue; }
    $path = get_attached_file($att);
    if (!$path || !file_exists($path)) { echo "NOFILE $pid\n"; $fail++; continue; }

    $cur = @getimagesize($path);
    if ($cur && max($cur[0], $cur[1]) >= 800) { $skip++; continue; } // ya arreglada

    $file = basename($path);
    if (!preg_match('/^D_(.+?)-O(?:-\d+)?\.\w+$/', $file, $mm)) { echo "NOPARSE $file\n"; $fail++; continue; }
    $mlid = $mm[1];
    $ext = strtolower(pathinfo($path, PATHINFO_EXTENSION));
    $ext_n = ($ext === 'jpeg') ? 'jpg' : $ext;

    $urls = array(
        "https://http2.mlstatic.com/D_{$mlid}-F.{$ext_n}",  // mismo formato: sin conversion
        "https://http2.mlstatic.com/D_{$mlid}-F.webp",       // fallback webp (convertir)
    );
    $data = null; $needconv = false;
    foreach ($urls as $i => $u) {
        $r = wp_remote_get($u, array('timeout' => 25));
        if (is_wp_error($r) || wp_remote_retrieve_response_code($r) != 200) { continue; }
        $b = wp_remote_retrieve_body($r);
        $sz = @getimagesizefromstring($b);
        if (!$sz || max($sz[0], $sz[1]) < 800) { continue; }
        $data = $b; $needconv = ($i === 1 && $ext_n !== 'webp');
        break;
    }
    if ($data === null) { echo "NOHIRES $pid ($file)\n"; $fail++; continue; }

    if (!$needconv) {
        file_put_contents($path, $data);
    } else {
        $tmp = $path . '.ml.webp';
        file_put_contents($tmp, $data);
        $ed = wp_get_image_editor($tmp);
        if (is_wp_error($ed)) { @unlink($tmp); echo "EDITORFAIL $pid\n"; $fail++; continue; }
        $res = $ed->save($path);
        @unlink($tmp);
        if (is_wp_error($res)) { echo "SAVEFAIL $pid\n"; $fail++; continue; }
    }

    $meta = wp_generate_attachment_metadata($att, $path);
    wp_update_attachment_metadata($att, $meta);
    $nd = @getimagesize($path);
    echo "OK $pid -> " . ($nd ? $nd[0] . 'x' . $nd[1] : '?') . " ($file)\n";
    $done++;
    gc_collect_cycles();
    usleep(350000);
}
echo "SUMMARY done=$done skipped=$skip fail=$fail total=" . count($ids) . "\n";
