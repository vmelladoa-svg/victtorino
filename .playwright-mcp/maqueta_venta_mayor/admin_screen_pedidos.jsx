/* ============================================================
   Back-office — Pantallas: Pedidos · Compras · Catálogo
   ============================================================ */

/* ---------------- PEDIDOS / FULFILLMENT ---------------- */
function AdmPedidos({ orders, onAdvance, onNav }) {
  const [filtro, setFiltro] = useStateA("todos");
  const [open, setOpen] = useStateA(null);
  const list = orders.filter((o) => filtro === "todos" || o.estado === filtro);

  const accionSiguiente = {
    validado: { label: "Generar OC importador", icon: "package", to: "comprado" },
    comprado: { label: "Marcar despachado", icon: "truck", to: "despachado" },
    despachado: { label: "Marcar entregado", icon: "check", to: "entregado" },
  };

  return (
    <div className="adm-page">
      <div className="adm-filters">
        <button className={"chip" + (filtro === "todos" ? " is-on" : "")} onClick={() => setFiltro("todos")}>Todos ({orders.length})</button>
        {ADM_ESTADOS.map((e) => {
          const n = orders.filter((o) => o.estado === e.id).length;
          if (!n) return null;
          return <button key={e.id} className={"chip" + (filtro === e.id ? " is-on" : "")} onClick={() => setFiltro(e.id)}><Icon name={e.icon} size={14} />{e.label} ({n})</button>;
        })}
      </div>

      <div className="ped-list">
        {list.map((o) => {
          const acc = accionSiguiente[o.estado];
          const isOpen = open === o.folio;
          return (
            <div className={"ped" + (isOpen ? " is-open" : "")} key={o.folio}>
              <div className="ped-head">
                <button className="ped-head-main" onClick={() => setOpen(isOpen ? null : o.folio)}>
                  <Icon name="chevdown" size={16} style={{ transform: isOpen ? "rotate(180deg)" : "none", transition: ".2s", color: "var(--ink-3)" }} />
                  <div className="ped-id">
                    <span className="mono">{o.folio}</span>
                    <small>{o.cliente.empresa} · {o.fecha}</small>
                  </div>
                </button>
                <div className="ped-pipe-wrap"><Pipeline id={o.estado} /></div>
                <AdmStatus id={o.estado} />
                <strong className="mono ped-total">{fmtMon(o.total)}</strong>
                {acc ? (
                  <Button size="sm" icon={acc.icon} onClick={() => onAdvance(o.folio, acc.to)}>{acc.label}</Button>
                ) : (
                  <span className="ped-done"><Icon name="check" size={14} />Completado</span>
                )}
              </div>
              {isOpen && (
                <div className="ped-body">
                  <div className="ped-cols">
                    <div>
                      <span className="lbl">Productos a despachar</span>
                      <div className="ped-items">
                        {o.items.map((it, i) => (
                          <div className="ped-item" key={i}>
                            <ProductImage prod={PRODUCTS.find((p) => p.id === it.id)} h={40} label="" />
                            <div className="ped-item-info">
                              <b>{it.name}</b>
                              <small className="mono">{it.sku} · {it.importador}</small>
                            </div>
                            <span className="mono ped-item-q">{it.cajas} cajas<small>{it.unidades} u.</small></span>
                            <span className="mono ped-item-cost">
                              <span className="ped-cost-venta">{fmtMon(it.ventaTotal)}</span>
                              <small>costo {fmtMon(it.costoTotal)}</small>
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="ped-side">
                      <span className="lbl">Despacho</span>
                      <div className="ped-kv"><span><Icon name="user" size={14} />{o.cliente.contacto}</span></div>
                      <div className="ped-kv"><span><Icon name="pin" size={14} />{o.dir}</span></div>
                      <div className="ped-kv"><span><Icon name="truck" size={14} />{o.reg.label} · {o.reg.dias} días</span></div>
                      {o.tracking && <div className="ped-kv"><span><Icon name="package" size={14} />{o.transportista}</span><b className="mono">{o.tracking}</b></div>}
                      {o.ocImportador && <div className="ped-kv"><span><Icon name="doc" size={14} />OC importador</span><b className="mono">{o.ocImportador}</b></div>}
                      <div className="ped-margin">
                        <div><span>Venta</span><b className="mono">{fmtMon(o.subtotal)}</b></div>
                        <div><span>Costo</span><b className="mono">{fmtMon(o.costoTotal)}</b></div>
                        <div className="ped-margin-net"><span>Margen ({o.margenPct}%)</span><b className="mono">+{fmtMon(o.margen)}</b></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---------------- COMPRAS A IMPORTADOR ---------------- */
function AdmCompras({ orders, onAdvance }) {
  // pedidos validados (listos para comprar) agrupados por importador
  const validados = orders.filter((o) => o.estado === "validado");
  const porImp = {};
  validados.forEach((o) => o.items.forEach((it) => {
    if (!porImp[it.importador]) porImp[it.importador] = { importador: it.importador, lines: [], total: 0, folios: new Set() };
    porImp[it.importador].lines.push({ ...it, folio: o.folio });
    porImp[it.importador].total += it.costoTotal;
    porImp[it.importador].folios.add(o.folio);
  }));
  const grupos = Object.values(porImp);

  return (
    <div className="adm-page">
      <div className="compras-intro">
        <Icon name="package" size={18} />
        <span>Pedidos con <b>pago validado</b>, agrupados por importador para generar la orden de compra. Al generarla, los pedidos pasan a <b>“Comprado”</b>.</span>
      </div>

      {grupos.length === 0 && (
        <div className="panel panel-empty-big">
          <Icon name="package" size={32} />
          <h3>Sin compras pendientes</h3>
          <p>Cuando valides un pago, el pedido aparecerá acá para comprarlo al importador.</p>
        </div>
      )}

      <div className="compras-grid">
        {grupos.map((g) => (
          <div className="oc" key={g.importador}>
            <div className="oc-head">
              <div>
                <span className="oc-imp"><Icon name="box" size={16} />{g.importador}</span>
                <small>{g.lines.length} líneas · {g.folios.size} pedidos</small>
              </div>
              <strong className="mono">{fmtMon(g.total)}</strong>
            </div>
            <div className="oc-lines">
              {g.lines.map((l, i) => (
                <div className="oc-line" key={i}>
                  <span className="mono oc-line-folio">{l.folio}</span>
                  <span className="oc-line-name">{l.name}</span>
                  <span className="mono oc-line-q">{l.cajas} cajas</span>
                  <span className="mono oc-line-cost">{fmtMon(l.costoTotal)}</span>
                </div>
              ))}
            </div>
            <div className="oc-foot">
              <span><Icon name="shield" size={14} />Costo total a pagar al importador</span>
              <Button size="sm" icon="package" onClick={() => g.lines.forEach((l) => onAdvance(l.folio, "comprado"))}>
                Generar orden de compra
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------------- CATÁLOGO & STOCK ---------------- */
function AdmCatalogo() {
  const [q, setQ] = useStateA("");
  const list = PRODUCTS.filter((p) => (p.name + p.sku + p.importador).toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="adm-page">
      <div className="adm-search">
        <Icon name="search" size={17} />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar producto, SKU o importador…" />
      </div>
      <div className="adm-table cat-table">
        <div className="adm-tr adm-thd cat-tr">
          <span>Producto</span><span>Importador</span><span className="ar">Costo u.</span><span className="ar">Venta u.</span><span className="ar">Margen</span><span className="ar">Stock</span><span>Estado</span>
        </div>
        {list.map((p) => {
          const costo = costoImportador(p);
          const venta = p.tiers[0].precioUnit;
          const mg = Math.round((1 - costo / venta) * 100);
          const cajas = Math.floor(p.stock / p.embalaje);
          let tone = "ok", txt = "OK";
          if (p.stock === 0) { tone = "out"; txt = "Sin stock"; }
          else if (p.stock <= p.embalaje * 4) { tone = "amber"; txt = "Bajo"; }
          return (
            <div className="adm-tr cat-tr" key={p.id}>
              <span className="cat-prod">
                <span className="cat-thumb" style={{ background: p.tint + "1a", color: p.tint }}><Icon name="box" size={15} /></span>
                <span className="cat-prod-txt"><b>{p.name}</b><small className="mono">{p.sku}</small></span>
              </span>
              <span className="td-imp">{p.importador}</span>
              <span className="ar mono">{fmtMon(costo)}</span>
              <span className="ar mono">{fmtMon(venta)}</span>
              <span className="ar mono td-margin">{mg}%</span>
              <span className="ar mono">{p.stock.toLocaleString("es-CL")}<small className="cat-cajas"> · {cajas} cajas</small></span>
              <span><span className={"adm-status adm-status-" + tone + " sm"}><span className="stockdot-dot" style={{ width: 7, height: 7, borderRadius: "50%", background: "currentColor" }} />{txt}</span></span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

Object.assign(window, { AdmPedidos, AdmCompras, AdmCatalogo });
