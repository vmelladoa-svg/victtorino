/* ============================================================
   Pantallas: Carrito · Checkout (despacho + transferencia + comprobante)
   ============================================================ */

/* ---------- helpers de carrito ---------- */
function lineTotales(item) {
  const prod = PRODUCTS.find((p) => p.id === item.id);
  const pu = precioUnit(prod, item.cajas);
  const unidades = item.cajas * prod.embalaje;
  return { prod, pu, unidades, total: pu * unidades };
}
function resumenCarrito(cart) {
  let subtotal = 0, cajas = 0, unidades = 0;
  cart.forEach((it) => { const l = lineTotales(it); subtotal += l.total; cajas += it.cajas; unidades += l.unidades; });
  return { subtotal, cajas, unidades };
}

/* ---------------- CARRITO ---------------- */
function CartScreen({ cart, setCajas, removeItem, onCheckout, onNav }) {
  const { subtotal, cajas, unidades } = resumenCarrito(cart);
  if (cart.length === 0) {
    return (
      <div className="empty big">
        <Icon name="cart" size={34} />
        <h2>Tu cotización está vacía</h2>
        <p>Agregá productos del catálogo para armar tu pedido mayorista.</p>
        <Button icon="grid" onClick={() => onNav("catalog")}>Ir al catálogo</Button>
      </div>
    );
  }
  return (
    <div className="cart">
      <div className="page-head">
        <button className="back" onClick={() => onNav("catalog")}><Icon name="chevleft" size={16} />Seguir comprando</button>
        <h1>Carrito / Cotización</h1>
      </div>
      <div className="cart-grid">
        <div className="cart-items">
          {cart.map((it) => {
            const { prod, pu, unidades, total } = lineTotales(it);
            const maxCajas = Math.max(1, Math.floor(prod.stock / prod.embalaje));
            return (
              <div className="citem" key={it.id}>
                <div className="citem-img"><ProductImage prod={prod} h={92} label="" /></div>
                <div className="citem-info">
                  <span className="pcard-sku mono">{prod.sku}</span>
                  <h3>{prod.name}</h3>
                  <Badge tone="neutral" icon="box">Embalaje {prod.embalaje} u.</Badge>
                  <span className="citem-unit mono">{CLP(pu)} <small>c/u</small></span>
                </div>
                <div className="citem-qty">
                  <CajaStepper cajas={it.cajas} setCajas={(v) => setCajas(it.id, v)} max={maxCajas} />
                  <small><span className="mono">{unidades}</span> unidades</small>
                </div>
                <div className="citem-total">
                  <strong className="mono">{CLP(total)}</strong>
                  <button className="citem-del" onClick={() => removeItem(it.id)}><Icon name="trash" size={16} />Quitar</button>
                </div>
              </div>
            );
          })}
        </div>
        <aside className="summary">
          <h3>Resumen</h3>
          <div className="sum-line"><span>Productos ({cart.length})</span><span className="mono">{CLP(subtotal)}</span></div>
          <div className="sum-line"><span>Total cajas</span><span className="mono">{cajas}</span></div>
          <div className="sum-line"><span>Total unidades</span><span className="mono">{unidades}</span></div>
          <div className="sum-note"><Icon name="truck" size={15} />El costo de despacho se calcula en el siguiente paso según tu región.</div>
          <div className="sum-total"><span>Subtotal</span><strong className="mono">{CLP(subtotal)}</strong></div>
          <Button size="lg" full iconRight="chevright" onClick={onCheckout}>Continuar al pago</Button>
          <span className="sum-secure"><Icon name="shield" size={14} />Pago por transferencia · validación 24–48h</span>
        </aside>
      </div>
    </div>
  );
}

/* ---------------- pasos del checkout ---------------- */
function Steps({ step }) {
  const items = [
    { n: 1, label: "Despacho" },
    { n: 2, label: "Pago" },
    { n: 3, label: "Listo" },
  ];
  return (
    <div className="steps">
      {items.map((it, i) => (
        <React.Fragment key={it.n}>
          <div className={"step" + (step === it.n ? " is-on" : "") + (step > it.n ? " is-done" : "")}>
            <span className="step-n">{step > it.n ? <Icon name="check" size={15} /> : it.n}</span>
            <span className="step-l">{it.label}</span>
          </div>
          {i < items.length - 1 && <span className={"step-bar" + (step > it.n ? " is-done" : "")} />}
        </React.Fragment>
      ))}
    </div>
  );
}

/* ---------------- CHECKOUT ---------------- */
function CheckoutScreen({ cart, user, onPlaceOrder, onNav }) {
  const { subtotal, cajas, unidades } = resumenCarrito(cart);
  const [step, setStep] = useState(1);
  const [region, setRegion] = useState("rm");
  const [dir, setDir] = useState("Av. Matta 1234, bodega 5, Santiago");
  const [contacto, setContacto] = useState(user.nombre);
  const [fono, setFono] = useState("+56 9 8765 4321");
  const [archivo, setArchivo] = useState(null);
  const [copiado, setCopiado] = useState("");
  const fileRef = useRef(null);

  const reg = REGIONES.find((r) => r.id === region);
  const despacho = reg.costoCaja * cajas;
  const total = subtotal + despacho;
  const folio = useMemo(() => "TGS-" + Math.floor(100000 + Math.random() * 899999), []);

  const copy = (txt, key) => {
    navigator.clipboard?.writeText(txt);
    setCopiado(key); setTimeout(() => setCopiado(""), 1400);
  };

  return (
    <div className="checkout">
      <div className="page-head">
        <button className="back" onClick={() => (step === 1 ? onNav("cart") : setStep(step - 1))}>
          <Icon name="chevleft" size={16} />{step === 1 ? "Volver al carrito" : "Atrás"}
        </button>
        <h1>Finalizar pedido</h1>
      </div>
      <Steps step={step} />

      <div className="checkout-grid">
        <div className="checkout-main">
          {step === 1 && (
            <div className="card form-card">
              <h3><Icon name="truck" size={18} />Datos de despacho</h3>
              <div className="form-2">
                <label className="field"><span>Razón social</span><input value={user.empresa} readOnly /></label>
                <label className="field"><span>RUT empresa</span><input value={user.rut} readOnly /></label>
                <label className="field"><span>Persona de contacto</span><input value={contacto} onChange={(e) => setContacto(e.target.value)} /></label>
                <label className="field"><span>Teléfono</span><input value={fono} onChange={(e) => setFono(e.target.value)} /></label>
              </div>
              <label className="field"><span>Región de destino</span>
                <div className="select-wrap">
                  <Icon name="pin" size={16} />
                  <select value={region} onChange={(e) => setRegion(e.target.value)}>
                    {REGIONES.map((r) => <option key={r.id} value={r.id}>{r.label} — despacho {r.dias} días hábiles</option>)}
                  </select>
                </div>
              </label>
              <label className="field"><span>Dirección de entrega</span><input value={dir} onChange={(e) => setDir(e.target.value)} /></label>
              <div className="ship-est">
                <Icon name="clock" size={16} />
                <span>Entrega estimada a <b>{reg.label}</b>: <b>{reg.dias} días hábiles</b> tras confirmar el pago.</span>
              </div>
              <Button size="lg" full iconRight="chevright" onClick={() => setStep(2)}>Continuar al pago</Button>
            </div>
          )}

          {step === 2 && (
            <div className="card form-card">
              <h3><Icon name="doc" size={18} />Pago por transferencia</h3>
              <p className="muted">Transferí el total y enviá el comprobante. Validamos en 24–48h hábiles y ahí coordinamos el despacho.</p>
              <div className="bank">
                {[
                  ["Titular", BANCO.titular],
                  ["RUT", BANCO.rut],
                  ["Banco", BANCO.banco],
                  ["Tipo de cuenta", BANCO.tipo],
                  ["N° de cuenta", BANCO.numero],
                  ["Correo de comprobantes", BANCO.email],
                ].map(([k, v]) => (
                  <div className="bank-row" key={k}>
                    <span>{k}</span>
                    <b className={k === "RUT" || k.includes("cuenta") ? "mono" : ""}>{v}</b>
                    <button onClick={() => copy(v, k)}>{copiado === k ? <Icon name="check" size={15} /> : "Copiar"}</button>
                  </div>
                ))}
                <div className="bank-amount">
                  <span>Monto exacto a transferir</span>
                  <strong className="mono">{CLP(total)}</strong>
                  <button onClick={() => copy(String(total), "amount")}>{copiado === "amount" ? <Icon name="check" size={15} /> : "Copiar"}</button>
                </div>
                <div className="bank-folio"><Icon name="bolt" size={14} />Indicá el folio <b className="mono">{folio}</b> en el detalle de la transferencia.</div>
              </div>

              <div className="upload" onClick={() => fileRef.current?.click()}>
                <input ref={fileRef} type="file" hidden accept="image/*,application/pdf"
                  onChange={(e) => setArchivo(e.target.files[0]?.name || null)} />
                {archivo ? (
                  <div className="upload-done"><Icon name="check" size={20} /><div><b>{archivo}</b><small>Comprobante listo para enviar</small></div></div>
                ) : (
                  <div className="upload-empty"><Icon name="upload" size={24} /><div><b>Adjuntá tu comprobante</b><small>JPG, PNG o PDF · se envía a {BANCO.email}</small></div></div>
                )}
              </div>

              <Button size="lg" full icon="check" disabled={!archivo}
                onClick={() => { onPlaceOrder({ folio, region, reg, despacho, total, comprobante: archivo }); setStep(3); }}>
                Ya transferí · enviar comprobante
              </Button>
              {!archivo && <span className="upload-hint">Adjuntá el comprobante para continuar.</span>}
            </div>
          )}

          {step === 3 && (
            <div className="card done-card">
              <div className="done-ico"><Icon name="check" size={34} /></div>
              <h2>¡Pedido recibido!</h2>
              <p>Tu pedido <b className="mono">{folio}</b> quedó en <b>validación de pago</b>. Te avisaremos por correo cuando confirmemos la transferencia y comencemos la preparación.</p>
              <div className="done-next">
                <div><span className="mono">1</span>Validamos tu comprobante (24–48h)</div>
                <div><span className="mono">2</span>Compramos al importador y preparamos</div>
                <div><span className="mono">3</span>Despachamos a {reg.label}</div>
              </div>
              <div className="done-actions">
                <Button icon="truck" onClick={() => onNav("orders")}>Ver mis pedidos</Button>
                <Button variant="ghost" icon="grid" onClick={() => onNav("catalog")}>Seguir comprando</Button>
              </div>
            </div>
          )}
        </div>

        {step < 3 && (
          <aside className="summary">
            <h3>Tu pedido</h3>
            <div className="sum-mini">
              {cart.map((it) => { const { prod, total } = lineTotales(it); return (
                <div className="sum-mini-row" key={it.id}>
                  <span>{it.cajas}× {prod.name}</span><span className="mono">{CLP(total)}</span>
                </div>
              ); })}
            </div>
            <div className="sum-line"><span>Subtotal productos</span><span className="mono">{CLP(subtotal)}</span></div>
            <div className="sum-line"><span>Despacho ({cajas} cajas · {reg.label})</span><span className="mono">{CLP(despacho)}</span></div>
            <div className="sum-total"><span>Total a transferir</span><strong className="mono">{CLP(total)}</strong></div>
            <span className="sum-secure"><Icon name="shield" size={14} />Folio {folio}</span>
          </aside>
        )}
      </div>
    </div>
  );
}

window.lineTotales = lineTotales;
window.resumenCarrito = resumenCarrito;
Object.assign(window, { CartScreen, CheckoutScreen });
