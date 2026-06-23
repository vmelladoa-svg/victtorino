"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import AgregarAlCarrito from "./agregar";
import { GRUPOS, OTROS, nivel1, grupoDe } from "@/lib/categorias";

/* ------------------------------------------------------------------ */
/*  Tipos                                                               */
/* ------------------------------------------------------------------ */
export type ProductoRow = {
  id: string;
  codigoAlila: string;
  nombre: string;
  categoria: string | null;
  precioT1: number | null;
  precioT2: number | null;
  precioT3: number | null;
  fotoUrl: string | null;
  stock: number | null;
  activo: boolean;
};

/* ------------------------------------------------------------------ */
/*  Helpers                                                             */
/* ------------------------------------------------------------------ */
function clp(n: number | null): string {
  if (n == null) return "Consultar";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(n);
}

/* ------------------------------------------------------------------ */
/*  Icono simple SVG inline                                             */
/* ------------------------------------------------------------------ */
function SearchIcon() {
  return (
    <svg
      width={18}
      height={18}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  );
}

function FilterIcon() {
  return (
    <svg
      width={16}
      height={16}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 5h18M6 12h12M10 19h4" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Tarjeta de producto                                                  */
/* ------------------------------------------------------------------ */
export function ProductCard({ prod }: { prod: ProductoRow }) {
  // stock null = sin tope (aún sin scraper); solo "sin stock" si es un número <= 0
  const sinStock = prod.stock != null && prod.stock <= 0;
  const [imgError, setImgError] = useState(false);

  return (
    <article
      className={`pcard${sinStock ? " is-out" : ""}`}
      style={{ cursor: "default" }}
    >
      {/* Imagen */}
      <div className="pcard-media">
        <Link href={"/catalogo/" + prod.codigoAlila} style={{ display: "block", textDecoration: "none" }}>
          {prod.fotoUrl && !imgError ? (
            <div
              style={{
                height: 168,
                position: "relative",
                borderRadius: "var(--rs)",
                overflow: "hidden",
                background: "#fff",
              }}
            >
              <Image
                src={prod.fotoUrl}
                alt={prod.nombre}
                fill
                sizes="(max-width: 720px) 50vw, (max-width: 1080px) 33vw, 25vw"
                style={{ objectFit: "contain" }}
                onError={() => setImgError(true)}
              />
            </div>
          ) : (
            /* Placeholder de rayas igual a la maqueta */
            <div
              style={{
                height: 168,
                background: "#0e7cc414",
                borderRadius: "var(--rs)",
                display: "grid",
                placeItems: "center",
                position: "relative",
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
        </Link>

        {/* Badge sin stock */}
        {sinStock && (
          <div className="pcard-tags">
            <span className="badge badge-out">Sin stock</span>
          </div>
        )}
      </div>

      {/* Cuerpo */}
      <div className="pcard-body">
        <span className="pcard-sku mono">{prod.codigoAlila}</span>
        <Link href={"/catalogo/" + prod.codigoAlila} style={{ textDecoration: "none", color: "inherit" }}>
          <h3>{prod.nombre}</h3>
        </Link>

        {/* Tramos de precio */}
        <div
          className="vol"
          style={{ margin: "8px 0 4px", border: "1px solid var(--line)", borderRadius: "var(--radius)", overflow: "hidden" }}
        >
          <div className="vol-head">
            <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10" />
            </svg>
            Precio por volumen
          </div>
          <div className="vol-tiers">
            <div className="vol-tier">
              <small>1–5 unid.</small>
              <strong className="mono">{clp(prod.precioT1)}</strong>
            </div>
            <div className="vol-tier">
              <small>6–20 unid.</small>
              <strong className="mono">{clp(prod.precioT2)}</strong>
            </div>
            <div className="vol-tier" style={{ borderRight: 0 }}>
              <small>21+ unid.</small>
              <strong className="mono">{clp(prod.precioT3)}</strong>
            </div>
          </div>
        </div>

        {prod.categoria && (
          <div className="pcard-meta">
            <span className="badge badge-neutral">{prod.categoria}</span>
          </div>
        )}

        <AgregarAlCarrito prod={prod} />
      </div>
    </article>
  );
}

/* ------------------------------------------------------------------ */
/*  Agrupación de categorías: 9 grupos -> categorías principales (18)    */
/* ------------------------------------------------------------------ */
const CATEGORY_GROUPS: { name: string; cats: string[] }[] = [
  { name: "Tecnología", cats: ["Computación", "Celulares y Telefonía", "Electrónica, Audio y Video", "Cámaras y Accesorios"] },
  { name: "Herramientas y Construcción", cats: ["Herramientas", "Construcción"] },
  { name: "Hogar y Jardín", cats: ["Hogar y Muebles", "Electrodomésticos"] },
  { name: "Salud y Deporte", cats: ["Salud y Equipamiento Médico", "Deportes y Fitness"] },
  { name: "Infantil", cats: ["Bebés", "Juegos y Juguetes"] },
  { name: "Moda y Belleza", cats: ["Vestuario y Calzado", "Belleza y Cuidado Personal"] },
  { name: "Vehículos", cats: ["Accesorios para Vehículos"] },
  { name: "Industria y Oficina", cats: ["Industrias y Oficinas", "Instrumentos Musicales"] },
  { name: "Mascotas", cats: ["Animales y Mascotas"] },
];

// Normaliza para emparejar a prueba de acentos / comas / espacios.
function normCat(s: string): string {
  return s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

// norm(categoría principal) -> nombre del grupo
const CAT_TO_GROUP: Record<string, string> = {};
for (const g of CATEGORY_GROUPS) for (const c of g.cats) CAT_TO_GROUP[normCat(c)] = g.name;

// Categoría principal de un producto: "Principal>Sub" -> "Principal"
function mainCat(categoria: string | null): string {
  return (categoria ?? "").split(">")[0].trim();
}
// Grupo al que pertenece un producto (vía su categoría principal)
function groupOf(categoria: string | null): string {
  return CAT_TO_GROUP[normCat(mainCat(categoria))] ?? "Otras";
}

/* ------------------------------------------------------------------ */
/*  Componente principal (client)                                        */
/* ------------------------------------------------------------------ */
export default function BuscarCatalogo({
  productos,
  categorias,
  initialQuery = "",
}: {
  productos: ProductoRow[];
  categorias: string[];
  initialQuery?: string;
}) {
  const [query, setQuery] = useState(initialQuery);
  useEffect(() => setQuery(initialQuery), [initialQuery]); // búsqueda desde el header (URL ?q)
  const [group, setGroup] = useState("todas"); // nivel 1: grupo
  const [subcat, setSubcat] = useState(""); // nivel 2: categoría principal real ("" = todo el grupo)
  const [pagina, setPagina] = useState(1);
  const skipReset = useRef(false);

  // Al volver desde una ficha: restaurar página, filtros y scroll (sessionStorage).
  useEffect(() => {
    try {
      const s = JSON.parse(sessionStorage.getItem("catEstado") || "null");
      if (s) {
        skipReset.current = true; // no resetear página mientras restauramos los filtros
        if (s.group) setGroup(s.group);
        if (typeof s.subcat === "string") setSubcat(s.subcat);
        if (s.pagina) setPagina(s.pagina);
        requestAnimationFrame(() => { skipReset.current = false; });
      }
      const y = Number(sessionStorage.getItem("catScroll"));
      if (y > 0) requestAnimationFrame(() => requestAnimationFrame(() => window.scrollTo(0, y)));
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persistir filtros + página.
  useEffect(() => {
    try { sessionStorage.setItem("catEstado", JSON.stringify({ group, subcat, pagina })); } catch {}
  }, [group, subcat, pagina]);

  // Guardar posición de scroll (throttle con rAF) para restaurarla al volver.
  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => { raf = 0; try { sessionStorage.setItem("catScroll", String(window.scrollY)); } catch {} });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => { window.removeEventListener("scroll", onScroll); if (raf) cancelAnimationFrame(raf); };
  }, []);

  // Grupos presentes en los datos, con sus categorías reales (nivel 2), en el orden definido.
  const grupos = useMemo(() => {
    const porGrupo = new Map<string, Set<string>>();
    for (const c of categorias) {
      const mc = mainCat(c);
      if (!mc) continue;
      const g = CAT_TO_GROUP[normCat(mc)] ?? "Otras";
      if (!porGrupo.has(g)) porGrupo.set(g, new Set());
      porGrupo.get(g)!.add(mc);
    }
    const orden = [...CATEGORY_GROUPS.map((g) => g.name), "Otras"];
    return orden
      .filter((name) => porGrupo.has(name))
      .map((name) => ({
        name,
        cats: [...porGrupo.get(name)!].sort((a, b) => a.localeCompare(b, "es")),
      }));
  }, [categorias]);

  // Categorías (nivel 2) del grupo seleccionado.
  const catsDelGrupo = useMemo(() => {
    if (group === "todas") return [];
    return grupos.find((g) => g.name === group)?.cats ?? [];
  }, [grupos, group]);

  const lista = useMemo(() => {
    let l = productos;

    // Filtro por categoría: subcategoría (categoría principal real) o grupo completo.
    if (subcat) {
      l = l.filter((p) => mainCat(p.categoria) === subcat);
    } else if (group !== "todas") {
      l = l.filter((p) => groupOf(p.categoria) === group);
    }

    // Filtro por texto
    const q = query.trim().toLowerCase();
    if (q) {
      l = l.filter((p) =>
        (p.nombre + " " + p.codigoAlila + " " + (p.categoria ?? ""))
          .toLowerCase()
          .includes(q)
      );
    }

    return l;
  }, [productos, query, group, subcat]);

  // Paginación: 24 por página, fácil de navegar.
  const POR_PAGINA = 24;
  const totalPaginas = Math.max(1, Math.ceil(lista.length / POR_PAGINA));
  const paginaSegura = Math.min(pagina, totalPaginas);
  const visibles = lista.slice((paginaSegura - 1) * POR_PAGINA, paginaSegura * POR_PAGINA);
  useEffect(() => {
    if (skipReset.current) return; // no resetear al restaurar estado
    setPagina(1);
  }, [query, group, subcat]); // volver a pág. 1 al filtrar
  function irPagina(n: number) {
    setPagina(n);
    if (typeof window !== "undefined") window.scrollTo({ top: 0, behavior: "smooth" });
  }
  const numeros: (number | "…")[] = [];
  if (totalPaginas <= 7) {
    for (let i = 1; i <= totalPaginas; i++) numeros.push(i);
  } else {
    numeros.push(1);
    const ini = Math.max(2, paginaSegura - 1);
    const fin = Math.min(totalPaginas - 1, paginaSegura + 1);
    if (ini > 2) numeros.push("…");
    for (let i = ini; i <= fin; i++) numeros.push(i);
    if (fin < totalPaginas - 1) numeros.push("…");
    numeros.push(totalPaginas);
  }

  // Selección desde el <select> jerárquico (optgroups).
  function onSelect(value: string) {
    if (value === "todas") {
      setGroup("todas");
      setSubcat("");
    } else if (value.startsWith("g:")) {
      setGroup(value.slice(2));
      setSubcat("");
    } else if (value.startsWith("c:")) {
      const c = value.slice(2);
      setGroup(CAT_TO_GROUP[normCat(c)] ?? "Otras");
      setSubcat(c);
    }
  }
  const selectValue = subcat ? `c:${subcat}` : group !== "todas" ? `g:${group}` : "todas";

  return (
    <div className="catalog">
      {/* Barra de búsqueda */}
      <div
        style={{
          display: "flex",
          gap: 12,
          marginBottom: 22,
          flexWrap: "wrap",
        }}
      >
        {/* Select jerárquico: 9 grupos con sus categorías (optgroups) */}
        <div
          className="cat-sort"
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          <FilterIcon />
          <select
            value={selectValue}
            onChange={(e) => onSelect(e.target.value)}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--rs)",
              padding: "9px 12px",
              background: "var(--surface)",
              fontSize: "13.5px",
              fontWeight: 600,
              color: "var(--ink)",
              cursor: "pointer",
              outline: "none",
              fontFamily: "inherit",
            }}
          >
            <option value="todas">Todas las categorías</option>
            {grupos.map((g) => (
              <optgroup key={g.name} label={g.name}>
                <option value={`g:${g.name}`}>Todo {g.name}</option>
                {g.cats.map((c) => (
                  <option key={c} value={`c:${c}`}>
                    {"  "}
                    {c}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>
      </div>

      {/* Contador */}
      <div className="cat-head" style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 21, fontWeight: 800 }}>
          {query
            ? `Resultados para "${query}"`
            : subcat
            ? subcat
            : group !== "todas"
            ? group
            : "Catálogo mayorista"}
        </h2>
        <span className="mono" style={{ color: "var(--ink-3)", fontSize: 13 }}>
          {lista.length} producto{lista.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Nivel 1: grupos principales */}
      <div className="cat-bar" style={{ marginBottom: catsDelGrupo.length ? 10 : 22 }}>
        <div className="cat-chips">
          <button
            className={`chip${group === "todas" ? " is-on" : ""}`}
            onClick={() => {
              setGroup("todas");
              setSubcat("");
            }}
          >
            Todas
          </button>
          {grupos.map((g) => (
            <button
              key={g.name}
              className={`chip${group === g.name ? " is-on" : ""}`}
              onClick={() => {
                setGroup(g.name);
                setSubcat("");
              }}
            >
              {g.name}
            </button>
          ))}
        </div>
      </div>

      {/* Nivel 2: categorías del grupo seleccionado */}
      {group !== "todas" && catsDelGrupo.length > 0 && (
        <div className="cat-bar" style={{ marginBottom: 22 }}>
          <div className="cat-chips">
            <button
              className={`chip${subcat === "" ? " is-on" : ""}`}
              onClick={() => setSubcat("")}
              style={{ fontStyle: "italic" }}
            >
              Todo {group}
            </button>
            {catsDelGrupo.map((c) => (
              <button
                key={c}
                className={`chip${subcat === c ? " is-on" : ""}`}
                onClick={() => setSubcat(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Grilla */}
      {lista.length > 0 ? (
        <div className="pgrid">
          {visibles.map((p) => (
            <ProductCard key={p.id} prod={p} />
          ))}
        </div>
      ) : (
        <div className="empty">
          <SearchIcon />
          <p>No encontramos productos para tu búsqueda.</p>
        </div>
      )}

      {/* Paginación */}
      {lista.length > 0 && totalPaginas > 1 && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, marginTop: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", justifyContent: "center" }}>
            <button
              className="chip"
              onClick={() => irPagina(paginaSegura - 1)}
              disabled={paginaSegura === 1}
              style={{ opacity: paginaSegura === 1 ? 0.4 : 1, cursor: paginaSegura === 1 ? "default" : "pointer" }}
            >
              ‹ Anterior
            </button>
            {numeros.map((n, i) =>
              n === "…" ? (
                <span key={`e${i}`} style={{ padding: "0 4px", color: "var(--ink-3)" }}>…</span>
              ) : (
                <button
                  key={n}
                  className={`chip${n === paginaSegura ? " is-on" : ""}`}
                  onClick={() => irPagina(n)}
                >
                  {n}
                </button>
              )
            )}
            <button
              className="chip"
              onClick={() => irPagina(paginaSegura + 1)}
              disabled={paginaSegura === totalPaginas}
              style={{ opacity: paginaSegura === totalPaginas ? 0.4 : 1, cursor: paginaSegura === totalPaginas ? "default" : "pointer" }}
            >
              Siguiente ›
            </button>
          </div>
          <span className="mono" style={{ fontSize: 12.5, color: "var(--ink-3)" }}>
            Mostrando {(paginaSegura - 1) * POR_PAGINA + 1}–{Math.min(paginaSegura * POR_PAGINA, lista.length)} de {lista.length}
          </span>
        </div>
      )}
    </div>
  );
}
