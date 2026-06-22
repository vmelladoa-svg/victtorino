import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt", maxAge: 60 * 60 * 24 * 7 }, // 7 días
  providers: [
    Credentials({
      credentials: { email: {}, password: {} },
      async authorize(c) {
        const email = String(c?.email ?? "").toLowerCase();
        const pass = String(c?.password ?? "");

        // Admin via env vars. Clave en texto plano en el .env (almacén de
        // secretos del servidor) para evitar la expansión de "$" de @next/env
        // sobre un hash bcrypt. Las claves de comerciantes SÍ van hasheadas en la BD.
        if (email === process.env.ADMIN_EMAIL?.toLowerCase()) {
          const admPass = process.env.ADMIN_PASSWORD ?? "";
          if (admPass && pass === admPass)
            return {
              id: "admin",
              email,
              name: "Admin",
              rol: "admin",
              estado: "aprobado",
            } as any;
          return null;
        }

        // Comerciante via DB
        const u = await prisma.comerciante.findUnique({ where: { email } });
        if (!u || !(await bcrypt.compare(pass, u.clave))) return null;
        return {
          id: u.id,
          email: u.email,
          name: u.nombre,
          rol: "comerciante",
          estado: u.estado,
        } as any;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        (token as any).rol = (user as any).rol;
        (token as any).estado = (user as any).estado;
        (token as any).uid = (user as any).id;
      }
      // Revalidar el estado del comerciante contra la BD en cada request: si fue
      // rechazado o eliminado, deja de operar SIN esperar a que cierre sesión.
      // El admin es por env var, no toca BD.
      if ((token as any).rol === "comerciante" && (token as any).uid) {
        const c = await prisma.comerciante.findUnique({
          where: { id: (token as any).uid },
          select: { estado: true },
        });
        (token as any).estado = c ? c.estado : "eliminado";
      }
      return token;
    },
    session({ session, token }) {
      (session.user as any).rol = (token as any).rol;
      (session.user as any).estado = (token as any).estado;
      (session.user as any).id = (token as any).uid;
      return session;
    },
  },
});
