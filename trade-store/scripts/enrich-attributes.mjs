// Enriquece lib/products.ts con atributos (ficha técnica) desde MercadoLibre.
// Fuentes: ítems ML por SKU directo (ML-MLC...) + catálogo de la cuenta C3 (por código/nombre).
// Fallback: atributos básicos extraídos del nombre (material, color, medidas).
// Solo lectura sobre ML. Requiere credenciales ML C3 en el .env del repo (carpeta padre).
//
// Uso:  npm run enrich   (correr DESPUÉS de npm run sync, que regenera products.ts sin atributos)

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const ENV_PATH = join(ROOT, "..", ".env"); // .env vive en la raíz del repo
const C3_CLIENT_ID = "3959231945649654";
const C3_CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG";
const C3_SELLER = 1194418785;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const norm = (s) =>
  s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, " ").trim();

function readEnv() {
  const txt = readFileSync(ENV_PATH, "utf8");
  const out = {};
  for (const line of txt.split(/\r?\n/)) {
    const i = line.indexOf("=");
    if (i < 0) continue;
    const k = line.slice(0, i).trim();
    if (!(k in out)) out[k] = line.slice(i + 1).trim(); // primera ocurrencia
  }
  return { txt, vars: out };
}

async function refreshToken(refresh) {
  const body = new URLSearchParams({
    grant_type: "refresh_token",
    client_id: C3_CLIENT_ID,
    client_secret: C3_CLIENT_SECRET,
    refresh_token: refresh,
  });
  const r = await fetch("https://api.mercadolibre.com/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body,
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("No se pudo refrescar el token ML: " + JSON.stringify(j));
  return j;
}

const SKIP = new Set([
  "ITEM_CONDITION", "GTIN", "EMPTY_GTIN_REASON", "SELLER_SKU", "MANUFACTURER",
  "SELLER_PACKAGE_TYPE", "SHIPMENT_PACKING", "PACKAGE_LENGTH", "PACKAGE_WIDTH",
  "PACKAGE_HEIGHT", "PACKAGE_WEIGHT", "LINE", "PRODUCT_FEATURES",
]);
const PRIO = ["BRAND", "MODEL", "MATERIAL", "MAIN_MATERIAL", "COLOR", "MAIN_COLOR", "FINISHING",
  "INSTALLATION_TYPE", "LENGTH", "WIDTH", "HEIGHT", "DEPTH", "DIAMETER", "CAPACITY", "NET_WEIGHT"];
const skipName = /seller|paquete|universal|condici|fabricante|l[íi]nea|^sku$|garant|es marca|marca tom|destacad|pymes|fuente del producto|c[óo]digo del|^id$/i;
const rename = (n) =>
  n.replace("Modelo alfanumérico", "Modelo").replace("Color principal", "Color").replace("Materiales", "Material");

function fromML(it) {
  let a = it.attrs.filter((x) => x.value_name && !SKIP.has(x.id) && !skipName.test(x.name));
  a = a.filter((x) => !(/modelo/i.test(x.name) && x.value_name.length > 26));
  a = a.filter((x) => x.value_name.length <= 95);
  a = a.filter((x) => x.value_name.trim().toLowerCase() !== x.name.trim().toLowerCase());
  a = a.filter((x) => !/^[0-9a-f]{8}-[0-9a-f]{4}-/i.test(x.value_name));
  a.sort((x, y) => {
    const px = PRIO.indexOf(x.id), py = PRIO.indexOf(y.id);
    return (px < 0 ? 99 : px) - (py < 0 ? 99 : py);
  });
  const seen = new Set(), out = [];
  for (const x of a) {
    const nm = rename(x.name);
    const key = nm.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ name: nm, value: x.value_name });
    if (out.length >= 9) break;
  }
  return out;
}
function fromName(n) {
  const out = [];
  const mat = /acero inoxidable|inoxidable/i.test(n) ? "Acero inoxidable"
    : /cer[áa]mic/i.test(n) ? "Cerámica" : /acr[íi]lic/i.test(n) ? "Acrílico"
    : /vidrio/i.test(n) ? "Vidrio templado" : /pl[áa]stic/i.test(n) ? "Plástico"
    : /crom/i.test(n) ? "Cromado" : /\babs\b/i.test(n) ? "ABS" : null;
  if (mat) out.push({ name: "Material", value: mat });
  const cm = n.match(/\b(plateado|negro|blanco|cromado|dorado|gris|beige|chocolate|transparente|verde|rojo|azul|niquel)\b/i);
  if (cm) out.push({ name: "Color", value: cm[0][0].toUpperCase() + cm[0].slice(1).toLowerCase() });
  const md = n.match(/\d+\s?x\s?\d+(?:\s?x\s?\d+)?(?:\s?cm)?|\d+(?:\.\d+)?\s?cm|\b\d+\s?\/\s?\d+\b/i);
  if (md) out.push({ name: "Medidas", value: md[0].replace(/\s+/g, "") });
  return out;
}

const { txt: envTxt, vars: env } = readEnv();

console.log("→ Refrescando token ML…");
const tok = await refreshToken(env.ML_REFRESH_TOKEN_C3);
// persistir el token rotado en el .env
let newEnv = envTxt.replace(/ML_ACCESS_TOKEN_C3=.*/, "ML_ACCESS_TOKEN_C3=" + tok.access_token);
if (tok.refresh_token) newEnv = newEnv.replace(/ML_REFRESH_TOKEN_C3=.*/, "ML_REFRESH_TOKEN_C3=" + tok.refresh_token);
writeFileSync(ENV_PATH, newEnv);
const H = { Authorization: "Bearer " + tok.access_token };

const PRODUCTS_PATH = join(ROOT, "lib", "products.ts");
const src = readFileSync(PRODUCTS_PATH, "utf8");
const head = src.slice(0, src.indexOf("= [") + 2);
const prods = JSON.parse(src.slice(src.indexOf("= [") + 2, src.lastIndexOf("]") + 1));

const attrById = {};
async function multiget(ids) {
  for (let i = 0; i < ids.length; i += 20) {
    const r = await fetch(
      `https://api.mercadolibre.com/items?ids=${ids.slice(i, i + 20).join(",")}&attributes=id,title,attributes,seller_custom_field`,
      { headers: H }
    );
    const j = await r.json();
    if (Array.isArray(j))
      for (const e of j)
        if (e.code === 200 && e.body)
          attrById[e.body.id] = { title: e.body.title, sku: e.body.seller_custom_field || "", attrs: e.body.attributes || [] };
    await sleep(120);
  }
}

console.log("→ Trayendo ítems ML por SKU directo…");
await multiget(prods.filter((p) => /^ML-MLC\d+$/.test(p.sku)).map((p) => p.sku.replace("ML-", "")));

console.log("→ Trayendo catálogo C3 completo (todos los estados)…");
let c3ids = [], off = 0;
while (true) {
  // sin filtro de estado → incluye activos, pausados y cerrados
  const r = await fetch(`https://api.mercadolibre.com/users/${C3_SELLER}/items/search?limit=50&offset=${off}`, { headers: H });
  const j = await r.json();
  c3ids.push(...j.results);
  if (off + 50 >= j.paging.total || off >= 950) break;
  off += 50;
}
console.log(`  ${c3ids.length} ítems C3`);
await multiget(c3ids);

// merge de catálogos de otras cuentas (C1/C2) guardados por OAuth (snapshots .cN-attrs.json)
for (const f of ["c1", "c2"]) {
  const p = join(ROOT, `.${f}-attrs.json`);
  try {
    const cache = JSON.parse(readFileSync(p, "utf8"));
    let n = 0;
    for (const id in cache) if (!attrById[id]) { attrById[id] = cache[id]; n++; }
    console.log(`  + ${n} ítems de ${f.toUpperCase()} (cache)`);
  } catch {
    /* sin cache de esa cuenta */
  }
}

const byCode = {}, byName = {};
for (const id in attrById) {
  const it = attrById[id];
  const base = (it.sku || "").split("__")[0].trim().toUpperCase();
  if (base) byCode[base] = it;
  byName[norm(it.title)] = it;
}

let viaML = 0, viaName = 0, sin = 0;
for (const p of prods) {
  let it = null;
  if (/^ML-MLC\d+$/.test(p.sku) && attrById[p.sku.replace("ML-", "")]) it = attrById[p.sku.replace("ML-", "")];
  else {
    const code = (p.sku || "").split("__")[0].trim().toUpperCase();
    it = byCode[code] || byName[norm(p.name)] || null;
  }
  let attrs = it ? fromML(it) : [];
  if (attrs.length) viaML++;
  else {
    attrs = fromName(p.name);
    if (attrs.length) viaName++;
    else sin++;
  }
  if (attrs.length) p.attributes = attrs;
  else delete p.attributes;
}

// desvinculación: ningún atributo debe mostrar "Victtorino" (publicaciones viejas)
const deb = (s) => s.replace(/victtorino/gi, "Trade");
for (const p of prods)
  if (p.attributes) p.attributes = p.attributes.map((a) => ({ name: deb(a.name), value: deb(a.value) }));

writeFileSync(PRODUCTS_PATH, head + JSON.stringify(prods, null, 2) + ";\n");
console.log(`✓ products.ts enriquecido — ML: ${viaML} · del nombre: ${viaName} · sin atributos: ${sin} de ${prods.length}`);
