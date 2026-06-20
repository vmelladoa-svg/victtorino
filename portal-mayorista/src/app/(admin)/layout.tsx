import "./admin.css";

// El guard de /admin está en src/proxy.ts (verifica rol admin antes de renderizar).
// Este layout solo importa los estilos compartidos del back-office.
export default function AdminGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
