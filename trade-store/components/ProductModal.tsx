"use client";

import { useEffect, useRef, useState } from "react";
import { cuotaText, formatCLP } from "@/lib/format";
import { installationFor, INSTALLATION_NOTE } from "@/lib/installation";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

export function ProductModal() {
  const { viewProduct: p, setViewProduct, addToCart, justAdded, openInstallTerms } = useStore();
  const [active, setActive] = useState(0);
  const [withInstall, setWithInstall] = useState(false);
  const sliderRef = useRef<HTMLDivElement>(null);

  const goTo = (i: number) => {
    const el = sliderRef.current;
    if (el) el.scrollTo({ left: i * el.clientWidth, behavior: "smooth" });
  };
  const onSliderScroll = () => {
    const el = sliderRef.current;
    if (el) setActive(Math.round(el.scrollLeft / el.clientWidth));
  };

  useEffect(() => {
    setActive(0);
    setWithInstall(false);
    if (sliderRef.current) sliderRef.current.scrollLeft = 0;
  }, [p?.id]);

  // navegar la galería con flechas ← →
  useEffect(() => {
    const list = p?.images?.length ? p.images : p?.image ? [p.image] : [];
    if (!p || list.length < 2) return;
    const onKey = (e: KeyboardEvent) => {
      const el = sliderRef.current;
      if (!el) return;
      const cur = Math.round(el.scrollLeft / el.clientWidth);
      if (e.key === "ArrowRight") el.scrollTo({ left: Math.min(cur + 1, list.length - 1) * el.clientWidth, behavior: "smooth" });
      else if (e.key === "ArrowLeft") el.scrollTo({ left: Math.max(cur - 1, 0) * el.clientWidth, behavior: "smooth" });
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [p?.id, p?.image, p?.images]);

  if (!p) return null;
  const added = justAdded === p.id;
  const close = () => setViewProduct(null);
  const imgs = p.images && p.images.length ? p.images : p.image ? [p.image] : [];
  const service = installationFor(p);
  return (
    <div>
      <div className="overlay" onClick={close} />
      <div
        className="modal"
        onClick={(e) => {
          if (e.target === e.currentTarget) close();
        }}
      >
        <div className="modal-card">
          <button
            className="icon-btn"
            style={{ position: "absolute", top: 16, right: 16, zIndex: 2 }}
            onClick={close}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div className="pm-grid">
            <div className="pm-media">
              <div className={"pm-img" + (imgs.length ? " has-photo" : "")}>
                {imgs.length ? (
                  <div className="pm-slider" ref={sliderRef} onScroll={onSliderScroll}>
                    {imgs.map((src, i) => (
                      <div className="pm-slide" key={src + i}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={src} alt={`${p.name} — foto ${i + 1}`} loading={i === 0 ? "eager" : "lazy"} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <span className="ph-letter">{p.name[0]}</span>
                )}
                {p.priceOriginal && <span className="badge sale">Oferta</span>}
                {imgs.length > 1 && (
                  <span className="pm-counter">
                    {active + 1} / {imgs.length}
                  </span>
                )}
              </div>
              {imgs.length > 1 && (
                <div className="pm-thumbs">
                  {imgs.map((src, i) => (
                    <button
                      key={src + i}
                      className={"pm-thumb" + (i === active ? " on" : "")}
                      onClick={() => goTo(i)}
                      aria-label={`Ver foto ${i + 1}`}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={src} alt="" loading="lazy" />
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="pm-body">
              <span className="pm-cat">{p.category}</span>
              <h3>{p.name}</h3>
              <p className="pm-sku">
                SKU: {p.sku}
                {p.lowStock ? " · Últimas unidades" : ""}
              </p>
              <div>
                <span className="pm-price">{formatCLP(p.price)}</span>
                {p.priceOriginal && (
                  <span className="pm-price-old">{formatCLP(p.priceOriginal)}</span>
                )}
              </div>
              {cuotaText(p.price) && <p className="pm-cuotas">ó {cuotaText(p.price)}</p>}
              {p.attributes && p.attributes.length > 0 && (
                <div className="pm-specs">
                  <span className="pm-specs-title">Ficha técnica</span>
                  <dl>
                    {p.attributes.map((a) => (
                      <div key={a.name}>
                        <dt>{a.name}</dt>
                        <dd>{a.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
              <div className="pm-perks">
                <span className="pm-perk">
                  <Icon d={ICONS.truck} size={18} /> Despacho a todo Chile en 2–5 días hábiles
                </span>
                <span className="pm-perk">
                  <Icon d={ICONS.shield} size={18} /> Garantía de 6 meses por defectos de fábrica
                </span>
                <span className="pm-perk">
                  <Icon d={ICONS.chat} size={18} /> ¿Dudas de compatibilidad? Te asesoramos por
                  WhatsApp
                </span>
              </div>
              {service && (
                <label className={"install-opt" + (withInstall ? " on" : "")}>
                  <input
                    type="checkbox"
                    checked={withInstall}
                    onChange={(e) => setWithInstall(e.target.checked)}
                  />
                  <span className="install-box">
                    {withInstall && <Icon d={ICONS.check} size={14} stroke={2.4} />}
                  </span>
                  <span className="install-text">
                    <b>
                      Agregar {service.name.toLowerCase()}{" "}
                      <span className="install-price">+{formatCLP(service.price)}</span>
                    </b>
                    <span>{INSTALLATION_NOTE}</span>
                    <button
                      type="button"
                      className="install-terms-link"
                      onClick={(e) => {
                        e.preventDefault();
                        openInstallTerms();
                      }}
                    >
                      Ver condiciones del servicio
                    </button>
                  </span>
                </label>
              )}
              <button
                className={"btn " + (added ? "btn-accent" : "btn-primary")}
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => {
                  addToCart(p);
                  if (service && withInstall) addToCart(service);
                }}
              >
                {added ? <Icon d={ICONS.check} size={18} /> : <Icon d={ICONS.cart} size={18} />}
                {added ? "Agregado al carrito" : "Agregar al carrito"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
