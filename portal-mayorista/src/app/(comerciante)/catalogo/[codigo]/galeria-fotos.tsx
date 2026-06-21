"use client";

import { useState } from "react";
import Image from "next/image";

interface GaleriaFotosProps {
  fotos: string[];
  nombre: string;
}

export default function GaleriaFotos({ fotos, nombre }: GaleriaFotosProps) {
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [imgError, setImgError] = useState<Record<number, boolean>>({});

  const fotoActiva = fotos[indiceActivo];
  const tieneError = imgError[indiceActivo];

  return (
    <div className="pdp-media">
      {/* Foto principal */}
      <div
        style={{
          height: 380,
          position: "relative",
          borderRadius: "var(--radius)",
          overflow: "hidden",
          border: "1px solid var(--line)",
          background: "#0e7cc414",
        }}
      >
        {fotoActiva && !tieneError ? (
          <Image
            src={fotoActiva}
            alt={`${nombre} — foto ${indiceActivo + 1}`}
            fill
            sizes="(max-width: 768px) 100vw, 50vw"
            style={{ objectFit: "contain" }}
            unoptimized
            onError={() =>
              setImgError((prev) => ({ ...prev, [indiceActivo]: true }))
            }
          />
        ) : (
          <div
            style={{
              height: "100%",
              display: "grid",
              placeItems: "center",
            }}
          >
            <span
              style={{
                fontFamily: "var(--mono)",
                fontSize: "10.5px",
                fontWeight: 700,
                opacity: 0.55,
                letterSpacing: ".02em",
                color: "#0e7cc4",
              }}
            >
              sin foto
            </span>
          </div>
        )}
      </div>

      {/* Miniaturas — solo si hay más de 1 foto */}
      {fotos.length > 1 && (
        <div
          className="pdp-thumbs"
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            marginTop: 10,
          }}
        >
          {fotos.map((url, i) => (
            <button
              key={i}
              className={`pdp-thumb${i === indiceActivo ? " is-on" : ""}`}
              onClick={() => setIndiceActivo(i)}
              aria-label={`Ver foto ${i + 1}`}
              style={{
                width: 68,
                background: "none",
                border:
                  i === indiceActivo
                    ? "2px solid #0e7cc4"
                    : "1px solid var(--line, #ddd)",
                borderRadius: 8,
                padding: 0,
                cursor: "pointer",
              }}
            >
              <div
                style={{
                  width: "100%",
                  height: 64,
                  position: "relative",
                  borderRadius: 6,
                  overflow: "hidden",
                  background: "#0e7cc414",
                }}
              >
                {!imgError[i] ? (
                  <Image
                    src={url}
                    alt={`${nombre} — miniatura ${i + 1}`}
                    fill
                    sizes="80px"
                    style={{ objectFit: "cover" }}
                    unoptimized
                    onError={() =>
                      setImgError((prev) => ({ ...prev, [i]: true }))
                    }
                  />
                ) : (
                  <div
                    style={{
                      height: "100%",
                      display: "grid",
                      placeItems: "center",
                    }}
                  >
                    <span
                      style={{
                        fontSize: 9,
                        color: "#0e7cc4",
                        opacity: 0.55,
                        fontWeight: 700,
                      }}
                    >
                      —
                    </span>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
