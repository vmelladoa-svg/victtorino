// erp-web.mjs — Trae ventas confirmadas de WooCommerce y las normaliza.
// Reusa el cliente Woo del Monitor (web-feed.mjs). Read-only.
import { getOrders, WC_BASE } from "./web-feed.mjs";
import { normalizarWeb } from "./erp-build.mjs";

export async function ventasWeb() {
  const url = `${WC_BASE}/wp-json/wc/v3/orders?per_page=50&orderby=date&order=desc&status=processing,completed`;
  const raw = await getOrders(url);
  return normalizarWeb(raw);
}
