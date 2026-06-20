/* ============================================================
   Back-office — App principal (routing + estado)
   ============================================================ */

const TITULOS = {
  dashboard: { t: "Resumen", s: "Estado general de la operación" },
  pagos: { t: "Pagos por validar", s: "Revisá comprobantes y confirmá transferencias" },
  pedidos: { t: "Pedidos", s: "Seguimiento y avance de cada pedido" },
  compras: { t: "Compras a importador", s: "Generá órdenes de compra agrupadas" },
  catalogo: { t: "Catálogo & stock", s: "Costos, márgenes y disponibilidad" },
};

function AdminApp() {
  const [view, setView] = useStateA("dashboard");
  const [orders, setOrders] = useStateA(() => ADM_ORDERS.map((o) => ({ ...o })));
  const [openPago, setOpenPago] = useStateA(null);
  const [sideOpen, setSideOpen] = useStateA(false);
  const [toast, setToast] = useStateA(null);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 2200); };

  const setEstado = (folio, estado, extra = {}) =>
    setOrders((os) => os.map((o) => o.folio === folio ? { ...o, estado, ...extra } : o));

  const validar = (folio) => { setEstado(folio, "validado", { comprobante: { ...orders.find(o=>o.folio===folio).comprobante, ref: "Validado por J. Méndez" } }); showToast("Pago validado · " + folio); };
  const rechazar = (folio) => { setOrders((os) => os.filter((o) => o.folio !== folio)); showToast("Pago rechazado · " + folio); };

  const advance = (folio, to) => {
    const extra = {};
    if (to === "comprado") extra.ocImportador = "OC-IMP-" + Math.floor(2300 + Math.random() * 99);
    if (to === "despachado") { extra.transportista = "Starken"; extra.tracking = "STK-" + Math.floor(10000000 + Math.random() * 89999999); }
    setEstado(folio, to, extra);
    const labels = { comprado: "OC generada · ", despachado: "Despachado · ", entregado: "Entregado · " };
    showToast((labels[to] || "") + folio);
  };

  const counts = { pagos: orders.filter((o) => o.estado === "por_validar").length };
  const ti = TITULOS[view];

  return (
    <div className="adm">
      <AdmSidebar view={view} onNav={setView} counts={counts} open={sideOpen} onClose={() => setSideOpen(false)} />
      <div className="adm-main">
        <AdmTopbar title={ti.t} sub={ti.s} onMenu={() => setSideOpen(true)}
          action={view === "dashboard" && (
            <a href="Portal Mayorista.html" className="adm-top-cta"><Icon name="bolt" size={16} />Ver tienda</a>
          )} />
        <div className="adm-scroll">
          {view === "dashboard" && <AdmDashboard orders={orders} onNav={setView} onOpenPago={(o) => { setView("pagos"); setOpenPago(o); }} />}
          {view === "pagos" && <AdmPagos orders={orders} onValidar={validar} onRechazar={rechazar} openPago={openPago} setOpenPago={setOpenPago} />}
          {view === "pedidos" && <AdmPedidos orders={orders} onAdvance={advance} onNav={setView} />}
          {view === "compras" && <AdmCompras orders={orders} onAdvance={advance} />}
          {view === "catalogo" && <AdmCatalogo />}
        </div>
      </div>
      {toast && <div className="toast"><Icon name="check" size={17} />{toast}</div>}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<AdminApp />);
