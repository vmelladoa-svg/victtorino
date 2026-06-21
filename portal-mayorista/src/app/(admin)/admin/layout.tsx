"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/admin",               label: "Resumen",      exact: true  },
  { href: "/admin/comerciantes",  label: "Comerciantes", exact: false },
  { href: "/admin/pagos",         label: "Pagos",        exact: false },
  { href: "/admin/ventas",        label: "Ventas",       exact: false },
  { href: "/admin/pedidos",       label: "Pedidos",      exact: false },
];

function AdminSidebar() {
  const pathname = usePathname();

  function isActive(href: string, exact: boolean) {
    return exact ? pathname === href : pathname.startsWith(href);
  }

  return (
    <aside className="adm-side">
      <div className="adm-brand">
        <span className="adm-logo">
          <Image
            src="/logo-clean.png"
            alt="Trade Global"
            width={38}
            height={38}
            style={{ borderRadius: "10px", objectFit: "contain" }}
          />
        </span>
        <span className="adm-brand-txt">
          <strong>Trade Global</strong>
          <small>Back-office</small>
        </span>
      </div>

      <nav className="adm-nav">
        {NAV.map((n) => (
          <Link
            key={n.href}
            href={n.href}
            className={"adm-navi" + (isActive(n.href, n.exact) ? " is-on" : "")}
            style={{ textDecoration: "none" }}
          >
            <span>{n.label}</span>
          </Link>
        ))}
      </nav>

      <div className="adm-side-foot">
        <Link
          href="/catalogo"
          className="adm-side-link"
          style={{ textDecoration: "none" }}
        >
          Ver tienda
        </Link>
      </div>
    </aside>
  );
}

export default function AdminShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="adm">
      <AdminSidebar />
      <div className="adm-main">
        <div className="adm-scroll">{children}</div>
      </div>
    </div>
  );
}
