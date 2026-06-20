// Scraper READ-ONLY de la web (WooCommerce, tradeglobalchile.cl) -> formato Comanda.
// SOLO lee /wc/v3/orders. No escribe nada. Muestra ventas por despachar (processing/on-hold).
// ponytail: la web no tiene "Flex"; despacho es por courier -> envio 'normal', sin plazo ML.

const WC_BASE = process.env.WC_STORE_URL || 'https://tradeglobalchile.cl'
// Llaves ya presentes en el repo (importar_ml_a_woo.py). Override por env si se quiere.
const WC_KEY = process.env.WC_CONSUMER_KEY || 'ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15'
const WC_SECRET = process.env.WC_CONSUMER_SECRET || 'cs_3604e7ebdb8ff78442731344cc95af50516188a5'

const AUTH = 'Basic ' + Buffer.from(WC_KEY + ':' + WC_SECRET).toString('base64')

// WooCommerce responde lento (~5 s) y a veces se cae: timeout 12 s + 1 reintento.
async function getOrders(url) {
  for (let intento = 0; intento < 2; intento++) {
    try {
      const r = await fetch(url, { headers: { Authorization: AUTH }, signal: AbortSignal.timeout(12_000) })
      if (!r.ok) throw new Error('woo orders -> ' + r.status)
      return await r.json()
    } catch (e) {
      if (intento === 1) throw e
    }
  }
}

export async function obtenerFeedWeb() {
  const url = `${WC_BASE}/wp-json/wc/v3/orders?per_page=20&orderby=date&order=desc&status=processing,on-hold`
  const orders = await getOrders(url)

  return orders.map((o) => {
    const li = (o.line_items && o.line_items[0]) || {}
    return {
      id: 'w' + o.id,
      tipo: 'venta',
      canal: 'web',
      cuenta: 'tradeglobalchile.cl',
      producto: li.name || '(sin producto)',
      sku: li.sku || String(li.product_id || ''),
      monto: Math.round(Number(o.total) || 0),
      precio: Math.round(Number(o.total) || 0),
      foto: (li.image && li.image.src) || '',
      ingreso: Date.parse((o.date_created_gmt || o.date_created) + 'Z'),
      envio: 'normal',
      validadoDefontana: false,
    }
  })
}
