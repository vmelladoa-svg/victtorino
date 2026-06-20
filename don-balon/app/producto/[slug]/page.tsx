import { notFound } from "next/navigation";
import Link from "next/link";
import ProductDetail from "@/components/ProductDetail";
import ProductCard from "@/components/ProductCard";
import { products, getProductBySlug, getRelated } from "@/data/products";

export function generateStaticParams() {
  return products.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }) {
  const p = getProductBySlug(params.slug);
  return { title: p ? `${p.name} — Don Balón` : "Producto — Don Balón" };
}

export default function ProductoPage({ params }: { params: { slug: string } }) {
  const product = getProductBySlug(params.slug);
  if (!product) notFound();
  const related = getRelated(product);

  return (
    <div className="container-db py-8">
      {/* breadcrumb */}
      <nav className="mb-6 text-sm text-neutral-500">
        <Link href="/" className="hover:text-balon">Inicio</Link> ·{" "}
        <Link href={`/catalogo?sport=${product.sport}`} className="capitalize hover:text-balon">{product.sport}</Link> ·{" "}
        <span className="text-carbon">{product.name}</span>
      </nav>

      <ProductDetail product={product} />

      {/* relacionados */}
      {related.length > 0 && (
        <section className="mt-16">
          <h2 className="display mb-6 text-3xl">También te puede gustar</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {related.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}
    </div>
  );
}
