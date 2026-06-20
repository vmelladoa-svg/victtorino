import Link from "next/link";
import Image from "next/image";
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const s = await auth();
  if ((s?.user as any)?.rol !== "admin") redirect("/login");

  return (
    <div className="adm">
      <AdminSidebar />
      <div className="adm-main">
        <div className="adm-scroll">{children}</div>
      </div>
    </div>
  );
}

function AdminSidebar() {
  const nav = [
    { href: "/admin",              label: "Resumen"       },
    { href: "/admin/comerciantes", label: "Comerciantes"  },
    { href: "/admin/pagos",        label: "Pagos"         },
    { href: "/admin/pedidos",      label: "Pedidos"       },
    { href: "/admin/catalogo",     label: "Catálogo"      },
  ];

  return (
    <aside className="adm-side">
      <div className="adm-brand">
        <span className="adm-logo">
          <Image src="/logo-clean.png" alt="Trade Global" width={38} height={38} style={{ borderRadius: "10px", objectFit: "contain" }} />
        </span>
        <span className="adm-brand-txt">
          <strong>Trade Global</strong>
          <small>Back-office</small>
        </span>
      </div>
      <nav className="adm-nav">
        {nav.map((n) => (
          <Link key={n.href} href={n.href} className="adm-navi" style={{ textDecoration: "none" }}>
            <span>{n.label}</span>
          </Link>
        ))}
      </nav>
      <div className="adm-side-foot">
        <Link href="/catalogo" className="adm-side-link" style={{ textDecoration: "none" }}>
          Ver tienda
        </Link>
      </div>
    </aside>
  );
}