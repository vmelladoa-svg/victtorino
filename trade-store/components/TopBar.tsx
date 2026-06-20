"use client";

import { useStore } from "@/lib/store-context";

export function TopBar() {
  const { user, openAccount, openTracking } = useStore();
  return (
    <div className="topbar">
      <div className="wrap topbar-in">
        <div className="topbar-msgs">
          <span className="topbar-msg">
            <b>Despacho express</b> en RM: 24 horas
          </span>
          <span className="topbar-msg">
            Hasta <b>12 cuotas sin interés</b>
          </span>
          <span className="topbar-msg">
            Garantía <b>6 meses</b> en todo
          </span>
        </div>
        <div className="topbar-links">
          <button className="topbar-btn" onClick={openTracking}>
            Seguir mi pedido
          </button>
          <button className="topbar-btn" onClick={openAccount}>
            {user ? `Hola, ${user.name.split(" ")[0]}` : "Mi cuenta"}
          </button>
        </div>
      </div>
    </div>
  );
}
