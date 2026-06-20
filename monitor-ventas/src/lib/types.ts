export type Canal = 'mercadolibre' | 'falabella' | 'paris' | 'walmart' | 'web'
export type Tipo = 'venta' | 'pregunta'
export type Envio = 'flex' | 'normal' // Flex = despacho propio mismo día; Normal = colecta/courier

export interface Comanda {
  id: string
  tipo: Tipo
  canal: Canal
  cuenta?: string          // ML opera con varias cuentas (C1/C2/C3)
  producto: string
  sku: string
  foto: string             // URL miniatura (maqueta = placeholder; real = cache fotos ML por SKU)
  monto?: number           // solo ventas: monto de la venta, en CLP
  precio: number           // precio de lista del producto, en CLP (se muestra en ventas y preguntas)
  pregunta?: string        // solo preguntas
  ingreso: number          // epoch ms (hora de la venta / ingreso de la pregunta)
  envio?: Envio            // solo ventas
  despacharAntes?: number  // solo ventas: epoch ms límite para despachar (fecha + hora)
  validadoDefontana?: boolean // solo ventas (Defontana = validador, no fuente)
  leaving?: boolean        // marca interna para la animación de salida
}
