"use client";

import { useRef, useState, useEffect } from "react";
import Image from "next/image";

interface GaleriaFotosProps {
  fotos: string[];
  nombre: string;
  productoId: string;
  shareUrl: string;
  shareText: string;
}

export default function GaleriaFotos({ fotos, nombre, productoId, shareUrl, shareText }: GaleriaFotosProps) {
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [imgError, setImgError] = useState<Record<number, boolean>>({});
  const [dragPx, setDragPx] = useState(0);
  const [arrastrando, setArrastrando] = useState(false);

  // Lightbox / zoom
  const [zoomOpen, setZoomOpen] = useState(false);
  const [escala, setEscala] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const startX = useRef(0);
  const vpW = useRef(1);
  const moved = useRef(0);
  const total = fotos.length;

  const [compAbierto, setCompAbierto] = useState(false); // menú de compartir propio
  useEffect(() => {
    if (!compAbierto) return;
    const cerrar = () => setCompAbierto(false);
    const id = window.setTimeout(() => document.addEventListener("click", cerrar), 0);
    return () => { window.clearTimeout(id); document.removeEventListener("click", cerrar); };
  }, [compAbierto]);

  // Favoritos (en este dispositivo, localStorage)
  const [fav, setFav] = useState(false);
  useEffect(() => {
    try {
      const favs: string[] = JSON.parse(localStorage.getItem("favoritos") || "[]");
      setFav(favs.includes(productoId));
    } catch {}
  }, [productoId]);
  function toggleFav(e: React.MouseEvent) {
    e.stopPropagation();
    try {
      const favs: string[] = JSON.parse(localStorage.getItem("favoritos") || "[]");
      const next = favs.includes(productoId)
        ? favs.filter((x) => x !== productoId)
        : [...favs, productoId];
      localStorage.setItem("favoritos", JSON.stringify(next));
      setFav(next.includes(productoId));
      window.dispatchEvent(new Event("favoritos:cambio"));
    } catch {}
  }
  function compartir(e: React.MouseEvent) {
    e.stopPropagation();
    setCompAbierto((o) => !o);
  }
  // Opciones de compartir (sin QR / enviar a dispositivos / copiar)
  const _t = encodeURIComponent(`${shareText}\n${shareUrl}`);
  const targets = [
    { label: "WhatsApp", color: "#25D366", href: `https://wa.me/?text=${_t}` },
  ];
  const iconBtn: React.CSSProperties = {
    width: 36, height: 36, borderRadius: "50%", border: "none",
    background: "rgba(255,255,255,0.92)", boxShadow: "0 2px 6px rgba(0,0,0,0.18)",
    cursor: "pointer", display: "grid", placeItems: "center", padding: 0,
  };

  function ir(ni: number) {
    setIndiceActivo(Math.max(0, Math.min(total - 1, ni)));
    setEscala(1);
    setPan({ x: 0, y: 0 });
  }

  // ── Swipe del carrusel principal (sigue el dedo, snap, y tap => zoom) ──
  function onDown(e: React.PointerEvent<HTMLDivElement>) {
    startX.current = e.clientX;
    vpW.current = e.currentTarget.offsetWidth || 1;
    moved.current = 0;
    setArrastrando(true);
    e.currentTarget.setPointerCapture?.(e.pointerId);
  }
  function onMove(e: React.PointerEvent<HTMLDivElement>) {
    if (!arrastrando || total < 2) return;
    let dx = e.clientX - startX.current;
    moved.current = Math.abs(dx);
    if ((indiceActivo === 0 && dx > 0) || (indiceActivo === total - 1 && dx < 0)) dx *= 0.35;
    setDragPx(dx);
  }
  function onUp(e: React.PointerEvent<HTMLDivElement>) {
    if (!arrastrando) return;
    const dx = e.clientX - startX.current;
    // tap (sin arrastre real) => abrir zoom
    if (Math.abs(dx) < 8) {
      setZoomOpen(true);
      setEscala(1);
      setPan({ x: 0, y: 0 });
    } else if (total > 1) {
      const umbral = Math.min(60, vpW.current * 0.18);
      if (dx < -umbral && indiceActivo < total - 1) setIndiceActivo(indiceActivo + 1);
      else if (dx > umbral && indiceActivo > 0) setIndiceActivo(indiceActivo - 1);
    }
    setDragPx(0);
    setArrastrando(false);
  }

  // ── Gestos del lightbox: pinch-to-zoom (2 dedos) + paneo (1 dedo) ──
  const pointers = useRef<Map<number, { x: number; y: number }>>(new Map());
  const pinchRef = useRef<{ dist: number; scale: number } | null>(null);
  const panRef = useRef<{ x: number; y: number; px: number; py: number } | null>(null);
  const lastTap = useRef(0);

  function distPts() {
    const p = [...pointers.current.values()];
    return p.length < 2 ? 0 : Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
  }
  function lbDown(e: React.PointerEvent<HTMLDivElement>) {
    e.stopPropagation();
    e.currentTarget.setPointerCapture?.(e.pointerId);
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.current.size === 2) {
      pinchRef.current = { dist: distPts(), scale: escala };
      panRef.current = null;
    } else {
      panRef.current = { x: e.clientX, y: e.clientY, px: pan.x, py: pan.y };
      const now = Date.now();
      if (now - lastTap.current < 300) {
        // doble toque = zoom rápido
        setEscala((s) => (s > 1 ? 1 : 2.5));
        setPan({ x: 0, y: 0 });
      }
      lastTap.current = now;
    }
  }
  function lbMove(e: React.PointerEvent<HTMLDivElement>) {
    if (!pointers.current.has(e.pointerId)) return;
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.current.size >= 2 && pinchRef.current) {
      const nd = distPts();
      if (nd > 0) {
        const s = Math.min(5, Math.max(1, pinchRef.current.scale * (nd / pinchRef.current.dist)));
        setEscala(s);
        if (s <= 1.01) setPan({ x: 0, y: 0 });
      }
    } else if (pointers.current.size === 1 && panRef.current && escala > 1) {
      setPan({
        x: panRef.current.px + (e.clientX - panRef.current.x),
        y: panRef.current.py + (e.clientY - panRef.current.y),
      });
    }
  }
  function lbUp(e: React.PointerEvent<HTMLDivElement>) {
    pointers.current.delete(e.pointerId);
    if (pointers.current.size < 2) pinchRef.current = null;
    if (pointers.current.size === 1) {
      const p = [...pointers.current.values()][0];
      panRef.current = { x: p.x, y: p.y, px: pan.x, py: pan.y };
    }
    if (pointers.current.size === 0 && escala <= 1.01) setPan({ x: 0, y: 0 });
  }

  const fotoZoom = fotos[indiceActivo];

  return (
    <div className="pdp-media">
      {/* Carrusel principal (deslizable + alto auto-ajustable) */}
      <div
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
        style={{
          height: "clamp(280px, 72vw, 420px)",
          position: "relative",
          borderRadius: "var(--radius)",
          overflow: "hidden",
          border: "1px solid var(--line)",
          background: "#fff",
          touchAction: "pan-y",
          cursor: arrastrando ? "grabbing" : "zoom-in",
          userSelect: "none",
        }}
      >
        <div
          style={{
            display: "flex",
            width: "100%",
            height: "100%",
            transform: `translateX(calc(${-indiceActivo * 100}% + ${dragPx}px))`,
            transition: arrastrando ? "none" : "transform 0.22s ease-out",
          }}
        >
          {fotos.map((url, i) => (
            <div key={i} style={{ flex: "0 0 100%", position: "relative", height: "100%" }}>
              {!imgError[i] ? (
                <Image
                  src={url}
                  alt={`${nombre} — foto ${i + 1}`}
                  fill
                  sizes="(max-width: 768px) 100vw, 50vw"
                  style={{ objectFit: "contain", pointerEvents: "none" }}
                  draggable={false}
                  unoptimized
                  onError={() => setImgError((prev) => ({ ...prev, [i]: true }))}
                />
              ) : (
                <div style={{ height: "100%", display: "grid", placeItems: "center" }}>
                  <span style={{ fontFamily: "var(--mono)", fontSize: 10.5, fontWeight: 700, opacity: 0.55, color: "#0e7cc4" }}>
                    sin foto
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Contador de fotos (arriba izquierda) */}
        {total > 1 && (
          <span
            style={{
              position: "absolute", top: 10, left: 10,
              background: "rgba(15,27,42,0.72)", color: "#fff",
              fontSize: 12, fontWeight: 700, padding: "3px 9px", borderRadius: 999,
              fontFamily: "var(--mono)", pointerEvents: "none",
            }}
          >
            {indiceActivo + 1} / {total}
          </span>
        )}

        {/* Acciones: compartir + favorito (arriba derecha) */}
        <div
          onPointerDown={(e) => e.stopPropagation()}
          onPointerUp={(e) => e.stopPropagation()}
          style={{ position: "absolute", top: 8, right: 8, display: "flex", gap: 8, zIndex: 2 }}
        >
          <button onClick={compartir} aria-label="Compartir" style={iconBtn}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f1b2a" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
          </button>
          <button onClick={toggleFav} aria-label={fav ? "Quitar de favoritos" : "Agregar a favoritos"} style={iconBtn}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill={fav ? "#e0245e" : "none"} stroke={fav ? "#e0245e" : "#0f1b2a"} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </button>

          {compAbierto && (
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                position: "absolute", top: 44, right: 0, background: "#fff",
                borderRadius: 8, boxShadow: "0 8px 26px rgba(0,0,0,0.2)",
                border: "1px solid var(--line)", padding: 6,
                display: "flex", flexDirection: "column", gap: 2, minWidth: 168, zIndex: 6,
              }}
            >
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--ink-3)", padding: "4px 8px" }}>Compartir</span>
              {targets.map((t) => (
                <a
                  key={t.label}
                  href={t.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setCompAbierto(false)}
                  style={{
                    display: "flex", alignItems: "center", gap: 10, padding: "9px 8px",
                    borderRadius: 6, textDecoration: "none", color: "var(--ink)", fontSize: 14, fontWeight: 600,
                  }}
                >
                  <span style={{ width: 18, height: 18, borderRadius: "50%", background: t.color, flexShrink: 0 }} />
                  {t.label}
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Puntos */}
        {total > 1 && (
          <div style={{ position: "absolute", bottom: 10, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 6, pointerEvents: "none" }}>
            {fotos.map((_, i) => (
              <span key={i} style={{ width: i === indiceActivo ? 18 : 6, height: 6, borderRadius: 3, background: i === indiceActivo ? "#0e7cc4" : "rgba(15,27,42,0.22)", transition: "width 0.2s ease, background 0.2s ease" }} />
            ))}
          </div>
        )}
      </div>

      {/* Miniaturas numeradas */}
      {total > 1 && (
        <div className="pdp-thumbs" style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
          {fotos.map((url, i) => (
            <button
              key={i}
              className={`pdp-thumb${i === indiceActivo ? " is-on" : ""}`}
              onClick={() => ir(i)}
              aria-label={`Ver foto ${i + 1}`}
              style={{ width: 68, background: "none", border: i === indiceActivo ? "2px solid #0e7cc4" : "1px solid var(--line, #ddd)", borderRadius: 8, padding: 0, cursor: "pointer" }}
            >
              <div style={{ width: "100%", height: 64, position: "relative", borderRadius: 6, overflow: "hidden", background: "#fff" }}>
                {!imgError[i] ? (
                  <Image src={url} alt={`${nombre} — miniatura ${i + 1}`} fill sizes="80px" style={{ objectFit: "contain" }} unoptimized onError={() => setImgError((prev) => ({ ...prev, [i]: true }))} />
                ) : (
                  <div style={{ height: "100%", display: "grid", placeItems: "center" }}>
                    <span style={{ fontSize: 9, color: "#0e7cc4", opacity: 0.55, fontWeight: 700 }}>—</span>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ── Lightbox con zoom ── */}
      {zoomOpen && fotoZoom && (
        <div
          onClick={() => setZoomOpen(false)}
          style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(8,14,22,0.94)", display: "grid", placeItems: "center", touchAction: "none" }}
        >
          {/* Contador */}
          <span style={{ position: "absolute", top: 14, left: 16, color: "#fff", fontSize: 13, fontWeight: 700, fontFamily: "var(--mono)" }}>
            {indiceActivo + 1} / {total}
          </span>
          {/* Cerrar */}
          <button
            onClick={(e) => { e.stopPropagation(); setZoomOpen(false); }}
            aria-label="Cerrar"
            style={{ position: "absolute", top: 10, right: 12, width: 38, height: 38, borderRadius: "50%", border: "none", background: "rgba(255,255,255,0.14)", color: "#fff", fontSize: 20, cursor: "pointer", lineHeight: 1 }}
          >
            ✕
          </button>

          {/* Imagen: pellizca con 2 dedos para zoom, arrastra con 1 para mover, doble toque = zoom rápido */}
          <div
            onPointerDown={lbDown}
            onPointerMove={lbMove}
            onPointerUp={lbUp}
            onPointerCancel={lbUp}
            style={{ position: "relative", width: "92vw", height: "82vh", touchAction: "none", cursor: escala > 1 ? "grab" : "zoom-in" }}
          >
            <Image
              src={fotoZoom}
              alt={`${nombre} — foto ${indiceActivo + 1} ampliada`}
              fill
              sizes="92vw"
              style={{ objectFit: "contain", transform: `translate(${pan.x}px, ${pan.y}px) scale(${escala})`, transition: pointers.current.size ? "none" : "transform 0.18s ease-out", pointerEvents: "none" }}
              draggable={false}
              unoptimized
            />
          </div>

          {/* Flechas prev/next */}
          {total > 1 && (
            <>
              <button
                onClick={(e) => { e.stopPropagation(); ir(indiceActivo - 1); }}
                disabled={indiceActivo === 0}
                aria-label="Anterior"
                style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", width: 42, height: 42, borderRadius: "50%", border: "none", background: "rgba(255,255,255,0.14)", color: "#fff", fontSize: 22, cursor: "pointer", opacity: indiceActivo === 0 ? 0.3 : 1 }}
              >
                ‹
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); ir(indiceActivo + 1); }}
                disabled={indiceActivo === total - 1}
                aria-label="Siguiente"
                style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", width: 42, height: 42, borderRadius: "50%", border: "none", background: "rgba(255,255,255,0.14)", color: "#fff", fontSize: 22, cursor: "pointer", opacity: indiceActivo === total - 1 ? 0.3 : 1 }}
              >
                ›
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
