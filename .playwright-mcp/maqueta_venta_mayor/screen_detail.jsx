/* ============================================================
   Pantalla: Detalle de producto
   ============================================================ */
function ProductDetail({ prod, onBack, onAdd, onOpen }) {
  const maxCajas = Math.floor(prod.stock / prod.embalaje);
  const [cajas, setCajas] = useState(1);
  const tier = tierPara(prod, cajas);
  const pu = tier.precioUnit;
  const unidades = cajas * prod.embalaje;
  const total = pu * unidades;
  const ahorro = (prod.tiers[0].precioUnit - pu) * unidades;
  const sinStock = prod.stock === 0;

  const relacionados = PRODUCTS.filter((p) => p.cat === prod.cat && p.id !== prod.id).slice(0, 4);

  return (
    <div className="pdp">
      <button className="back" onClick={onBack}><Icon name="chevleft" size={16} />Volver al catálogo</button>

      <div className="pdp-grid">
        <div className="pdp-media">
          <ProductImage prod={prod} h={420} label="product shot · vista principal" />
          <div className="pdp-thumbs">
            {["frente", "detalle", "embalaje", "uso"].map((l, i) => (
              <div key={i} className={"pdp-thumb" + (i === 0 ? " is-on" : "")}>
                <ProductImage prod={prod} h={72} label={l} />
              </div>
            ))}
          </div>
        </div>

        <div className="pdp-info">
          <div className="pdp-tags">
            {prod.tags.map((t) => <Badge key={t} tone={t === "Nuevo" ? "brand" : "amber"} icon={t === "Más vendido" ? "star" : "bolt"}>{t}</Badge>)}
            <span className="pcard-sku mono">{prod.sku}</span>
          </div>
          <h1>{prod.name}</h1>
          <StockDot prod={prod} />
          <p className="pdp-desc">{prod.desc}</p>

          <div className="pdp-importer">
            <Icon name="shield" size={16} />
            <span>Importado por <b>{prod.importador}</b> · stock gestionado por Trade Global</span>
          </div>

          {/* Tabla de precios por volumen */}
          <div className="vol">
            <div className="vol-head">
              <Icon name="bolt" size={15} /><span>Precio por volumen (unitario)</span>
            </div>
            <div className="vol-tiers">
              {prod.tiers.map((t, i) => {
                const active = tier.minCajas === t.minCajas;
                return (
                  <div key={i} className={"vol-tier" + (active ? " is-on" : "")}>
                    <small>{t.minCajas}+ {t.minCajas === 1 ? "caja" : "cajas"}</small>
                    <strong className="mono">{CLP(t.precioUnit)}</strong>
                    {i > 0 && <span className="vol-save">−{Math.round((1 - t.precioUnit / prod.tiers[0].precioUnit) * 100)}%</span>}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selector de cajas */}
          <div className="pdp-buy">
            <div className="pdp-buy-row">
              <div className="pdp-buy-min">
                <span className="lbl">Cantidad</span>
                <Badge tone="neutral" icon="box">Mínimo 1 caja · {prod.embalaje} u.</Badge>
              </div>
              <CajaStepper cajas={cajas} setCajas={setCajas} max={Math.max(1, maxCajas)} size="lg" />
            </div>
            <div className="pdp-buy-calc">
              <div className="calc-line">
                <span><span className="mono">{cajas}</span> cajas × <span className="mono">{prod.embalaje}</span> = <b className="mono">{unidades}</b> unidades</span>
                <span className="mono">{CLP(pu)} c/u</span>
              </div>
              {ahorro > 0 && (
                <div className="calc-line calc-save"><span>Ahorro por volumen</span><span className="mono">−{CLP(ahorro)}</span></div>
              )}
              <div className="calc-total">
                <span>Total productos</span>
                <strong className="mono">{CLP(total)}</strong>
              </div>
            </div>
            <Button size="lg" full icon="cart" disabled={sinStock} onClick={() => onAdd(prod, cajas)}>
              {sinStock ? "Sin stock disponible" : "Agregar a la cotización"}
            </Button>
            <div className="pdp-buy-notes">
              <span><Icon name="truck" size={15} />Despacho a todo Chile</span>
              <span><Icon name="clock" size={15} />Validación de pago en 24–48h</span>
            </div>
          </div>
        </div>
      </div>

      {relacionados.length > 0 && (
        <section className="pdp-rel">
          <h2>Del mismo rubro</h2>
          <div className="pgrid pgrid-dense">
            {relacionados.map((p) => (
              <ProductCard key={p.id} prod={p} onOpen={onOpen} onQuickAdd={(pp) => onAdd(pp, 1)} dense />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

window.ProductDetail = ProductDetail;
