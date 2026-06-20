"use client";
import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useCart } from "@/lib/store";
import { formatCLP, discountPct } from "@/lib/format";
import type { Product } from "@/data/products";

export default function ProductDetail({ product }: { product: Product }) {
  const router = useRouter();
  const add = useCart((s) => s.add);
  const [img, setImg] = useState(0);
  const [qty, setQty] = useState(1);
  const [color, setColor] = useState(product.colors?.[0]);
  const [size, setSize] = useState(product.sizes?.[0]);
  const off = discountPct(product.price, product.compareAt);

  const opts = { qty, color, size };
  const buyNow = () => {
    add(product, opts);
    router.push("/checkout");
  };

  return (
    <div className="grid gap-10 md:grid-cols-2">
      {/* galería */}
      <div>
        <div className="group relative aspect-square overflow-hidden rounded-3xl border border-black/10 bg-neutral-100">
          <Image
            src={product.images[img]}
            alt={product.name}
            fill
            sizes="(max-width:768px) 100vw, 50vw"
            className="object-cover transition-transform duration-500 group-hover:scale-110"
            priority
          />
          {off && <span className="badge absolute left-4 top-4 bg-balon text-white">-{off}%</span>}
        </div>
        {product.images.length > 1 && (
          <div className="mt-3 flex gap-3">
            {product.images.map((src, i) => (
              <button
                key={i}
                onClick={() => setImg(i)}
                className={`relative h-20 w-20 overflow-hidden rounded-xl border-2 transition ${i === img ? "border-balon" : "border-transparent opacity-70 hover:opacity-100"}`}
              >
                <Image src={src} alt="" fill sizes="80px" className="object-cover" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* info */}
      <div>
        <span className="text-sm font-semibold uppercase tracking-wide text-neutral-400">{product.brand}</span>
        <h1 className="display mt-1 text-4xl md:text-5xl">{product.name}</h1>
        <div className="mt-2 flex items-center gap-2 text-sm text-neutral-500">
          <span className="text-balon">{"★".repeat(Math.round(product.rating))}</span>
          {product.rating} · {product.reviews} reseñas
        </div>

        <div className="mt-5 flex items-end gap-3">
          <span className="font-display text-4xl text-carbon">{formatCLP(product.price)}</span>
          {product.compareAt && <span className="mb-1.5 text-lg text-neutral-400 line-through">{formatCLP(product.compareAt)}</span>}
        </div>
        <p className="mt-1 text-sm text-cancha">o 3 cuotas sin interés de {formatCLP(product.price / 3)}</p>

        <p className="mt-5 text-neutral-600">{product.description}</p>

        {/* variantes color */}
        {product.colors && (
          <div className="mt-6">
            <span className="text-sm font-semibold">Color: <span className="font-normal text-neutral-500">{color}</span></span>
            <div className="mt-2 flex flex-wrap gap-2">
              {product.colors.map((c) => (
                <button key={c} onClick={() => setColor(c)}
                  className={`rounded-full border px-4 py-1.5 text-sm transition ${color === c ? "border-balon bg-balon-50 text-balon" : "border-black/15 hover:border-carbon"}`}>
                  {c}
                </button>
              ))}
            </div>
          </div>
        )}
        {/* variantes talla */}
        {product.sizes && (
          <div className="mt-5">
            <span className="text-sm font-semibold">Talla: <span className="font-normal text-neutral-500">{size}</span></span>
            <div className="mt-2 flex flex-wrap gap-2">
              {product.sizes.map((s) => (
                <button key={s} onClick={() => setSize(s)}
                  className={`min-w-11 rounded-lg border px-3 py-2 text-sm transition ${size === s ? "border-balon bg-balon-50 text-balon" : "border-black/15 hover:border-carbon"}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* cantidad + acciones */}
        <div className="mt-7 flex items-center gap-3">
          <div className="flex items-center rounded-xl border border-black/15">
            <button onClick={() => setQty((q) => Math.max(1, q - 1))} className="grid h-12 w-12 place-items-center text-lg">−</button>
            <span className="w-10 text-center font-semibold">{qty}</span>
            <button onClick={() => setQty((q) => Math.min(product.stock, q + 1))} className="grid h-12 w-12 place-items-center text-lg">+</button>
          </div>
          <button onClick={() => add(product, opts)} className="btn-primary flex-1 py-3.5">Agregar al carrito</button>
        </div>
        <button onClick={buyNow} className="btn-dark mt-3 w-full py-3.5">Comprar ahora</button>

        {/* stock / envío */}
        <div className="mt-6 space-y-2 rounded-2xl border border-black/10 bg-neutral-50 p-4 text-sm">
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${product.stock > 5 ? "bg-cancha" : "bg-balon"}`} />
            {product.stock > 5 ? "En stock — listo para despachar" : `¡Quedan solo ${product.stock} unidades!`}
          </div>
          <div className="flex items-center gap-2 text-neutral-600">🚚 Envío 24–48h hábiles · gratis sobre {formatCLP(39990)}</div>
          <div className="flex items-center gap-2 text-neutral-600">🔒 Pago seguro con Webpay · 🛡️ Garantía de producto original</div>
        </div>

        {/* especificaciones */}
        <div className="mt-8">
          <h2 className="font-head text-lg font-bold">Especificaciones</h2>
          <dl className="mt-3 overflow-hidden rounded-2xl border border-black/10">
            {product.specs.map((s, i) => (
              <div key={s.label} className={`flex justify-between px-4 py-2.5 text-sm ${i % 2 ? "bg-neutral-50" : "bg-white"}`}>
                <dt className="text-neutral-500">{s.label}</dt>
                <dd className="font-medium">{s.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
}
