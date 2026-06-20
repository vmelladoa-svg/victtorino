import Image from "next/image";
import Link from "next/link";

export const metadata = { title: "Página no encontrada" };

export default function NotFound() {
  return (
    <main className="nf-wrap">
      <Image src="/logo.png" alt="Trade" width={72} height={54} priority />
      <span className="nf-code">404</span>
      <h1 style={{ fontSize: 26 }}>No encontramos esta página</h1>
      <p>
        Puede que el enlace esté roto o que la página se haya movido. Vuelve al inicio y sigue
        explorando nuestro catálogo.
      </p>
      <Link className="btn btn-primary" href="/">
        Volver al inicio
      </Link>
    </main>
  );
}
