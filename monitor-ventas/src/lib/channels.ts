import type { Canal } from './types'

// Color/ícono por canal, centralizado. `bg` = color de marca, `fg` = texto legible encima.
export const CANALES: Record<Canal, { nombre: string; bg: string; fg: string; icon: string }> = {
  mercadolibre: { nombre: 'MercadoLibre', bg: '#FFE600', fg: '#1a1a1a', icon: '🛒' },
  falabella:    { nombre: 'Falabella',    bg: '#22B14C', fg: '#ffffff', icon: '🏬' },
  paris:        { nombre: 'París',        bg: '#2D7DD2', fg: '#ffffff', icon: '🛍️' },
  walmart:      { nombre: 'Walmart',      bg: '#0B3D91', fg: '#ffffff', icon: '🏷️' },
  web:          { nombre: 'Web',          bg: '#7B2FBF', fg: '#ffffff', icon: '🌐' },
}

export const ORDEN_CANALES: Canal[] = ['mercadolibre', 'falabella', 'paris', 'walmart', 'web']
