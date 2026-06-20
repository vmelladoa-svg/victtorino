"use client";
import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import { products, categories, brands, type Sport } from "@/data/products";
import { formatCLP } from "@/lib/format";

const PRICES = products.map((p) => p.price);
const MIN = Math.min(...PRICES);
const MAX = Math.max(...PRICES);

type Sort = "relevancia" | "precio-asc" | "precio-desc" | "novedades";

export default function Catalog() {
  const params = useSearchParams();
  const initialSport = (params.get("sport") as Sport) || "all";

  const [sport, setSport] = useState<Sport | "all">(initialSport);
  const [brandSel, setBrandSel] = useState<string[]>([]);
  const [level, setLevel] = useState<"all" | "amateur" | "profesional">("all");
  const [use, setUse] = useState<"all" | "indoor" | "outdoor">("all");
  const [maxPrice, setMaxPrice] = useState(MAX);
  const [sort, setSort] = useState<Sort>("relevancia");
  const [open, setOpen] = useState(false); // filtros móvil

  const toggleBrand = (b: string) =>
    setBrandSel((s) => (s.includes(b) ? s.filter((x) => x !== b) : [...s, b]));

  const reset = () => {
    setSport("all"); setBrandSel([]); setLevel("all"); setUse("all"); setMaxPrice(MAX); setSort("relevancia");
  };

  const filtered = useMemo(() => {
    let list = products.filter((p) => {
      if (sport !== "all" && p.sport !== sport) return false;
      if (brandSel.length && !brandSel.includes(p.brand)) return false;
      if (level !== "all" && p.level !== level) return false;
      if (use !== "all" && p.use !== use) return false;
      if (p.price > maxPrice) return false;
      return true;
    });
    if (sort === "precio-asc") list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "precio-desc") list = [...list].sort((a, b) => b.price - a.price);
    if (sort === "novedades")
      list = [...list].sort((a, b) => Number(b.badges.includes("Nuevo")) - Number(a.badges.includes("Nuevo")));
    return list;
  }, [sport, brandSel, level, use, maxPrice, sort]);

  const cat = categories.find((c) => c.slug === sport);

  const Filters = (
    <div className="space-y-6">
      <FilterGroup title="Deporte">
        <Radio name="sport" label="Todos" checked={sport === "all"} onChange={() => setSport("all")} />
        {categories.map((c) => (
          <Radio key={c.slug} name="sport" label={`${c.icon} ${c.name}`} checked={sport === c.slug} onChange={() => setSport(c.slug)} />
        ))}
      </FilterGroup>

      <FilterGroup title="Marca">
        {brands.map((b) => (
          <Check key={b} label={b} checked={brandSel.includes(b)} onChange={() => toggleBrand(b)} />
        ))}
      </FilterGroup>

      <FilterGroup title="Nivel">
        <Radio name="level" label="Todos" checked={level === "all"} onChange={() => setLevel("all")} />
        <Radio name="level" label="Amateur" checked={level === "amateur"} onChange={() => setLevel("amateur")} />
        <Radio name="level" label="Profesional" checked={level === "profesional"} onChange={() => setLevel("profesional")} />
      </FilterGroup>

      <FilterGroup title="Uso">
        <Radio name="use" label="Todos" checked={use === "all"} onChange={() => setUse("all")} />
        <Radio name="use" label="Indoor" checked={use === "indoor"} onChange={() => setUse("indoor")} />
        <Radio name="use" label="Outdoor" checked={use === "outdoor"} onChange={() => setUse("outdoor")} />
      </FilterGroup>

      <FilterGroup title={`Precio máx: ${formatCLP(maxPrice)}`}>
        <input type="range" min={MIN} max={MAX} step={1000} value={maxPrice}
          onChange={(e) => setMaxPrice(Number(e.target.value))} className="w-full accent-balon" />
        <div className="flex justify-between text-xs text-neutral-400"><span>{formatCLP(MIN)}</span><span>{formatCLP(MAX)}</span></div>
      </FilterGroup>

      <button onClick={reset} className="btn-ghost w-full py-2.5 text-sm">Limpiar filtros</button>
    </div>
  );

  return (
    <div className="container-db py-8">
      {/* encabezado */}
      <div className="mb-6">
        <h1 className="display text-4xl md:text-5xl">{cat ? `${cat.icon} ${cat.name}` : "Todo el catálogo"}</h1>
        <p className="mt-1 text-neutral-500">{filtered.length} producto{filtered.length !== 1 && "s"}</p>
      </div>

      <div className="flex flex-col gap-8 lg:flex-row">
        {/* sidebar filtros (desktop) */}
        <aside className="hidden w-64 shrink-0 lg:block">{Filters}</aside>

        <div className="flex-1">
          {/* barra: filtros móvil + sort */}
          <div className="mb-5 flex items-center justify-between gap-3">
            <button onClick={() => setOpen(true)} className="btn-ghost px-4 py-2 text-sm lg:hidden">⚙ Filtros</button>
            <label className="ml-auto flex items-center gap-2 text-sm text-neutral-600">
              Ordenar por
              <select value={sort} onChange={(e) => setSort(e.target.value as Sort)}
                className="rounded-lg border border-black/15 bg-white px-3 py-2 text-sm outline-none focus:border-balon">
                <option value="relevancia">Relevancia</option>
                <option value="precio-asc">Precio: menor a mayor</option>
                <option value="precio-desc">Precio: mayor a menor</option>
                <option value="novedades">Novedades</option>
              </select>
            </label>
          </div>

          {filtered.length === 0 ? (
            <div className="grid place-items-center rounded-2xl border border-dashed border-black/15 py-20 text-center text-neutral-500">
              <span className="text-4xl">🔍</span>
              <p className="mt-3">No hay productos con estos filtros.</p>
              <button onClick={reset} className="btn-primary mt-4 px-5 py-2.5 text-sm">Limpiar filtros</button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
              {filtered.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </div>
      </div>

      {/* drawer filtros móvil */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-0 h-full w-80 max-w-[85%] overflow-y-auto bg-white p-5 animate-slide-in">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-xl">Filtros</h2>
              <button onClick={() => setOpen(false)} className="grid h-9 w-9 place-items-center rounded-full hover:bg-neutral-100">✕</button>
            </div>
            {Filters}
            <button onClick={() => setOpen(false)} className="btn-primary mt-5 w-full py-3">Ver {filtered.length} productos</button>
          </div>
        </div>
      )}
    </div>
  );
}

function FilterGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="mb-2 font-head text-sm font-bold uppercase tracking-wide text-carbon">{title}</h3>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}
function Radio({ name, label, checked, onChange }: { name: string; label: string; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-neutral-600 hover:text-carbon">
      <input type="radio" name={name} checked={checked} onChange={onChange} className="accent-balon" /> {label}
    </label>
  );
}
function Check({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-neutral-600 hover:text-carbon">
      <input type="checkbox" checked={checked} onChange={onChange} className="accent-balon" /> {label}
    </label>
  );
}
