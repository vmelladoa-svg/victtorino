import { prisma } from "@/lib/db";

// Rate-limit de ventana fija usando la propia base (no Upstash). El UPSERT atomico
// incrementa o reinicia el contador segun si la ventana venció; dos requests
// concurrentes no se pisan. Devuelve true si el intento está PERMITIDO.
// ponytail: fail-open — si la BD falla, dejamos pasar; el rate-limit nunca debe
//           tumbar el login. Brute-force real igual choca con bcrypt + revalidación.
export async function permitir(
  key: string,
  limite: number,
  ventanaMin: number,
): Promise<boolean> {
  try {
    const rows = await prisma.$queryRaw<{ count: number | bigint }[]>`
      INSERT INTO "RateLimit" ("key", "count", "resetAt")
      VALUES (${key}, 1, now() + make_interval(mins => ${ventanaMin}))
      ON CONFLICT ("key") DO UPDATE SET
        "count" = CASE WHEN "RateLimit"."resetAt" < now() THEN 1 ELSE "RateLimit"."count" + 1 END,
        "resetAt" = CASE WHEN "RateLimit"."resetAt" < now() THEN now() + make_interval(mins => ${ventanaMin}) ELSE "RateLimit"."resetAt" END
      RETURNING "count"`;
    return Number(rows[0]?.count ?? 1) <= limite;
  } catch (e) {
    console.error("[rate-limit] error, se permite por defecto:", e);
    return true;
  }
}

// IP del cliente desde los headers (Vercel pone x-forwarded-for). "desconocida"
// si no hay; en prod siempre existe.
export function ipDe(req: Request): string {
  const xff = req.headers.get("x-forwarded-for");
  return xff?.split(",")[0]?.trim() || req.headers.get("x-real-ip") || "desconocida";
}
