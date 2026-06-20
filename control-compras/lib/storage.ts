"use client";
// ============================================================
//  ALMACENAMIENTO
//  - Modo NUBE: si el servidor tiene la base de datos configurada
//    (Upstash/Redis vía Vercel), lee/escribe vía /api/data → sincroniza
//    entre dispositivos. El PIN se valida en el servidor.
//  - Modo LOCAL (respaldo): si no hay nube, guarda en este navegador
//    (localStorage). Útil mientras no se conecta la base, o sin internet.
// ============================================================
import { AppData, emptyData } from "./types";

const LS_KEY = "control-compras-data";
const PIN_KEY = "control-compras-pin";

let _cloud: boolean | null = null;
let _pin = "";

export async function detectCloud(): Promise<boolean> {
  if (_cloud !== null) return _cloud;
  try {
    const r = await fetch("/api/status");
    const j = await r.json();
    _cloud = !!j.cloud;
  } catch {
    _cloud = false;
  }
  return _cloud;
}

export const isCloud = () => _cloud === true;
export const getStoredPin = () => {
  try {
    return localStorage.getItem(PIN_KEY) || "";
  } catch {
    return "";
  }
};
const rememberPin = (p: string) => {
  _pin = p;
  try {
    localStorage.setItem(PIN_KEY, p);
  } catch {}
};

/** Carga los datos validando el PIN. Lanza Error("PIN") si es incorrecto. */
export async function loadData(pin: string): Promise<AppData> {
  const cloud = await detectCloud();
  if (cloud) {
    const r = await fetch("/api/data", { headers: { "x-pin": pin } });
    if (r.status === 401) throw new Error("PIN");
    const j = await r.json();
    rememberPin(pin);
    return (j.data as AppData) ?? emptyData();
  }
  // modo local
  const stored = getStoredPin();
  if (stored && stored !== pin) throw new Error("PIN");
  rememberPin(pin);
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? (JSON.parse(raw) as AppData) : emptyData();
  } catch {
    return emptyData();
  }
}

export async function saveData(data: AppData): Promise<void> {
  if (isCloud()) {
    await fetch("/api/data", {
      method: "POST",
      headers: { "content-type": "application/json", "x-pin": _pin },
      body: JSON.stringify(data),
    });
  } else {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(data));
    } catch {}
  }
}
