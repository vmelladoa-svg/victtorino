"use client";
import Image from "next/image";
import Link from "next/link";
import { useCart } from "@/lib/store";
import { formatCLP, discountPct } from "@/lib/format";
import type { Product, Badge } from "@/data/products";

const badgeStyle: Record<Badge, string> = {
  "Más vendido": "bg-carbon text-white",
  Nuevo: "bg-azulina text-white",
  Oferta: "bg-balon text-white",
  Profesional: "bg-cancha text-white",
};

export default function ProductCard({ product }: { product: Product }) {
  const add = useCart((s) => s.add);
  const off = discountPct(product.price, product.compareAt);
  const hasAlt = product.images.length > 1;

  return (
    <div className="group relative flex flex-col overflow-hidden rounded-2xl border border-black/10 bg-white shadow-card transition-all duration-300 hover:-translate-y-1 hover:shadow-card-hover">
      <Link href={`/producto/${product.slug}`} className="relative block aspect-square overflow-hidden bg-neutral-100">
        <Image
          src={product.images[0]}
          alt={product.name}
          fill
          sizes="(max-width:768px) 50vw, 25vw"
          className={`object-cover transition-opacity duration-300 ${hasAlt ? "group-hover:opacity-0" : ""}`}
        />
        {hasAlt && (
          <Image
            src={product.images[1]}
            alt=""
            fill
            sizes="(max-width:768px) 50vw, 25vw"
            className="object-cover opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          />
        )}
        {/* badges */}
        <div className="absolute left-3 top-3 flex flex-col gap-1.5">
          {product.badges.map((b) => (
            <span key={b} className={`badge ${badgeStyle[b]}`}>{b}</span>
          ))}
        </div>
        {off && (
          <span className="badge absolute right-3 top-3 bg-white text-balon shadow-card">-{off}%</span>
        )}
      </Link>

      <div className="flex flex-1 flex-col p-4">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400">{product.brand}</span>
        <Link href={`/producto/${product.slug}`} className="mt-0.5 line-clamp-2 font-head font-semibold leading-snug hover:text-balon">
          {product.name}
        </Link>
        <div className="mt-1 flex items-center gap-1 text-xs text-neutral-500">
          <span className="text-balon">★</span> {product.rating} <span className="text-neutral-300">·</span> {product.reviews} reseñas
        </div>

        <div className="mt-3 flex items-end gap-2">
          <span className="font-display text-2xl text-carbon">{formatCLP(product.price)}</span>
          {product.compareAt && (
            <span className="mb-1 text-sm text-neutral-400 line-through">{formatCLP(product.compareAt)}</span>
          )}
        </div>

        <button
          onClick={() => add(product, { color: product.colors?.[0], size: product.sizes?.[0] })}
          className="btn-primary mt-3 w-full py-2.5 text-sm"
        >
          Agregar al carrito
        </button>
      </div>
    </div>
  );
}
