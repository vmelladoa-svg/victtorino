import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt" },
  providers: [
    Credentials({
      credentials: { email: {}, password: {} },
      async authorize(c) {
        const email = String(c?.email ?? "").toLowerCase();
        const pass = String(c?.password ?? "");

        // Admin via env vars
        if (email === process.env.ADMIN_EMAIL?.toLowerCase()) {
          const hash = process.env.ADMIN_PASSWORD_HASH ?? "";
          if (await bcrypt.compare(pass, hash))
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
    jwt({ token, user }) {
      if (user) {
        (token as any).rol = (user as any).rol;
        (token as any).estado = (user as any).estado;
        (token as any).uid = (user as any).id;
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
