"use client";

import { useEffect, useState } from "react";
import { useStore } from "@/lib/store-context";

export function AccountModal() {
  const { accountOpen, closeAccount, user, login, register, logout, openWishlist } = useStore();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ nombre: "", email: "", pass: "" });

  useEffect(() => {
    if (accountOpen) {
      setMode("login");
      setForm({ nombre: "", email: "", pass: "" });
    }
  }, [accountOpen]);

  if (!accountOpen) return null;
  const set = (k: keyof typeof form, v: string) => setForm({ ...form, [k]: v });
  const can =
    mode === "login"
      ? Boolean(form.email.trim() && form.pass.trim())
      : Boolean(form.nombre.trim() && form.email.trim() && form.pass.trim());

  return (
    <div>
      <div className="overlay" onClick={closeAccount} />
      <div
        className="modal"
        onClick={(e) => {
          if (e.target === e.currentTarget) closeAccount();
        }}
      >
        <div className="modal-card" style={{ maxWidth: 440 }}>
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={closeAccount}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div style={{ padding: "36px 36px 32px" }}>
            {user ? (
              <div>
                <h3 style={{ fontSize: 22, marginBottom: 4 }}>Hola, {user.name}</h3>
                <p style={{ color: "var(--ink-soft)", fontSize: 14.5, marginBottom: 22 }}>
                  {user.email}
                </p>
                <div style={{ display: "grid", gap: 10 }}>
                  <button
                    className="btn btn-ghost"
                    style={{ justifyContent: "center" }}
                    onClick={() => {
                      closeAccount();
                      openWishlist();
                    }}
                  >
                    Ver mis favoritos
                  </button>
                  <button
                    className="btn btn-primary"
                    style={{ justifyContent: "center" }}
                    onClick={logout}
                  >
                    Cerrar sesión
                  </button>
                </div>
                <div className="demo-note" style={{ marginTop: 18 }}>
                  Demo: en producción verás aquí tu historial de pedidos y tus datos de despacho
                  guardados.
                </div>
              </div>
            ) : (
              <div>
                <div className="acc-tabs">
                  <button
                    className={"acc-tab" + (mode === "login" ? " on" : "")}
                    onClick={() => setMode("login")}
                  >
                    Iniciar sesión
                  </button>
                  <button
                    className={"acc-tab" + (mode === "register" ? " on" : "")}
                    onClick={() => setMode("register")}
                  >
                    Crear cuenta
                  </button>
                </div>
                <div style={{ display: "grid", gap: 14, marginTop: 20 }}>
                  {mode === "register" && (
                    <div className="field">
                      <label>Nombre</label>
                      <input
                        value={form.nombre}
                        onChange={(e) => set("nombre", e.target.value)}
                        placeholder="Tu nombre"
                      />
                    </div>
                  )}
                  <div className="field">
                    <label>Correo electrónico</label>
                    <input
                      type="email"
                      value={form.email}
                      onChange={(e) => set("email", e.target.value)}
                      placeholder="tucorreo@ejemplo.cl"
                    />
                  </div>
                  <div className="field">
                    <label>Contraseña</label>
                    <input
                      type="password"
                      value={form.pass}
                      onChange={(e) => set("pass", e.target.value)}
                      placeholder="••••••••"
                    />
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ justifyContent: "center", opacity: can ? 1 : 0.45 }}
                    disabled={!can}
                    onClick={() =>
                      mode === "login"
                        ? login(form.email)
                        : register(form.nombre || form.email.split("@")[0], form.email)
                    }
                  >
                    {mode === "login" ? "Entrar" : "Crear cuenta"}
                  </button>
                  <div className="demo-note">
                    Demo: autenticación de ejemplo (no valida la contraseña). En producción se
                    conecta a cuentas reales con tu historial de pedidos.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
