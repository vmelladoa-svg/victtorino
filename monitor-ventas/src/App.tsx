import { useEffect, useRef, useState, type CSSProperties } from 'react'
import type { Canal, Comanda, Tipo } from './lib/types'
import { CANALES, ORDEN_CANALES } from './lib/channels'
import { formatCLP, formatHora, formatFechaHora, hace } from './lib/format'
import { dinDon } from './lib/sound'
import { seedInicial, generarComanda } from './lib/mock'
import { obtenerNuevas as obtenerFeed } from './lib/sources/mercadolibre'
// ML + Web ya son reales (poll a /feed); Falabella/París/Walmart siguen en mock.

// Umbrales de envejecimiento (minutos) para destacar lo más antiguo.
const EDAD_ALERTA = 3
const EDAD_URGENTE = 6

type FiltroCanal = Canal | 'todos'
type FiltroTipo = Tipo | 'todos'

// Despacho "urgente" si quedan menos de 3 h para el límite (o ya pasó).
const despachoUrgente = (limite: number, ahora: number) => limite - ahora < 3 * 3_600_000

type Archivada = Comanda & { vistaEn: number } // comanda + momento en que se marcó como vista

export default function App() {
  const [comandas, setComandas] = useState<Comanda[]>(() => seedInicial(Date.now()))
  // Acumulado del día: persiste aunque la tarjeta se marque como vista.
  // ponytail: se reinicia al recargar; agregar reset a medianoche cuando se conecte a datos reales.
  const [ventasDia, setVentasDia] = useState(0)
  const [montoDia, setMontoDia] = useState(0)
  const [ahora, setAhora] = useState(Date.now())
  const [muted, setMuted] = useState(false)
  const [sonidoListo, setSonidoListo] = useState(false) // el navegador exige un gesto para sonar
  const [fCanal, setFCanal] = useState<FiltroCanal>('todos')
  const [fTipo, setFTipo] = useState<FiltroTipo>('todos')
  // Historial de comandas atendidas, persistido en localStorage (sobrevive recargas).
  const [historial, setHistorial] = useState<Archivada[]>(() => {
    try { return JSON.parse(localStorage.getItem('historial') ?? '[]') } catch { return [] }
  })
  const [verHistorial, setVerHistorial] = useState(false)
  const mutedRef = useRef(muted)
  mutedRef.current = muted
  const sonidoRef = useRef(sonidoListo)
  sonidoRef.current = sonidoListo
  // IDs ya vistos (en tablero o archivados) para no re-agregar lo mismo en cada poll.
  const conocidosRef = useRef<Set<string>>(new Set())

  // Reloj + recálculo de "hace X" cada segundo.
  useEffect(() => {
    const t = setInterval(() => setAhora(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])

  // Contar las ventas del seed inicial una vez (set-a-valor: seguro ante StrictMode).
  useEffect(() => {
    const v = comandas.filter((c) => c.tipo === 'venta')
    setVentasDia(v.length)
    setMontoDia(v.reduce((s, c) => s + (c.monto ?? 0), 0))
    // Sembrar IDs conocidos (tablero + historial) para el polling real.
    comandas.forEach((c) => conocidosRef.current.add(c.id))
    historial.forEach((h) => conocidosRef.current.add(h.id))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Polling REAL de los canales conectados cada 60 s (GET /feed). Solo agrega lo nuevo.
  useEffect(() => {
    let cancelado = false
    const tirar = async () => {
      try {
        const feed = await obtenerFeed()
        if (cancelado) return
        const nuevos = feed.filter((c) => !conocidosRef.current.has(c.id))
        if (!nuevos.length) return
        nuevos.forEach((c) => conocidosRef.current.add(c.id))
        setComandas((prev) => [...nuevos, ...prev])
        const v = nuevos.filter((c) => c.tipo === 'venta')
        if (v.length) {
          setVentasDia((n) => n + v.length)
          setMontoDia((m) => m + v.reduce((s, c) => s + (c.monto ?? 0), 0))
        }
        if (!mutedRef.current && sonidoRef.current) dinDon()
      } catch (e) {
        console.error('[ML feed]', e)
      }
    }
    tirar()
    const t = setInterval(tirar, 60_000)
    return () => { cancelado = true; clearInterval(t) }
  }, [])

  // Generador en vivo: nueva comanda cada 5–15 s (demo). FASE REAL: polling/webhook de las fuentes.
  useEffect(() => {
    let cancelado = false
    let timer: number
    const programar = () => {
      const ms = 5000 + Math.random() * 10000
      timer = window.setTimeout(() => {
        if (cancelado) return
        const c = generarComanda(Date.now())
        setComandas((prev) => [c, ...prev])
        if (c.tipo === 'venta') {
          setVentasDia((n) => n + 1)
          setMontoDia((m) => m + (c.monto ?? 0))
        }
        if (!mutedRef.current && sonidoListo) dinDon()
        programar()
      }, ms)
    }
    programar()
    return () => { cancelado = true; clearTimeout(timer) }
  }, [sonidoListo])

  // Persistir historial cuando cambie.
  useEffect(() => {
    try { localStorage.setItem('historial', JSON.stringify(historial.slice(0, 500))) } catch { /* sin storage */ }
  }, [historial])

  // Clic en tarjeta = marcar como vista -> archivar en historial -> salida -> quitar del tablero.
  // ponytail: NO escribe en ningún canal, solo archiva localmente.
  const marcarVista = (id: string) => {
    const c = comandas.find((x) => x.id === id)
    if (c && !c.leaving) setHistorial((h) => [{ ...c, vistaEn: Date.now() }, ...h])
    setComandas((prev) => prev.map((x) => (x.id === id ? { ...x, leaving: true } : x)))
    window.setTimeout(() => {
      setComandas((prev) => prev.filter((x) => x.id !== id))
    }, 350)
  }

  const habilitarSonido = () => {
    setSonidoListo(true)
    dinDon()
  }

  const vivas = comandas.filter((c) => !c.leaving)
  const totVentas = vivas.filter((c) => c.tipo === 'venta').length
  const totPreg = vivas.filter((c) => c.tipo === 'pregunta').length

  const porCanal = (c: Comanda) => fCanal === 'todos' || c.canal === fCanal
  // Ventas: el despacho más próximo arriba (lo urgente no se pasa).
  const ventas = comandas
    .filter((c) => c.tipo === 'venta' && porCanal(c))
    .sort((a, b) => (a.despacharAntes ?? Infinity) - (b.despacharAntes ?? Infinity))
  // Preguntas: la más antigua arriba (ninguna se queda sin responder).
  const preguntas = comandas
    .filter((c) => c.tipo === 'pregunta' && porCanal(c))
    .sort((a, b) => a.ingreso - b.ingreso)

  const verVentas = fTipo !== 'pregunta'
  const verPreguntas = fTipo !== 'venta'

  return (
    <div className="app">
      <header className="topbar">
        <div className="contadores">
          <span className="logo">📺 Monitor de Ventas</span>
          <Contador label="Pendientes" valor={vivas.length} tono="total" />
          <Contador label="Ventas" valor={totVentas} tono="venta" />
          <Contador label="Preguntas" valor={totPreg} tono="pregunta" />
          <span className="sep" />
          <Contador label="Ventas hoy" valor={ventasDia} tono="dia" />
          <span className="contador dia">
            <strong>{formatCLP(montoDia)}</strong> Total hoy
          </span>
        </div>

        <div className="filtros">
          <FiltroTipoBtns valor={fTipo} set={setFTipo} />
          <select
            className="sel-canal"
            value={fCanal}
            onChange={(e) => setFCanal(e.target.value as FiltroCanal)}
          >
            <option value="todos">Todos los canales</option>
            {ORDEN_CANALES.map((c) => (
              <option key={c} value={c}>{CANALES[c].nombre}</option>
            ))}
          </select>

          {!sonidoListo ? (
            <button className="btn-sonido alerta" onClick={habilitarSonido}>🔔 Activar sonido</button>
          ) : (
            <button className="btn-sonido" onClick={() => setMuted((m) => !m)}>
              {muted ? '🔇 Silenciado' : '🔊 Sonido'}
            </button>
          )}

          <button className="btn-sonido" onClick={() => setVerHistorial(true)}>
            📋 Historial ({historial.length})
          </button>

          <Reloj ahora={ahora} />
        </div>
      </header>

      {verHistorial && (
        <PanelHistorial
          items={historial}
          onClose={() => setVerHistorial(false)}
          onLimpiar={() => setHistorial([])}
        />
      )}

      <main className={`columnas ${verVentas && verPreguntas ? '' : 'una'}`}>
        {verVentas && (
          <section className="col">
            <h2 className="col-titulo venta">🛒 Ventas <span>{ventas.length}</span></h2>
            <div className="col-grid">
              {ventas.map((c) => (
                <Tarjeta key={c.id} c={c} ahora={ahora} onClick={() => marcarVista(c.id)} />
              ))}
              {ventas.length === 0 && <div className="vacio">Sin ventas pendientes 🎉</div>}
            </div>
          </section>
        )}
        {verPreguntas && (
          <section className="col">
            <h2 className="col-titulo pregunta">💬 Preguntas <span>{preguntas.length}</span></h2>
            <div className="col-grid">
              {preguntas.map((c) => (
                <Tarjeta key={c.id} c={c} ahora={ahora} onClick={() => marcarVista(c.id)} />
              ))}
              {preguntas.length === 0 && <div className="vacio">Sin preguntas pendientes 🎉</div>}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

function Contador({ label, valor, tono }: { label: string; valor: number; tono: string }) {
  return (
    <span className={`contador ${tono}`}>
      <strong>{valor}</strong> {label}
    </span>
  )
}

function FiltroTipoBtns({ valor, set }: { valor: FiltroTipo; set: (v: FiltroTipo) => void }) {
  const opts: { v: FiltroTipo; t: string }[] = [
    { v: 'todos', t: 'Todo' },
    { v: 'venta', t: 'Ventas' },
    { v: 'pregunta', t: 'Preguntas' },
  ]
  return (
    <div className="seg">
      {opts.map((o) => (
        <button
          key={o.v}
          className={valor === o.v ? 'on' : ''}
          onClick={() => set(o.v)}
        >
          {o.t}
        </button>
      ))}
    </div>
  )
}

function Reloj({ ahora }: { ahora: number }) {
  const d = new Date(ahora)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return <span className="reloj">{hh}:{mm}:{ss}</span>
}

function PanelHistorial({
  items, onClose, onLimpiar,
}: { items: Archivada[]; onClose: () => void; onLimpiar: () => void }) {
  const ventas = items.filter((c) => c.tipo === 'venta')
  const montoTotal = ventas.reduce((s, c) => s + (c.monto ?? 0), 0)
  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-top">
          <h2>📋 Historial atendido</h2>
          <div className="modal-resumen">
            {items.length} comandas · {ventas.length} ventas · {formatCLP(montoTotal)}
          </div>
          <div className="modal-acciones">
            {items.length > 0 && (
              <button className="btn-sonido" onClick={onLimpiar}>🗑 Limpiar</button>
            )}
            <button className="btn-sonido alerta" onClick={onClose}>Cerrar</button>
          </div>
        </div>
        <div className="modal-lista">
          {items.length === 0 && <div className="vacio">Aún no hay comandas atendidas.</div>}
          {items.map((c) => {
            const ch = CANALES[c.canal]
            return (
              <div key={c.id + c.vistaEn} className="hist-fila">
                <img className="hist-foto" src={c.foto} alt="" loading="lazy" />
                <span className={`badge-tipo ${c.tipo}`}>{c.tipo === 'venta' ? 'VENTA' : 'PREG'}</span>
                <span className="badge-canal" style={{ background: ch.bg, color: ch.fg }}>{ch.icon}</span>
                <span className="hist-prod">{c.producto}</span>
                <span className="hist-monto">{formatCLP(c.tipo === 'venta' ? (c.monto ?? 0) : c.precio)}</span>
                <span className="hist-hora">vista {formatFechaHora(c.vistaEn)}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function Tarjeta({ c, ahora, onClick }: { c: Comanda; ahora: number; onClick: () => void }) {
  const ch = CANALES[c.canal]
  const min = (ahora - c.ingreso) / 60000
  const edad = min >= EDAD_URGENTE ? 'urgente' : min >= EDAD_ALERTA ? 'alerta' : 'fresca'
  // Parpadeo por plazo de despacho sin acción: vencido > por-vencer.
  const plazo =
    c.tipo === 'venta' && c.despacharAntes
      ? c.despacharAntes <= ahora
        ? 'vencido'
        : despachoUrgente(c.despacharAntes, ahora)
          ? 'por-vencer'
          : ''
      : ''
  const cls = `card ${c.tipo} ${edad} ${plazo}${c.leaving ? ' leaving' : ' entrando'}`

  // Parpadeo acelerado: más rápido mientras más cerca del plazo y más pasado el vencimiento.
  let style: CSSProperties | undefined
  if (plazo === 'por-vencer' && c.despacharAntes) {
    const h = (c.despacharAntes - ahora) / 3_600_000 // 0..3 h restantes
    style = { animationDuration: `${(0.45 + (h / 3) * 0.95).toFixed(2)}s` } // 1.4s lejos → 0.45s encima
  } else if (plazo === 'vencido' && c.despacharAntes) {
    const min = (ahora - c.despacharAntes) / 60_000 // minutos pasados
    style = { animationDuration: `${Math.max(0.18, 0.4 - min * 0.01).toFixed(2)}s` } // baja hasta 0.18s
  }

  return (
    <article className={cls} style={style} onClick={onClick} title="Clic para marcar como vista">
      <div className="card-top">
        <span className={`badge-tipo ${c.tipo}`}>{c.tipo === 'venta' ? 'VENTA' : 'PREGUNTA'}</span>
        <span className="badge-canal" style={{ background: ch.bg, color: ch.fg }}>
          {ch.icon} {ch.nombre}
        </span>
      </div>

      <div className="card-cuerpo">
        <div className="thumb">
          <img src={c.foto} alt={c.producto} loading="lazy" />
          {c.tipo === 'pregunta' && <span className="thumb-q" title="Pregunta">❓</span>}
        </div>
        <div className="card-info">
          {c.cuenta && <div className="cuenta">Cuenta: {c.cuenta}</div>}
          <div className="producto">{c.producto}</div>
          <div className="sku">SKU {c.sku}</div>
        </div>
      </div>

      {c.tipo === 'venta' ? (
        <>
          <div className="monto">{formatCLP(c.monto ?? 0)}</div>
          <div className="meta-venta">
            <span className={`badge-envio ${c.envio}`}>
              {c.envio === 'flex' ? '⚡ Flex' : '📦 Envío normal'}
            </span>
            <span className="venta-hora">Venta {formatHora(c.ingreso)}</span>
          </div>
          {c.despacharAntes && (
            <div className={`despacho ${plazo}`}>
              {plazo === 'vencido' ? '⛔ Plazo VENCIDO: ' : '🚚 Despachar antes: '}
              <strong>{formatFechaHora(c.despacharAntes)}</strong>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="precio-pregunta">{formatCLP(c.precio)}</div>
          <div className="pregunta">“{c.pregunta}”</div>
        </>
      )}

      <div className="card-bot">
        <span className="tiempo">{hace(c.ingreso, ahora)}</span>
        {c.tipo === 'venta' && (
          <span className={`defontana ${c.validadoDefontana ? 'ok' : 'no'}`}>
            {c.validadoDefontana ? '✓ Defontana' : '⚠ Sin validar'}
          </span>
        )}
      </div>
    </article>
  )
}
