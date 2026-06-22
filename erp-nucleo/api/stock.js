import { query } from '../lib/db.js';
import { checkKey } from '../lib/auth.js';
import { stockVivo, stockDe } from '../lib/stock.js';

export default async function handler(req, res) {
  if (!checkKey(req)) return res.status(401).json({ error: 'no autorizado' });
  try {
    if (req.query?.codigo) {
      const stock = await stockDe(query, req.query.codigo);
      return res.status(200).json({ codigo: req.query.codigo, stock });
    }
    return res.status(200).json(await stockVivo(query));
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message });
  }
}
