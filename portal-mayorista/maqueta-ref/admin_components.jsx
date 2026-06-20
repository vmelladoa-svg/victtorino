/* ============================================================
   Back-office — shell (sidebar + topbar) y componentes
   ============================================================ */
const { useState: useStateA, useMemo: useMemoA, useRef: useRefA } = React;

const NAV = [
  { id: "dashboard", label: "Resumen", icon: "grid" },
  { id: "pagos", label: "Pagos por validar", icon: "doc", badge: "pagos" },
  { id: "pedidos", label: "Pedidos", icon: "truck" },
  { id: "compras", label: "Compras a importador", icon: "package" },
  { id: "catalogo", label: "Catálogo & stock", icon: "box" },
];

function AdmSidebar({ view, onNav, counts, open, onClose }) {
  return (
    <>
      <div className={"adm-scrim" + (open ? " is-on" : "")} onClick={onClose} />
      <aside className={"adm-side" + (open ? " is-open" : "")}>
        <div className="adm-brand">
          <span className="adm-logo"><img src="assets/logo.png" alt="TGS" /></span>
          <span className="adm-brand-txt"><strong>Trade Global</strong><small>Back-office</small></span>
        </div>
        <nav className="adm-nav">
          {NAV.map((n) => (
            <button key={n.id} className={"adm-navi" + (view === n.id ? " is-on" : "")} onClick={() => { onNav(n.id); onClose(); }}>
              <Icon name={n.icon} size={19} />
              <span>{n.label}</span>
              {n.badge && counts[n.badge] > 0 && <span className="adm-navi-badge mono">{counts[n.badge]}</span>}
            </button>
          ))}
        </nav>
        <div className="adm-side-foot">
          <a href="Portal Mayorista.html" className="adm-side-link"><Icon name="logout" size={17} />Ir a la tienda</a>
          <div className="adm-side-user">
            <span className="adm-side-avatar">JM</span>
            <span><strong>Juan Méndez</strong><small>Operaciones</small></span>
          </div>
        </div>
      </aside>
    </>
  );
}

function AdmTopbar({ title, sub, onMenu, action }) {
  return (
    <header className="adm-top">
      <button className="adm-burger" onClick={onMenu} aria-label="Menú"><Icon name="filter" size={20} /></button>
      <div className="adm-top-txt">
        <h1>{title}</h1>
        {sub && <p>{sub}</p>}
      </div>
      {action}
    </header>
  );
}

/* KPI card */
function StatCard({ label, value, hint, icon, tone = "brand", trend }) {
  return (
    <div className={"stat stat-" + tone}>
      <div className="stat-ico"><Icon name={icon} size={20} /></div>
      <div className="stat-body">
        <span className="stat-label">{label}</span>
        <strong className="stat-value mono">{value}</strong>
        {hint && <span className="stat-hint">{trend && <em className={trend > 0 ? "up" : "down"}>{trend > 0 ? "▲" : "▼"} {Math.abs(trend)}%</em>} {hint}</span>}
      </div>
    </div>
  );
}

/* Estado pill admin */
function AdmStatus({ id, small }) {
  const e = admEstado(id);
  return <span className={"adm-status adm-status-" + e.tone + (small ? " sm" : "")}><Icon name={e.icon} size={small ? 12 : 14} stroke={2} />{e.label}</span>;
}

/* Pipeline mini (puntos de progreso) */
function Pipeline({ id }) {
  const idx = admIndex(id);
  return (
    <div className="pipe">
      {ADM_ESTADOS.map((e, i) => (
        <div key={e.id} className={"pipe-seg" + (i <= idx ? " is-on" : "")} title={e.label}>
          <span className="pipe-dot">{i < idx ? <Icon name="check" size={10} stroke={3} /> : i === idx ? <span className="pipe-now" /> : null}</span>
          {i < ADM_ESTADOS.length - 1 && <span className="pipe-bar" />}
        </div>
      ))}
    </div>
  );
}

/* Modal genérico */
function Modal({ title, onClose, children, wide }) {
  return (
    <div className="modal-scrim" onClick={onClose}>
      <div className={"modal" + (wide ? " modal-wide" : "")} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{title}</h3>
          <button onClick={onClose} aria-label="Cerrar"><Icon name="x" size={18} /></button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

Object.assign(window, { NAV, AdmSidebar, AdmTopbar, StatCard, AdmStatus, Pipeline, Modal });
