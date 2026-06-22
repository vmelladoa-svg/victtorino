// Auth mínima por token compartido. ponytail: un solo negocio, no hay multi-usuario.
export function checkKey(req) {
  const key = req.headers['x-erp-key'];
  return !!process.env.ERP_KEY && key === process.env.ERP_KEY;
}
