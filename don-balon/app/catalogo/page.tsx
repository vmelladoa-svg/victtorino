import { Suspense } from "react";
import Catalog from "@/components/Catalog";

export default function CatalogoPage() {
  return (
    <Suspense fallback={<div className="container-db py-20 text-center text-neutral-400">Cargando catálogo…</div>}>
      <Catalog />
    </Suspense>
  );
}
