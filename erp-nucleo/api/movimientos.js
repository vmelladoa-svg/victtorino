import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { insertarMovimientos } from '../lib/movimientos.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  if (req.method !== 'POST') return res.status(405).json({ error: 'método no permitido' });
  try {
    const movs = Array.isArray(req.body) ? req.body : [req.body];
    return res.status(200).json(await insertarMovimientos(query, movs));
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
