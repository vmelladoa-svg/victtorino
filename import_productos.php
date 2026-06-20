<?php
// Importa el catálogo (formato WC export) a WooCommerce, enganchando imágenes por URL.
$file = '/home/u764256910/catalogo-final.csv';
if (!file_exists($file)) { echo "NO existe el CSV: $file\n"; return; }

if (!class_exists('WC_Product_CSV_Importer'))           include_once WC_ABSPATH.'includes/import/class-wc-product-csv-importer.php';
if (!class_exists('WC_Product_CSV_Importer_Controller')) include_once WC_ABSPATH.'includes/admin/importers/class-wc-product-csv-importer-controller.php';

$fh = fopen($file,'r'); $headers = fgetcsv($fh); fclose($fh);
echo "columnas: ".count($headers)."\n";

$controller = new WC_Product_CSV_Importer_Controller();
$ref = new ReflectionMethod('WC_Product_CSV_Importer_Controller','auto_map_columns');
$ref->setAccessible(true);
$mapping = $ref->invoke($controller, $headers);

$args = array(
  'mapping'         => $mapping,
  'parse'           => true,
  'update_existing' => false,
  'lines'           => -1,
  'prevent_timeouts'=> false,
);
$importer = new WC_Product_CSV_Importer($file, $args);
$r = $importer->import();
echo "imported=".count($r['imported'])." updated=".count($r['updated'])." failed=".count($r['failed'])." skipped=".count($r['skipped'])."\n";
foreach (array_slice($r['failed'],0,6) as $e) { echo "FAIL: ".$e->get_error_message()."\n"; }
