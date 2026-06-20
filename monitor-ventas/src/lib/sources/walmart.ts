import type { Comanda } from '../types'

// Walmart Chile (Lider Marketplace, Mirakl) — API de seller. Pedidos y mensajes.
// TODO: autenticar y mapear a Comanda { canal:'walmart', ... }
export async function obtenerNuevas(_desde: number): Promise<Comanda[]> {
  return [] // stub
}
