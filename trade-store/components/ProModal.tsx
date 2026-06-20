"use client";

import { useEffect, useState } from "react";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

const RUBROS = [
  "Gasfitería e instalaciones sanitarias",
  "Construcción y remodelación",
  "Electricidad",
  "Mantención de edificios / condominios",
  "Otro oficio técnico",
];

export function ProModal() {
  const { proModalOpen, closeProModal, registerPro } = useStore();
  const [form, setForm] = useState({ nombre: "", rut: "", telefono: "", rubro: RUBROS[0] });
  const [sent, setSent] = useState(false);
  useEffect(() => {
    if (proModalOpen) {
      setSent(false);
      setForm({ nombre: "", rut: "", telefono: "", rubro: RUBROS[0] });
    }
  }, [proModalOpen]);
  if (!proModalOpen) return null;
  const set = (k: keyof typeof form, v: string) => setForm({ ...form, [k]: v });
  const can = form.nombre.trim() && form.rut.trim() && form.telefono.trim();

  return (
    <div>
      <div className="overlay" onClick={closeProModal} />
      <div
        className="modal"
        onClick={(e) => {
          if (e.target === e.currentTarget) closeProModal();
        }}
      >
        <div className="modal-card" style={{ maxWidth: 480 }}>
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={closeProModal}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div style={{ padding: "36px 36px 32px" }}>
            {!sent ? (
              <div>
                <h3 style={{ fontSize: 22, marginBottom: 6 }}>Registro Trade Pro</h3>
                <p style={{ color: "var(--ink-soft)", fontSize: 14.5, marginBottom: 20 }}>
                  Cuéntanos de tu oficio. Validamos tus datos y activamos tu descuento Pro Cobre
                  (5%).
                </p>
                <div style={{ display: "grid", gap: 14 }}>
                  <div className="field">
                    <label>Nombre completo</label>
                    <input
                      value={form.nombre}
                      onChange={(e) => set("nombre", e.target.value)}
                      placeholder="Ej: Juan Pérez"
                    />
                  </div>
                  <div className="field-row">
                    <div className="field">
                      <label>RUT</label>
                      <input
                        value={form.rut}
                        onChange={(e) => set("rut", e.target.value)}
                        placeholder="12.345.678-9"
                      />
                    </div>
                    <div className="field">
                      <label>Teléfono</label>
                      <input
                        value={form.telefono}
                        onChange={(e) => set("telefono", e.target.value)}
                        placeholder="+56 9 …"
                      />
                    </div>
                  </div>
                  <div className="field">
                    <label>Rubro</label>
                    <select value={form.rubro} onChange={(e) => set("rubro", e.target.value)}>
                      {RUBROS.map((r) => (
                        <option key={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ justifyContent: "center", opacity: can ? 1 : 0.45 }}
                    disabled={!can}
                    onClick={() => setSent(true)}
                  >
                    Enviar registro
                  </button>
                  <div className="demo-note">
                    Demo: en producción este registro pasa por validación manual (RUT + rubro)
                    antes de activar el descuento.
                  </div>
                </div>
              </div>
            ) : (
              <div className="co-success">
                <span className="ok-circle">
                  <Icon d={ICONS.check} size={34} stroke={2.4} />
                </span>
                <h3 style={{ fontSize: 24, marginBottom: 8 }}>¡Bienvenido a Trade Pro!</h3>
                <p
                  style={{
                    color: "var(--ink-soft)",
                    maxWidth: 360,
                    margin: "0 auto 24px",
                  }}
                >
                  {form.nombre.split(" ")[0]}, tu cuenta Pro Cobre quedó activa con 5% de
                  descuento en todo el catálogo. Tus compras de los próximos 3 meses suman para
                  subir de nivel.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    registerPro({
                      name: form.nombre,
                      rut: form.rut,
                      telefono: form.telefono,
                      rubro: form.rubro,
                    });
                    closeProModal();
                  }}
                >
                  Empezar a comprar
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
