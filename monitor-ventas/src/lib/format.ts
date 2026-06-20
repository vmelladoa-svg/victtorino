// Helpers reutilizables centralizados.

const clp = new Intl.NumberFormat('es-CL', {
  style: 'currency',
  currency: 'CLP',
  maximumFractionDigits: 0,
})

export const formatCLP = (n: number) => clp.format(n) // $19.990

const hora = new Intl.DateTimeFormat('es-CL', { hour: '2-digit', minute: '2-digit', hour12: false })
const fechaHora = new Intl.DateTimeFormat('es-CL', {
  weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
})

export const formatHora = (ms: number) => hora.format(ms)        // 14:35
export const formatFechaHora = (ms: number) => fechaHora.format(ms) // jue 19-06 14:35

// "hace 2 min" / "hace 45 s" a partir de ms transcurridos.
export function hace(ingreso: number, ahora: number): string {
  const s = Math.max(0, Math.floor((ahora - ingreso) / 1000))
  if (s < 60) return `hace ${s} s`
  const m = Math.floor(s / 60)
  if (m < 60) return `hace ${m} min`
  const h = Math.floor(m / 60)
  return `hace ${h} h ${m % 60} min`
}
