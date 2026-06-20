/* ============================================================
   Pantalla: Mis pedidos + seguimiento (timeline)
   ============================================================ */
const ESTADOS = [
  { id: "validacion", label: "Pago en validación", icon: "clock", tone: "amber",
    desc: "Recibimos tu comprobante. Estamos verificando la transferencia." },
  { id: "confirmado", label: "Pago confirmado", icon: "check", tone: "brand",
    desc: "Transferencia validada. Compramos al importador y preparamos tu pedido." },
  { id: "despacho", label: "En despacho", icon: "truck", tone: "blue",
    desc: "Tu pedido salió a ruta con el transportista hacia tu región." },
  { id: "entregado", label: "Entregado", icon: "package", tone: "ok",
    desc: "Pedido entregado en la dirección indicada. ¡Gracias por tu compra!" },
];
function estadoIndex(id) { return ESTADOS.findIndex((e) => e.id === id); }

function OrderTimeline({ order }) {
  const idx = estadoIndex(order.estado);
  return (
    <div className="tl">
      {ESTADOS.map((e, i) => {
        const done = i < idx, current = i === idx;
        return (
          <div key={e.id} className={"tl-step" + (done ? " is-done" : "") + (current ? " is-current" : "")}>
            <div className="tl-marker"><Icon name={done || current ? e.icon : e.icon} size={16} /></div>
            <div className="tl-body">
              <div className="tl-top">
                <strong>{e.label}</strong>
                {current && <Badge tone={e.tone} icon="bolt">Estado actual</Badge>}
                {done && <span className="tl-when mono">{order.fechas?.[e.id] || "✓"}</span>}
              </div>
              {(current || done) && <p>{e.desc}</p>}
              {current && e.id === "validacion" && (
                <span className="tl-eta"><Icon name="clock" size={13} />Validación estimada: 24–48h hábiles</span>
              )}
              {current && e.id === "despacho" && order.reg && (
                <span className="tl-eta"><Icon name="truck" size={13} />Llega a {order.reg.label} en {order.reg.dias} días hábiles</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function OrderCard({ order, open, onToggle, onAdvance }) {
  const est = ESTADOS[estadoIndex(order.estado)];
  return (
    <div className={"ocard" + (open ? " is-open" : "")}>
      <button className="ocard-head" onClick={onToggle}>
        <div className="ocard-id">
          <span className="mono folio">{order.folio}</span>
          <small>{order.fecha} · {order.items.length} productos · {order.cajas} cajas</small>
        </div>
        <div className="ocard-right">
          <Badge tone={est.tone} icon={est.icon}>{est.label}</Badge>
          <strong className="mono">{CLP(order.total)}</strong>
          <Icon name="chevdown" size={18} style={{ transform: open ? "rotate(180deg)" : "none", transition: ".2s" }} />
        </div>
      </button>
      {open && (
        <div className="ocard-body">
          <div className="ocard-cols">
            <div className="ocard-tl"><OrderTimeline order={order} /></div>
            <div className="ocard-side">
              <div className="ocard-block">
                <span className="lbl">Productos</span>
                {order.items.map((it, i) => (
                  <div className="ocard-prod" key={i}>
                    <ProductImage prod={PRODUCTS.find((p) => p.id === it.id)} h={44} label="" />
                    <div><b>{it.name}</b><small className="mono">{it.cajas} cajas · {it.unidades} u.</small></div>
                    <span className="mono">{CLP(it.total)}</span>
                  </div>
                ))}
              </div>
              <div className="ocard-block">
                <span className="lbl">Despacho</span>
                <div className="ocard-kv"><span><Icon name="pin" size={14} />{order.reg?.label || "—"}</span><b className="mono">{CLP(order.despacho || 0)}</b></div>
                <div className="ocard-kv"><span><Icon name="doc" size={14} />Comprobante</span><b>{order.comprobante || "enviado"}</b></div>
                <div className="ocard-kv total"><span>Total pagado</span><b className="mono">{CLP(order.total)}</b></div>
              </div>
              {estadoIndex(order.estado) < ESTADOS.length - 1 && (
                <button className="ocard-sim" onClick={onAdvance}>
                  <Icon name="bolt" size={14} />Simular avance de estado
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function OrdersScreen({ orders, onNav, advance }) {
  const [openId, setOpenId] = useState(orders[0]?.folio || null);
  const [filtro, setFiltro] = useState("todos");
  const list = orders.filter((o) => filtro === "todos" || o.estado === filtro);

  if (orders.length === 0) {
    return (
      <div className="empty big">
        <Icon name="truck" size={34} />
        <h2>Todavía no tenés pedidos</h2>
        <p>Cuando completes una compra, vas a poder seguir acá su estado: validación, despacho y entrega.</p>
        <Button icon="grid" onClick={() => onNav("catalog")}>Ir al catálogo</Button>
      </div>
    );
  }
  return (
    <div className="orders">
      <div className="page-head"><h1>Mis pedidos</h1></div>
      <div className="orders-filters">
        <button className={"chip" + (filtro === "todos" ? " is-on" : "")} onClick={() => setFiltro("todos")}>Todos ({orders.length})</button>
        {ESTADOS.map((e) => {
          const n = orders.filter((o) => o.estado === e.id).length;
          if (!n) return null;
          return <button key={e.id} className={"chip" + (filtro === e.id ? " is-on" : "")} onClick={() => setFiltro(e.id)}><Icon name={e.icon} size={15} />{e.label} ({n})</button>;
        })}
      </div>
      <div className="orders-list">
        {list.map((o) => (
          <OrderCard key={o.folio} order={o} open={openId === o.folio}
            onToggle={() => setOpenId(openId === o.folio ? null : o.folio)}
            onAdvance={() => advance(o.folio)} />
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { ESTADOS, OrdersScreen });
