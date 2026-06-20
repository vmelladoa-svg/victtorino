/* ============================================================
   Pantallas: Header · Login · Catálogo · Detalle de producto
   ============================================================ */

/* ---------------- HEADER ---------------- */
function Header({ user, cartCount, onNav, onSearch, query, view }) {
  const [openMenu, setOpenMenu] = useState(false);
  return (
    <header className="hdr">
      <div className="hdr-main">
        <Logo onClick={() => onNav("catalog")} />
        <div className="hdr-search">
          <Icon name="search" size={18} />
          <input
            value={query}
            onChange={(e) => onSearch(e.target.value)}
            onFocus={() => onNav("catalog")}
            placeholder="Buscar productos, SKU o categoría…"
          />
        </div>
        <div className="hdr-actions">
          <button className="hdr-pedidos" onClick={() => onNav("orders")}>
            <Icon name="truck" size={19} />
            <span>Mis pedidos</span>
          </button>
          <button className="hdr-cart" onClick={() => onNav("cart")}>
            <Icon name="cart" size={20} />
            {cartCount > 0 && <span className="hdr-cart-badge mono">{cartCount}</span>}
          </button>
          <button className="hdr-user" onClick={() => setOpenMenu((o) => !o)}>
            <span className="hdr-avatar">{user.empresa.slice(0, 1)}</span>
            <span className="hdr-user-txt">
              <strong>{user.empresa}</strong>
              <small>{user.nombre}</small>
            </span>
            <Icon name="chevdown" size={15} />
          </button>
          {openMenu && (
            <div className="hdr-menu" onMouseLeave={() => setOpenMenu(false)}>
              <div className="hdr-menu-head">
                <strong>{user.empresa}</strong>
                <small>{user.email}</small>
                <Badge tone="ok" icon="shield">Cuenta verificada</Badge>
              </div>
              <button onClick={() => { onNav("orders"); setOpenMenu(false); }}><Icon name="truck" size={16} />Mis pedidos</button>
              <button onClick={() => { onNav("cart"); setOpenMenu(false); }}><Icon name="cart" size={16} />Carrito / Cotización</button>
              <a href="Panel Admin.html" className="hdr-menu-admin"><Icon name="shield" size={16} />Panel de administrador</a>
              <button onClick={() => { onNav("login"); setOpenMenu(false); }} className="danger"><Icon name="logout" size={16} />Cerrar sesión</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

/* ---------------- LOGIN ---------------- */
function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("compras@comercialandes.cl");
  const [pass, setPass] = useState("••••••••");
  return (
    <div className="login">
      <div className="login-aside">
        <Logo />
        <div className="login-aside-body">
          <Badge tone="brand" icon="bolt">Portal mayorista B2B</Badge>
          <h1>Compra al por mayor, despachamos a todo Chile.</h1>
          <p>Catálogo multi-rubro con stock en tiempo real, precios por volumen y despacho gestionado. Pagás por transferencia, validamos el comprobante y coordinamos la entrega.</p>
          <ul className="login-feats">
            <li><Icon name="bolt" size={18} /><span>Stock real, sin sobreventa</span></li>
            <li><Icon name="package" size={18} /><span>Precio por volumen según cajas</span></li>
            <li><Icon name="truck" size={18} /><span>Despacho a las 16 regiones</span></li>
          </ul>
        </div>
        <span className="login-foot">Trade Global Solutions SpA · RUT 77.412.905-K</span>
      </div>
      <div className="login-form-wrap">
        <form className="login-form" onSubmit={(e) => { e.preventDefault(); onLogin(); }}>
          <h2>Ingresá a tu cuenta</h2>
          <p className="login-sub">Acceso exclusivo para comerciantes registrados.</p>
          <label className="field">
            <span>Correo de la empresa</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="field">
            <span>Contraseña</span>
            <input type="password" value={pass} onChange={(e) => setPass(e.target.value)} />
          </label>
          <div className="login-row">
            <label className="check"><input type="checkbox" defaultChecked /><span>Recordarme</span></label>
            <a href="#" onClick={(e) => e.preventDefault()}>¿Olvidaste tu clave?</a>
          </div>
          <Button type="submit" full size="lg" iconRight="chevright">Entrar al catálogo</Button>
          <div className="login-divider"><span>¿Aún no tenés cuenta?</span></div>
          <Button variant="ghost" full onClick={onLogin}>Solicitar acceso mayorista</Button>
        </form>
      </div>
    </div>
  );
}

/* ---------------- TARJETA DE PRODUCTO ---------------- */
function ProductCard({ prod, onOpen, onQuickAdd, dense }) {
  const t0 = prod.tiers[0].precioUnit;
  const tMin = prod.tiers[prod.tiers.length - 1].precioUnit;
  const sinStock = prod.stock === 0;
  return (
    <article className={"pcard" + (sinStock ? " is-out" : "")} onClick={() => onOpen(prod)}>
      <div className="pcard-media">
        <ProductImage prod={prod} h={dense ? 130 : 168} />
        <div className="pcard-tags">
          {prod.tags.map((t) => <Badge key={t} tone={t === "Nuevo" ? "brand" : "amber"} icon={t === "Más vendido" ? "star" : "bolt"}>{t}</Badge>)}
          {sinStock && <Badge tone="out">Sin stock</Badge>}
        </div>
      </div>
      <div className="pcard-body">
        <span className="pcard-sku mono">{prod.sku}</span>
        <h3>{prod.name}</h3>
        <StockDot prod={prod} />
        <div className="pcard-price">
          <div>
            <strong className="mono">{CLP(t0)}</strong>
            <small>/ unidad</small>
          </div>
          <span className="pcard-vol">desde <b className="mono">{CLP(tMin)}</b> por volumen</span>
        </div>
        <div className="pcard-meta">
          <Badge tone="neutral" icon="box">Embalaje {prod.embalaje} u.</Badge>
        </div>
        <div className="pcard-actions" onClick={(e) => e.stopPropagation()}>
          <Button variant="soft" size="sm" full icon="cart" disabled={sinStock} onClick={() => onQuickAdd(prod)}>
            {sinStock ? "No disponible" : "Agregar caja"}
          </Button>
        </div>
      </div>
    </article>
  );
}

/* ---------------- CATÁLOGO ---------------- */
function CatalogScreen({ onOpen, onQuickAdd, query, cardStyle, showHero }) {
  const [cat, setCat] = useState("all");
  const [sort, setSort] = useState("rel");

  const list = useMemo(() => {
    let l = PRODUCTS.filter((p) => cat === "all" || p.cat === cat);
    if (query.trim()) {
      const q = query.toLowerCase();
      l = l.filter((p) => (p.name + " " + p.sku + " " + p.cat).toLowerCase().includes(q));
    }
    if (sort === "priceup") l = [...l].sort((a, b) => a.tiers[0].precioUnit - b.tiers[0].precioUnit);
    if (sort === "pricedown") l = [...l].sort((a, b) => b.tiers[0].precioUnit - a.tiers[0].precioUnit);
    if (sort === "stock") l = [...l].sort((a, b) => b.stock - a.stock);
    return l;
  }, [cat, query, sort]);

  return (
    <div className="catalog">
      {!query && showHero && (
        <section className="hero">
          <div className="hero-txt">
            <Badge tone="brand" icon="bolt">Reposición semanal · +120 SKUs</Badge>
            <h1>Tu proveedor mayorista,<br /><em>sin intermediarios.</em></h1>
            <p>Importamos, mantenemos stock y despachamos a todo Chile. Comprá por caja, pagá por transferencia y nosotros gestionamos el resto.</p>
            <div className="hero-stats">
              <div><strong className="mono">16</strong><small>regiones con despacho</small></div>
              <div><strong className="mono">24–48h</strong><small>validación de pago</small></div>
              <div><strong className="mono">100%</strong><small>stock garantizado</small></div>
            </div>
          </div>
          <div className="hero-card">
            <ProductImage prod={PRODUCTS[0]} h={230} label="banner / campaña destacada" />
          </div>
        </section>
      )}

      <div className="cat-bar">
        <div className="cat-chips">
          {CATEGORIES.map((c) => (
            <button key={c.id} className={"chip" + (cat === c.id ? " is-on" : "")} onClick={() => setCat(c.id)}>
              <Icon name={c.icon} size={16} />{c.label}
            </button>
          ))}
        </div>
        <div className="cat-sort">
          <Icon name="filter" size={16} />
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="rel">Relevancia</option>
            <option value="priceup">Precio: menor a mayor</option>
            <option value="pricedown">Precio: mayor a menor</option>
            <option value="stock">Mayor stock</option>
          </select>
        </div>
      </div>

      <div className="cat-head">
        <h2>{query ? `Resultados para "${query}"` : CATEGORIES.find((c) => c.id === cat).label}</h2>
        <span className="mono">{list.length} productos</span>
      </div>

      <div className={"pgrid" + (cardStyle === "dense" ? " pgrid-dense" : "")}>
        {list.map((p) => (
          <ProductCard key={p.id} prod={p} onOpen={onOpen} onQuickAdd={onQuickAdd} dense={cardStyle === "dense"} />
        ))}
      </div>
      {list.length === 0 && <div className="empty"><Icon name="search" size={28} /><p>No encontramos productos para tu búsqueda.</p></div>}
    </div>
  );
}

Object.assign(window, { Header, LoginScreen, ProductCard, CatalogScreen });
