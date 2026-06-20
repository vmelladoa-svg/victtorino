// Sincroniza el catálogo de Trade (productos + fotos) desde la tienda WooCommerce.
// SOLO LECTURA sobre la fuente: hace `wp eval-file -` (PHP por stdin) para exportar
// y `tar` para bajar imágenes. No modifica nada en el servidor.
// Cross-platform: usa ssh.exe/tar con stdin/stdout manejados por Node (sin pipes de shell).
//
// Uso:  npm run sync     (o: node scripts/sync-catalog.mjs)
// Config por variables de entorno (defaults para el server actual de Hostinger):
//   TRADE_SSH        usuario@host        (def: u764256910@212.85.6.38)
//   TRADE_SSH_PORT   puerto ssh          (def: 65002)
//   TRADE_SSH_KEY    ruta llave privada  (def: ~/.ssh/cloudways_victtorino_rsa)
//   TRADE_WP_PATH    path del WordPress  (def: ~/domains/tradeglobalchile.cl/public_html)
//   TRADE_BASE_URL   base de uploads     (def: https://tradeglobalchile.cl/wp-content/uploads/)

import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync, mkdirSync, readdirSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import * as tar from "tar";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SSH = process.env.TRADE_SSH || "u764256910@212.85.6.38";
const PORT = process.env.TRADE_SSH_PORT || "65002";
const KEY = process.env.TRADE_SSH_KEY || join(homedir(), ".ssh", "cloudways_victtorino_rsa");
const WP = process.env.TRADE_WP_PATH || "~/domains/tradeglobalchile.cl/public_html";
const BASE_URL = process.env.TRADE_BASE_URL || "https://tradeglobalchile.cl/wp-content/uploads/";

const SSH_ARGS = ["-p", PORT, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", "-i", KEY, SSH];

// ssh remoto: ejecuta `remoteCmd` en bash del server; `input` va por stdin; devuelve stdout.
function ssh(remoteCmd, { input, binary } = {}) {
  return execFileSync("ssh", [...SSH_ARGS, remoteCmd], {
    input: input ?? "",
    maxBuffer: 256 * 1024 * 1024,
    encoding: binary ? null : "utf8",
    windowsHide: true,
  });
}

// Mapeo categorías de la tienda → las 7 del diseño Trade.
const CAT_MAP = {
  "Grifería": "Grifería", "Lavaplatos": "Cocina", "Lavamanos": "Baño", "Espejos": "Espejos",
  "WC e Inodoros": "WC e Inodoros", "Shower/Mamparas/Receptáculos": "Shower & Mamparas",
  "Dispensador": "Baño", "Agarraderas y Barras": "Baño", "Sifones y Desagües": "Accesorios",
  "Accesorios": "Accesorios",
};
function pickCategory(cats) {
  const mapped = (cats || []).map((c) => CAT_MAP[c]).filter(Boolean);
  return mapped.find((c) => c !== "Accesorios") || mapped[0] || "Accesorios";
}

// --- 1) Exportar catálogo (read-only, PHP por stdin) ----------------------
const PHP = `<?php
$ps=get_posts(["post_type"=>"product","post_status"=>"publish","posts_per_page"=>-1]);
$out=[];
foreach($ps as $p){
  $pr=wc_get_product($p->ID);
  $cats=wp_get_post_terms($p->ID,"product_cat",["fields"=>"names"]);
  $img=get_the_post_thumbnail_url($p->ID,"full");
  $gal=[]; foreach($pr->get_gallery_image_ids() as $gid){ $u=wp_get_attachment_url($gid); if($u)$gal[]=$u; }
  $out[]=["id"=>$p->ID,"name"=>$p->post_title,"sku"=>$pr->get_sku(),
    "price"=>$pr->get_price(),"regular"=>$pr->get_regular_price(),"sale"=>$pr->get_sale_price(),
    "cats"=>$cats,"img"=>$img?:"","gallery"=>$gal];
}
echo json_encode($out);`;

console.log("→ Exportando catálogo desde la tienda (solo lectura)…");
const raw = ssh(`cd ${WP} && wp eval-file - 2>/dev/null`, { input: PHP });
const woo = JSON.parse(raw.slice(raw.indexOf("["), raw.lastIndexOf("]") + 1));
console.log(`  ${woo.length} productos`);

// --- 2) Transformar a Product[] -------------------------------------------
const files = new Set();
const products = woo.map((p, i) => {
  const price = Math.round(parseFloat(p.price || p.regular || 0));
  const reg = Math.round(parseFloat(p.regular || 0));
  const sale = p.sale !== "" && p.sale != null ? Math.round(parseFloat(p.sale)) : null;
  // galería: principal primero + galería, sin duplicados
  const urls = [...new Set([p.img, ...(p.gallery || [])].filter(Boolean))];
  urls.forEach((u) => files.add(u.replace(BASE_URL, "")));
  const images = urls.map((u) => "/products/" + u.split("/").pop());
  return {
    id: "p" + (i + 1),
    name: p.name,
    price,
    priceOriginal: sale && reg && reg > sale ? reg : null,
    lowStock: false, // stock de la fuente poco fiable; reactivar cuando sea real
    sku: p.sku || "TR-" + p.id,
    category: pickCategory(p.cats),
    image: images[0],
    images,
  };
});

// --- 3) Bajar imágenes (tar por SSH, read-only) ---------------------------
console.log(`→ Descargando ${files.size} imágenes…`);
const tmp = mkdtempSync(join(tmpdir(), "trade-sync-"));
const tarGz = join(tmp, "imgs.tar.gz");
const buf = ssh(`cd ${WP}/wp-content/uploads && tar -czf - -T - 2>/dev/null`, {
  input: [...files].join("\n"),
  binary: true,
});
writeFileSync(tarGz, buf);
const outDir = join(ROOT, "public", "products");
rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });
// tar (JS puro, multiplataforma) — extrae aplanando 2 niveles (AAAA/MM/).
await tar.x({ file: tarGz, strip: 2, C: outDir });
const have = new Set(readdirSync(outDir));
const missing = products
  .flatMap((p) => p.images || [])
  .filter((src) => !have.has(src.replace("/products/", ""))).length;
console.log(`  ${have.size} imágenes guardadas · faltantes: ${missing}`);

// --- 4) Escribir lib/products.ts ------------------------------------------
const header =
  "// Catálogo Trade — datos reales sincronizados desde la tienda (solo lectura).\n" +
  "// Generado por scripts/sync-catalog.mjs — no editar a mano.\n" +
  'import type { Product } from "./types";\n\nexport const PRODUCTS: Product[] = ';
writeFileSync(join(ROOT, "lib", "products.ts"), header + JSON.stringify(products, null, 2) + ";\n");
rmSync(tmp, { recursive: true, force: true });

const byCat = {};
products.forEach((p) => (byCat[p.category] = (byCat[p.category] || 0) + 1));
console.log("✓ lib/products.ts actualizado");
console.log(`  ${products.length} productos · ${products.filter((p) => p.priceOriginal).length} en oferta`);
console.log("  por categoría:", JSON.stringify(byCat));
