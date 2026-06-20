/* ============================================================
   App principal — routing, estado y Tweaks
   ============================================================ */

const USER = {
  empresa: "Comercial Andes Ltda.",
  nombre: "María Fernanda Rojas",
  email: "compras@comercialandes.cl",
  rut: "76.998.221-4",
};

// Pedidos sembrados (para mostrar el seguimiento ya poblado)
function seedOrders() {
  const mk = (id, cajas) => { const p = PRODUCTS.find((x) => x.id === id); const pu = precioUnit(p, cajas); const u = cajas * p.embalaje; return { id, name: p.name, cajas, unidades: u, total: pu * u }; };
  const build = (o) => {
    o.cajas = o.items.reduce((s, i) => s + i.cajas, 0);
    o.total = o.items.reduce((s, i) => s + i.total, 0) + o.despacho;
    return o;
  };
  return [
    build({
      folio: "TGS-840192", fecha: "5 jun 2026", estado: "despacho",
      items: [mk("tec-01", 6), mk("bazar-01", 4)],
      despacho: 12000, reg: REGIONES[4], comprobante: "transferencia_bci.pdf",
      fechas: { validacion: "3 jun", confirmado: "4 jun" },
    }),
    build({
      folio: "TGS-829934", fecha: "2 jun 2026", estado: "entregado",
      items: [mk("textil-01", 8)],
      despacho: 9600, reg: REGIONES[0], comprobante: "comprobante_santander.jpg",
      fechas: { validacion: "1 jun", confirmado: "1 jun", despacho: "2 jun", entregado: "3 jun" },
    }),
    build({
      folio: "TGS-851077", fecha: "6 jun 2026", estado: "validacion",
      items: [mk("belleza-01", 3), mk("herr-02", 2)],
      despacho: 6000, reg: REGIONES[1], comprobante: "transf_estado.png",
      fechas: {},
    }),
  ];
}

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#0e7cc4",
  "radius": "soft",
  "cardStyle": "standard",
  "font": "jakarta",
  "showHero": true
}/*EDITMODE-END*/;

const RADIUS_MAP = { sharp: "4px", soft: "12px", round: "22px" };
const FONT_MAP = {
  jakarta: "'Plus Jakarta Sans', system-ui, sans-serif",
  space: "'Space Grotesk', system-ui, sans-serif",
  system: "system-ui, -apple-system, 'Segoe UI', sans-serif",
};

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [view, setView] = useState("login");
  const [prod, setProd] = useState(null);
  const [query, setQuery] = useState("");
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState(seedOrders);
  const [toast, setToast] = useState(null);

  const scrollTop = () => { const el = document.querySelector(".app-scroll"); if (el) el.scrollTop = 0; };
  const nav = (v) => { setView(v); setQuery(""); scrollTop(); };
  const openProd = (p) => { setProd(p); setView("detail"); scrollTop(); };

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 2200); };

  const addToCart = (p, cajas = 1) => {
    setCart((c) => {
      const ex = c.find((x) => x.id === p.id);
      const maxC = Math.max(1, Math.floor(p.stock / p.embalaje));
      if (ex) return c.map((x) => x.id === p.id ? { ...x, cajas: Math.min(maxC, x.cajas + cajas) } : x);
      return [...c, { id: p.id, cajas: Math.min(maxC, cajas) }];
    });
    showToast(`${cajas} ${cajas === 1 ? "caja agregada" : "cajas agregadas"} · ${p.name}`);
  };
  const setCajas = (id, v) => setCart((c) => c.map((x) => x.id === id ? { ...x, cajas: v } : x));
  const removeItem = (id) => setCart((c) => c.filter((x) => x.id !== id));

  const cartCount = cart.reduce((s, x) => s + x.cajas, 0);

  const placeOrder = (info) => {
    const items = cart.map((it) => { const l = lineTotales(it); return { id: it.id, name: l.prod.name, cajas: it.cajas, unidades: l.unidades, total: l.total }; });
    const { subtotal } = resumenCarrito(cart);
    const order = {
      folio: info.folio, fecha: "7 jun 2026", estado: "validacion",
      items, cajas: items.reduce((s, i) => s + i.cajas, 0),
      despacho: info.despacho, reg: info.reg, comprobante: info.comprobante,
      total: subtotal + info.despacho, fechas: {},
    };
    setOrders((o) => [order, ...o]);
    setCart([]);
  };

  const advance = (folio) => setOrders((os) => os.map((o) => {
    if (o.folio !== folio) return o;
    const i = ESTADOS.findIndex((e) => e.id === o.estado);
    const next = ESTADOS[Math.min(ESTADOS.length - 1, i + 1)];
    const fechas = { ...o.fechas, [next.id]: "hoy" };
    return { ...o, estado: next.id, fechas };
  }));

  const rootStyle = {
    "--brand": t.accent,
    "--radius": RADIUS_MAP[t.radius] || "12px",
    "--font": FONT_MAP[t.font] || FONT_MAP.jakarta,
  };

  const isLogin = view === "login";

  return (
    <div className="app" style={rootStyle}>
      {isLogin ? (
        <LoginScreen onLogin={() => nav("catalog")} />
      ) : (
        <>
          <Header user={USER} cartCount={cartCount} onNav={nav} onSearch={(q) => { setQuery(q); if (view !== "catalog") setView("catalog"); }} query={query} view={view} />
          <div className="app-scroll">
            <main className="app-main">
              {view === "catalog" && <CatalogScreen onOpen={openProd} onQuickAdd={(p) => addToCart(p, 1)} query={query} cardStyle={t.cardStyle} showHero={t.showHero} />}
              {view === "detail" && prod && <ProductDetail prod={prod} onBack={() => nav("catalog")} onAdd={(p, c) => addToCart(p, c)} onOpen={openProd} />}
              {view === "cart" && <CartScreen cart={cart} setCajas={setCajas} removeItem={removeItem} onCheckout={() => nav("checkout")} onNav={nav} />}
              {view === "checkout" && (cart.length === 0
                ? <CartScreen cart={cart} setCajas={setCajas} removeItem={removeItem} onCheckout={() => {}} onNav={nav} />
                : <CheckoutScreen cart={cart} user={USER} onPlaceOrder={placeOrder} onNav={nav} />)}
              {view === "orders" && <OrdersScreen orders={orders} onNav={nav} advance={advance} />}
            </main>
            <footer className="app-foot">
              <Logo />
              <span>© 2026 Trade Global Solutions SpA · Venta mayorista · Despacho a todo Chile</span>
              <span className="mono">pagos@tradeglobal.cl</span>
            </footer>
          </div>
        </>
      )}

      {toast && <div className="toast"><Icon name="check" size={17} />{toast}</div>}

      <TweaksPanel>
        <TweakSection label="Marca" />
        <TweakColor label="Color de acento" value={t.accent}
          options={["#0e7cc4", "#16a6db", "#1e2a86", "#0f766e", "#0e8a55"]}
          onChange={(v) => setTweak("accent", v)} />
        <TweakRadio label="Tipografía" value={t.font}
          options={["jakarta", "space", "system"]}
          onChange={(v) => setTweak("font", v)} />
        <TweakSection label="Estilo visual" />
        <TweakRadio label="Bordes" value={t.radius}
          options={["sharp", "soft", "round"]}
          onChange={(v) => setTweak("radius", v)} />
        <TweakRadio label="Tarjetas" value={t.cardStyle}
          options={["standard", "dense"]}
          onChange={(v) => setTweak("cardStyle", v)} />
        <TweakToggle label="Mostrar hero" value={t.showHero}
          onChange={(v) => setTweak("showHero", v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
