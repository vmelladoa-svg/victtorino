import type { Comanda } from '../types'

// Defontana = VALIDADOR, no fuente. No dispara comandas; solo confirma que la
// venta quedó registrada en el ERP. Requiere API Token (pendiente, ver memoria defontana).
//
// TODO: consultar el documento de venta por folio/SKU/fecha y devolver true si existe.
export async function validarEnDefontana(_venta: Comanda): Promise<boolean> {
  return false // stub
}
