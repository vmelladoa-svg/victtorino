<?php
// Importador propio: parsea el CSV (formato WC export, cabecera en español) y crea
// productos directamente, enganchando imágenes por nombre de archivo.
global $wpdb;
$file = '/home/u764256910/catalogo-import.csv';
$fh = fopen($file, 'r');
$headers = fgetcsv($fh);
$idx = array();
foreach ($headers as $i => $h) { $idx[trim($h)] = $i; }
function col($row, $idx, $label) { return (isset($idx[$label]) && isset($row[$idx[$label]])) ? $row[$idx[$label]] : ''; }

// Mapa nombre-de-archivo -> attachment ID
$att = $wpdb->get_results("SELECT post_id, meta_value FROM {$wpdb->postmeta} WHERE meta_key='_wp_attached_file'");
$imgmap = array();
foreach ($att as $a) { $imgmap[strtolower(basename($a->meta_value))] = (int) $a->post_id; }
function find_img($url, $imgmap) {
    $p = parse_url(trim($url), PHP_URL_PATH);
    $b = strtolower(basename($p ? $p : trim($url)));
    return isset($imgmap[$b]) ? $imgmap[$b] : 0;
}

// Resolver categorías "Padre > Hijo, Otra" creando términos
$catcache = array();
function get_cat_ids($str, &$catcache) {
    $ids = array();
    if (trim($str) === '') return $ids;
    foreach (explode(',', $str) as $path) {
        $path = trim($path); if ($path === '') continue;
        $parent = 0; $term_id = 0;
        foreach (array_map('trim', explode('>', $path)) as $name) {
            $key = $parent.'|'.$name;
            if (isset($catcache[$key])) { $term_id = $catcache[$key]; }
            else {
                $ex = get_terms(array('taxonomy'=>'product_cat','name'=>$name,'parent'=>$parent,'hide_empty'=>false));
                if (!is_wp_error($ex) && !empty($ex)) { $term_id = $ex[0]->term_id; }
                else { $r = wp_insert_term($name, 'product_cat', array('parent'=>$parent)); $term_id = is_wp_error($r) ? 0 : $r['term_id']; }
                $catcache[$key] = $term_id;
            }
            $parent = $term_id;
        }
        if ($term_id) $ids[] = $term_id;
    }
    return $ids;
}

$created=0; $img_set=0; $skipped_var=0; $skipped_dup=0; $skipped_empty=0;
while (($row = fgetcsv($fh)) !== false) {
    $type = col($row,$idx,'Tipo');
    if ($type === 'variation') { $skipped_var++; continue; }
    $name = trim(col($row,$idx,'Nombre'));
    if ($name === '') { $skipped_empty++; continue; }
    $sku = trim(col($row,$idx,'SKU'));
    if ($sku !== '' && wc_get_product_id_by_sku($sku)) { $skipped_dup++; continue; }

    $p = ($type === 'variable') ? new WC_Product_Variable() : new WC_Product_Simple();
    $p->set_name($name);
    if ($sku !== '') $p->set_sku($sku);
    $p->set_status(col($row,$idx,'Publicado') == '1' ? 'publish' : 'draft');
    $p->set_description(col($row,$idx,'Descripción'));
    $p->set_short_description(col($row,$idx,'Descripción corta'));
    $reg = col($row,$idx,'Precio normal'); if ($reg !== '') $p->set_regular_price($reg);
    $sale = col($row,$idx,'Precio rebajado'); if ($sale !== '') $p->set_sale_price($sale);
    $p->set_featured(col($row,$idx,'¿Está destacado?') == '1');
    $sq = col($row,$idx,'Inventario');
    if ($sq !== '') { $p->set_manage_stock(true); $p->set_stock_quantity((int)$sq); }
    $instock = col($row,$idx,'¿En inventario?');
    $p->set_stock_status(($instock=='1'||$instock==='') ? 'instock' : 'outofstock');
    $wt = col($row,$idx,'Peso (kg)'); if ($wt !== '') $p->set_weight($wt);
    $cats = get_cat_ids(col($row,$idx,'Categorías'), $catcache);
    if ($cats) $p->set_category_ids($cats);

    $imgs = col($row,$idx,'Imágenes');
    if (trim($imgs) !== '') {
        $ids = array();
        foreach (explode(',', $imgs) as $u) { $a = find_img($u, $imgmap); if ($a) $ids[] = $a; }
        if ($ids) { $p->set_image_id($ids[0]); $img_set++; if (count($ids) > 1) $p->set_gallery_image_ids(array_slice($ids,1)); }
    }
    $p->save();
    $created++;
}
fclose($fh);
echo "creados=$created | con_foto=$img_set | variaciones_saltadas=$skipped_var | dup_saltados=$skipped_dup | vacios=$skipped_empty\n";
