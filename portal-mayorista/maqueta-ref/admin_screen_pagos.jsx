/* ============================================================
   Back-office — Pantallas: Dashboard · Pagos por validar
   ============================================================ */

function fmtMon(n) { return CLP(n); }

/* ---------------- DASHBOARD ---------------- */
function AdmDashboard({ orders, onNav, onOpenPago }) {
  const porValidar = orders.filter((o) => o.estado === "por_validar");
  const enProceso = orders.filter((o) => ["validado", "comprado", "despachado"].includes(o.estado));
  const ventasMes = orders.reduce((s, o) => s + o.subtotal, 0);
  const margenMes = orders.reduce((s, o) => s + o.margen, 0);
  const margenPct = Math.round((margenMes / ventasMes) * 100);
  const porComprar = orders.filter((o) => o.estado === "validado");

  const recientes = [...orders].slice(0, 5);

  return (
    <div className="adm-page">
      <div className="stat-grid">
        <StatCard label="Ventas del mes" value={fmtMon(ventasMes)} icon="bolt" tone="brand" hint="vs. mes anterior" trend={12} />
        <StatCard label="Margen estimado" value={fmtMon(margenMes)} icon="shield" tone="ok" hint={margenPct + "% sobre venta"} />
        <StatCard label="Pagos por validar" value={porValidar.length} icon="clock" tone="amber" hint={fmtMon(porValidar.reduce((s,o)=>s+o.total,0)) + " en espera"} />
        <StatCard label="En proceso / despacho" value={enProceso.length} icon="truck" tone="blue" hint="pedidos activos" />
      </div>

      <div className="adm-cols">
        <section className="panel">
          <div className="panel-head">
            <h2><Icon name="clock" size={18} />Pagos por validar</h2>
            <button className="panel-link" onClick={() => onNav("pagos")}>Ver todos<Icon name="chevright" size={15} /></button>
          </div>
          {porValidar.length === 0 && <div className="panel-empty">No hay pagos pendientes. 🎉</div>}
          {porValidar.map((o) => (
            <button className="prow" key={o.folio} onClick={() => onOpenPago(o)}>
              <div className="prow-main">
                <span className="mono prow-folio">{o.folio}</span>
                <span className="prow-cli">{o.cliente.empresa}</span>
              </div>
              <span className="prow-bank"><Icon name="doc" size={14} />{o.comprobante.banco}</span>
              <strong className="mono">{fmtMon(o.total)}</strong>
              <span className="prow-cta">Validar<Icon name="chevright" size={14} /></span>
            </button>
          ))}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2><Icon name="package" size={18} />Por comprar al importador</h2>
            <button className="panel-link" onClick={() => onNav("compras")}>Gestionar<Icon name="chevright" size={15} /></button>
          </div>
          {porComprar.length === 0 && <div className="panel-empty">Sin compras pendientes.</div>}
          {porComprar.map((o) => (
            <div className="prow static" key={o.folio}>
              <div className="prow-main">
                <span className="mono prow-folio">{o.folio}</span>
                <span className="prow-cli">{o.items.length} productos · {o.cajas} cajas</span>
              </div>
              <span className="prow-bank"><Icon name="box" size={14} />{o.items[0].importador.split(" ")[0]}…</span>
              <strong className="mono">{fmtMon(o.costoTotal)}</strong>
              <span className="prow-tag">costo</span>
            </div>
          ))}
        </section>
      </div>

      <section className="panel">
        <div className="panel-head"><h2><Icon name="grid" size={18} />Actividad reciente</h2></div>
        <div className="adm-table">
          <div className="adm-tr adm-thd">
            <span>Folio</span><span>Cliente</span><span>Estado</span><span className="ar">Venta</span><span className="ar">Margen</span><span></span>
          </div>
          {recientes.map((o) => (
            <button className="adm-tr" key={o.folio} onClick={() => onNav("pedidos")}>
              <span className="mono">{o.folio}</span>
              <span className="td-cli">{o.cliente.empresa}</span>
              <span><AdmStatus id={o.estado} small /></span>
              <span className="ar mono">{fmtMon(o.subtotal)}</span>
              <span className="ar mono td-margin">+{fmtMon(o.margen)}</span>
              <span className="ar"><Icon name="chevright" size={15} /></span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ---------------- PAGOS POR VALIDAR ---------------- */
function AdmPagos({ orders, onValidar, onRechazar, openPago, setOpenPago }) {
  const porValidar = orders.filter((o) => o.estado === "por_validar");

  return (
    <div className="adm-page">
      {porValidar.length === 0 ? (
        <div className="panel panel-empty-big">
          <Icon name="check" size={32} />
          <h3>Todo al día</h3>
          <p>No hay comprobantes pendientes de validación.</p>
        </div>
      ) : (
        <div className="pagos-grid">
          {porValidar.map((o) => (
            <div className="pago-card" key={o.folio}>
              <div className="pago-card-head">
                <div>
                  <span className="mono pago-folio">{o.folio}</span>
                  <h3>{o.cliente.empresa}</h3>
                  <small>{o.fecha} · {o.hora} · {o.cliente.contacto}</small>
                </div>
                <strong className="mono pago-amount">{fmtMon(o.total)}</strong>
              </div>
              <div className="pago-comp">
                <div className="pago-comp-thumb"><Icon name="doc" size={22} /></div>
                <div className="pago-comp-info">
                  <b>{o.comprobante.archivo}</b>
                  <small>{o.comprobante.banco} · {o.comprobante.fecha}</small>
                </div>
                <button className="pago-comp-view" onClick={() => setOpenPago(o)}>Ver<Icon name="chevright" size={14} /></button>
              </div>
              <div className="pago-actions">
                <Button variant="ghost" size="sm" icon="x" onClick={() => onRechazar(o.folio)}>Rechazar</Button>
                <Button size="sm" icon="check" onClick={() => onValidar(o.folio)}>Validar pago</Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {openPago && (
        <Modal title={"Comprobante · " + openPago.folio} onClose={() => setOpenPago(null)} wide>
          <div className="comp-modal">
            <div className="comp-doc">
              <div className="comp-doc-paper">
                <Icon name="doc" size={40} />
                <b>{openPago.comprobante.archivo}</b>
                <small>Vista previa del comprobante</small>
              </div>
            </div>
            <div className="comp-detail">
              <h4>Datos del pago</h4>
              <div className="comp-kv"><span>Cliente</span><b>{openPago.cliente.empresa}</b></div>
              <div className="comp-kv"><span>RUT</span><b className="mono">{openPago.cliente.rut}</b></div>
              <div className="comp-kv"><span>Banco origen</span><b>{openPago.comprobante.banco}</b></div>
              <div className="comp-kv"><span>Fecha transferencia</span><b>{openPago.comprobante.fecha}</b></div>
              <div className="comp-kv comp-kv-total"><span>Monto esperado</span><b className="mono">{fmtMon(openPago.total)}</b></div>
              <div className="comp-note"><Icon name="shield" size={14} />Confirmá que el monto y el titular coincidan antes de validar.</div>
              <div className="comp-modal-actions">
                <Button variant="ghost" icon="x" onClick={() => { onRechazar(openPago.folio); setOpenPago(null); }}>Rechazar</Button>
                <Button icon="check" onClick={() => { onValidar(openPago.folio); setOpenPago(null); }}>Validar pago</Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

Object.assign(window, { AdmDashboard, AdmPagos });
