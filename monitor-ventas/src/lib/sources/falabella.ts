import type { Comanda } from '../types'

// Falabella Seller Center — API de pedidos (fetchProductlist / Seller API) y preguntas.
// TODO: autenticar (cuenta Trade Global) y mapear pedidos/preguntas a Comanda { canal:'falabella', ... }
export async function obtenerNuevas(_desde: number): Promise<Comanda[]> {
  return [] // stub
}
