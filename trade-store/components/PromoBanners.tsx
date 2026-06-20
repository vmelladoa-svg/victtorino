"use client";

import { useState } from "react";
import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

function DuoCard({
  variant,
  cat,
  kicker,
  title,
  text,
  cta,
  img,
  onPick,
}: {
  variant: "bath" | "kitchen";
  cat: string;
  kicker: string;
  title: string;
  text: string;
  cta: string;
  img: string;
  onPick: (cat: string) => void;
}) {
  const [imgOk, setImgOk] = useState(true);
  return (
    <button className={"duo-card " + variant} onClick={() => onPick(cat)}>
      {imgOk ? (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="duo-photo"
            src={img}
            alt=""
            loading="lazy"
            decoding="async"
            onError={() => setImgOk(false)}
          />
          <span className="duo-shade" />
        </>
      ) : (
        <span
          className="duo-orb"
          style={{ width: 280, height: 280, top: -90, right: -60 }}
        />
      )}
      <span className="duo-kicker">{kicker}</span>
      <h3>{title}</h3>
      <p>{text}</p>
      <span className="duo-cta">
        {cta} <Icon d={ICONS.arrow} size={16} />
      </span>
    </button>
  );
}

export function PromoBanners() {
  const { pickCategory } = useStore();
  return (
    <section className="block" style={{ paddingTop: 0 }}>
      <div className="wrap duo-grid">
        <DuoCard
          variant="bath"
          cat="Baño"
          kicker="Baño"
          title="Renueva tu baño completo"
          text="Vanitorios, espejos LED, grifería y accesorios en acero inoxidable que combinan entre sí."
          cta="Ver productos de baño"
          img="/categories/banner-bano.webp"
          onPick={pickCategory}
        />
        <DuoCard
          variant="kitchen"
          cat="Cocina"
          kicker="Cocina"
          title="Equipa tu cocina como profesional"
          text="Lavaplatos, grifos extensibles, filtros de agua y organización bajo mesada."
          cta="Ver productos de cocina"
          img="/categories/banner-cocina.webp"
          onPick={pickCategory}
        />
      </div>
    </section>
  );
}
