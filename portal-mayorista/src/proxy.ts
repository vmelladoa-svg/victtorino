import { auth } from "@/auth";
import type { NextAuthRequest } from "next-auth";

// auth() wraps the handler and populates req.auth from the JWT token
const guardHandler = auth((req: NextAuthRequest) => {
  const u = req.auth?.user as any;
  const p = req.nextUrl.pathname;

  if (p.startsWith("/admin") && u?.rol !== "admin")
    return Response.redirect(new URL("/login", req.url));

  if (
    (p.startsWith("/catalogo") ||
      p.startsWith("/checkout") ||
      p.startsWith("/mis-pedidos")) &&
    !u
  )
    return Response.redirect(new URL("/login", req.url));
});

// Next.js 16 expects named "proxy" export (or default)
export const proxy = guardHandler;
export default guardHandler;

export const config = {
  matcher: [
    "/admin/:path*",
    "/catalogo/:path*",
    "/checkout/:path*",
    "/mis-pedidos/:path*",
  ],
};
