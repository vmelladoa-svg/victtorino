import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { listarProductos, importarProductos } from '../lib/productos.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  try {
    if (req.method === 'GET') {
      return res.status(200).json(await listarProductos(query));
    }
    if (req.method === 'POST') {
      const filas = Array.isArray(req.body) ? req.body : (req.body?.filas ?? []);
      return res.status(200).json(await importarProductos(query, filas));
    }
    return res.status(405).json({ error: 'método no permitido' });
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
