import type { Comanda } from '../types'

// París (Cencosud Marketplace) — API de seller (Mirakl). Pedidos y mensajes/preguntas.
// TODO: autenticar y mapear a Comanda { canal:'paris', ... }
export async function obtenerNuevas(_desde: number): Promise<Comanda[]> {
  return [] // stub
}
