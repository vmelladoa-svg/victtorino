# Portal Mayorista (Comercial Solutions) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el portal B2B mayorista (tienda + panel admin) que convierte la maqueta de Claude Design en un sitio real con backend, sobre `comercialsolutions.cl`.

**Architecture:** App única **Next.js (App Router, TypeScript)** que sirve tienda (comerciante) y panel (admin) separados por rol. Datos en **Postgres (Neon)** vía **Prisma**. Login con **Auth.js v5** (credentials + bcrypt). Comprobantes en **Vercel Blob**. Avisos por **WhatsApp (CallMeBot)**. Catálogo se carga desde `mayorista_catalogo.xlsx` con un seed. La UI se adapta de la maqueta existente del proyecto "Venta por Mayor" en Claude Design.

**Tech Stack:** Next.js 15, TypeScript, Prisma, PostgreSQL (Neon), Auth.js v5, bcryptjs, @vercel/blob, xlsx (SheetJS), Vitest. Deploy en Vercel.

## Global Constraints
- Modelo **dropship a pedido**: sin inventario, sin descuento de stock. Todo "disponible".
- **Proveedor único = AlilaTop**. La OC usa `codigo_alila`. Lead time 1 día.
- **Idioma de toda la UI: español de Chile** (sin voseo argentino: nada de "tenés/querés/podés").
- Precios **solo visibles para comerciante con `estado = aprobado`**. Sin login no se ve nada.
- **Precio por tramo según cantidad de cada producto:** 1–5 u → `precio_t1` · 6–20 u → `precio_t2` · 21+ u → `precio_t3`.
- Datos de transferencia (mostrados en checkout): **Scotiabank, Cuenta Corriente, N° 000993556831, Trade Global Solutions SpA, RUT 78.103.712-5**.
- WhatsApp admin: CallMeBot `phone=56996953815`, `apikey=5759352`, texto plano sin emojis.
- Si CallMeBot falla, el pedido **igual se persiste** (el aviso nunca bloquea la venta).
- Moneda CLP, enteros (sin decimales).

---

## File Structure
```
portal-mayorista/
  prisma/schema.prisma            # modelos: Comerciante, Producto, Pedido, PedidoItem, OC
  prisma/seed.ts                  # importa mayorista_catalogo.xlsx → Producto
  src/lib/precios.ts              # regla de tramos (lógica pura)
  src/lib/pedido-estado.ts        # máquina de estados del pedido (lógica pura)
  src/lib/whatsapp.ts             # aviso CallMeBot (no bloqueante)
  src/lib/db.ts                   # cliente Prisma singleton
  src/auth.ts                     # config Auth.js (credentials + roles)
  src/middleware.ts               # guard de rutas por rol/estado
  src/app/(comerciante)/...       # registro, login, catalogo, carrito, checkout, mis-pedidos
  src/app/(admin)/admin/...       # comerciantes, pagos, pedidos, oc, despacho
  src/app/api/...                 # route handlers (pedidos, comprobante, admin acciones)
  tests/precios.test.ts
  tests/pedido-estado.test.ts
```

---

### Task 1: Bootstrap del proyecto y dependencias

**Files:**
- Create: `portal-mayorista/` (proyecto Next.js)
- Create: `portal-mayorista/.env.example`

**Interfaces:**
- Produces: proyecto Next.js compilando; scripts `dev`, `build`, `test`.

- [ ] **Step 1: Crear app Next.js (TypeScript, App Router)**

```bash
npx create-next-app@latest portal-mayorista --ts --app --eslint --src-dir --no-tailwind --import-alias "@/*"
cd portal-mayorista
npm i prisma @prisma/client next-auth@beta bcryptjs @vercel/blob xlsx
npm i -D vitest @types/bcryptjs tsx
npx prisma init
```

- [ ] **Step 2: Configurar script de test en package.json**

Agregar a `"scripts"`: `"test": "vitest run"`, `"seed": "tsx prisma/seed.ts"`.

- [ ] **Step 3: Crear `.env.example`**

```
DATABASE_URL="postgres://..."        # Neon
AUTH_SECRET="..."                    # openssl rand -base64 32
BLOB_READ_WRITE_TOKEN="..."          # Vercel Blob
WA_PHONE="56996953815"
WA_KEY="5759352"
ADMIN_EMAIL="victor@comercialsolutions.cl"
ADMIN_PASSWORD_HASH="..."            # bcrypt hash inicial
```

- [ ] **Step 4: Verificar build**

Run: `npm run build`
Expected: compila sin errores.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: bootstrap portal mayorista (next.js + deps)"
```

---

### Task 2: Esquema de base de datos (Prisma)

**Files:**
- Modify: `prisma/schema.prisma`
- Create: `src/lib/db.ts`

**Interfaces:**
- Produces: modelos `Comerciante`, `Producto`, `Pedido`, `PedidoItem`, `OC`; enums `EstadoComerciante`, `EstadoPedido`; cliente `prisma`.

- [ ] **Step 1: Definir el schema**

```prisma
generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

enum EstadoComerciante { pendiente aprobado rechazado }
enum EstadoPedido { pago_en_validacion validado oc_generada despachado entregado rechazado }

model Comerciante {
  id        String   @id @default(cuid())
  nombre    String
  email     String   @unique
  clave     String
  rutEmpresa String
  giro      String
  telefono  String
  estado    EstadoComerciante @default(pendiente)
  pedidos   Pedido[]
  createdAt DateTime @default(now())
}

model Producto {
  id          String  @id @default(cuid())
  codigoAlila String  @unique
  nombre      String
  categoria   String?
  costo       Int?
  precioT1    Int?
  precioT2    Int?
  precioT3    Int?
  unidCaja    Int?
  minCompra   Int     @default(1)
  fotoUrl     String?
  link1688    String?
  activo      Boolean @default(true)
  items       PedidoItem[]
}

model Pedido {
  id            String   @id @default(cuid())
  comerciante   Comerciante @relation(fields: [comercianteId], references: [id])
  comercianteId String
  estado        EstadoPedido @default(pago_en_validacion)
  total         Int
  region        String
  direccion     String
  comprobanteUrl String?
  transportista String?
  tracking      String?
  items         PedidoItem[]
  oc            OC?
  createdAt     DateTime @default(now())
}

model PedidoItem {
  id           String  @id @default(cuid())
  pedido       Pedido  @relation(fields: [pedidoId], references: [id])
  pedidoId     String
  producto     Producto @relation(fields: [productoId], references: [id])
  productoId   String
  cantidad     Int
  precioAplicado Int
  subtotal     Int
}

model OC {
  id        String   @id @default(cuid())
  pedido    Pedido   @relation(fields: [pedidoId], references: [id])
  pedidoId  String   @unique
  proveedor String   @default("AlilaTop")
  numeroOc  String   @unique
  estado    String   @default("emitida")
  createdAt DateTime @default(now())
}
```

- [ ] **Step 2: Cliente Prisma singleton** (`src/lib/db.ts`)

```ts
import { PrismaClient } from "@prisma/client";
const g = globalThis as unknown as { prisma?: PrismaClient };
export const prisma = g.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== "production") g.prisma = prisma;
```

- [ ] **Step 3: Generar y migrar**

Run: `npx prisma migrate dev --name init`
Expected: migración creada, tablas en Neon.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: esquema de datos (prisma)"
```

---

### Task 3: Regla de precios por tramo (lógica pura, TDD)

**Files:**
- Create: `src/lib/precios.ts`
- Test: `tests/precios.test.ts`

**Interfaces:**
- Produces: `precioPorCantidad(p: {precioT1,precioT2,precioT3}, cantidad: number): number` y `subtotalLinea(p, cantidad): number`.

- [ ] **Step 1: Test que falla**

```ts
import { describe, it, expect } from "vitest";
import { precioPorCantidad, subtotalLinea } from "@/lib/precios";
const P = { precioT1: 10000, precioT2: 8800, precioT3: 8000 };

describe("precioPorCantidad", () => {
  it("1-5 u usa T1", () => expect(precioPorCantidad(P, 1)).toBe(10000));
  it("borde 5 usa T1", () => expect(precioPorCantidad(P, 5)).toBe(10000));
  it("6-20 u usa T2", () => expect(precioPorCantidad(P, 6)).toBe(8800));
  it("borde 20 usa T2", () => expect(precioPorCantidad(P, 20)).toBe(8800));
  it("21+ u usa T3", () => expect(precioPorCantidad(P, 21)).toBe(8000));
  it("subtotal = precio x cantidad", () => expect(subtotalLinea(P, 6)).toBe(52800));
});
```

- [ ] **Step 2: Correr y ver fallar**

Run: `npm test -- precios`
Expected: FAIL ("precioPorCantidad is not a function").

- [ ] **Step 3: Implementar**

```ts
export type TramoPrecio = { precioT1: number | null; precioT2: number | null; precioT3: number | null };

export function precioPorCantidad(p: TramoPrecio, cantidad: number): number {
  if (cantidad >= 21 && p.precioT3 != null) return p.precioT3;
  if (cantidad >= 6 && p.precioT2 != null) return p.precioT2;
  if (p.precioT1 != null) return p.precioT1;
  throw new Error("Producto sin precio");
}
export function subtotalLinea(p: TramoPrecio, cantidad: number): number {
  return precioPorCantidad(p, cantidad) * cantidad;
}
```

- [ ] **Step 4: Correr y ver pasar**

Run: `npm test -- precios`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: regla de precios por tramo + tests"
```

---

### Task 4: Máquina de estados del pedido (lógica pura, TDD)

**Files:**
- Create: `src/lib/pedido-estado.ts`
- Test: `tests/pedido-estado.test.ts`

**Interfaces:**
- Consumes: enum `EstadoPedido` (strings del schema).
- Produces: `puedeTransicionar(de, a): boolean` y `SIGUIENTE: Record<estado, estado[]>`.

- [ ] **Step 1: Test que falla**

```ts
import { describe, it, expect } from "vitest";
import { puedeTransicionar } from "@/lib/pedido-estado";
describe("estados", () => {
  it("validar tras pago", () => expect(puedeTransicionar("pago_en_validacion","validado")).toBe(true));
  it("rechazar pago", () => expect(puedeTransicionar("pago_en_validacion","rechazado")).toBe(true));
  it("no se genera OC sin validar", () => expect(puedeTransicionar("pago_en_validacion","oc_generada")).toBe(false));
  it("OC tras validar", () => expect(puedeTransicionar("validado","oc_generada")).toBe(true));
  it("despacho tras OC", () => expect(puedeTransicionar("oc_generada","despachado")).toBe(true));
  it("entrega tras despacho", () => expect(puedeTransicionar("despachado","entregado")).toBe(true));
  it("no salta de validado a despachado", () => expect(puedeTransicionar("validado","despachado")).toBe(false));
});
```

- [ ] **Step 2: Correr y ver fallar** — Run: `npm test -- pedido-estado` → FAIL.

- [ ] **Step 3: Implementar**

```ts
export type EstadoPedido = "pago_en_validacion"|"validado"|"oc_generada"|"despachado"|"entregado"|"rechazado";
export const SIGUIENTE: Record<EstadoPedido, EstadoPedido[]> = {
  pago_en_validacion: ["validado","rechazado"],
  validado: ["oc_generada"],
  oc_generada: ["despachado"],
  despachado: ["entregado"],
  entregado: [],
  rechazado: [],
};
export function puedeTransicionar(de: EstadoPedido, a: EstadoPedido): boolean {
  return SIGUIENTE[de]?.includes(a) ?? false;
}
```

- [ ] **Step 4: Correr y ver pasar** — Run: `npm test -- pedido-estado` → PASS.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: máquina de estados del pedido + tests"`

---

### Task 5: Seed del catálogo desde Excel

**Files:**
- Create: `prisma/seed.ts`
- Copy: `mayorista_catalogo.xlsx` a `portal-mayorista/data/mayorista_catalogo.xlsx`

**Interfaces:**
- Consumes: columnas del Excel (Código, Nombre, Categoría, Costo 1688 CLP, "1-5 u (x2,5)", "6-20 u (x2,2)", "21+ u (x2,0)", Link 1688, Foto principal).
- Produces: filas en `Producto` (upsert por `codigoAlila`).

- [ ] **Step 1: Implementar seed**

```ts
import { PrismaClient } from "@prisma/client";
import * as XLSX from "xlsx";
const prisma = new PrismaClient();
const num = (v: any) => { const n = parseInt(String(v).replace(/\D/g, ""), 10); return Number.isFinite(n) ? n : null; };

async function main() {
  const wb = XLSX.readFile("data/mayorista_catalogo.xlsx");
  const rows = XLSX.utils.sheet_to_json<any>(wb.Sheets[wb.SheetNames[0]]);
  let n = 0;
  for (const r of rows) {
    const codigo = String(r["Código"] ?? "").trim();
    if (!codigo) continue;
    await prisma.producto.upsert({
      where: { codigoAlila: codigo },
      update: {},
      create: {
        codigoAlila: codigo,
        nombre: String(r["Nombre"] ?? "").trim(),
        categoria: r["Categoría"] ? String(r["Categoría"]) : null,
        costo: num(r["Costo 1688 CLP"]),
        precioT1: num(r["1-5 u  (x2,5)"]),
        precioT2: num(r["6-20 u  (x2,2)"]),
        precioT3: num(r["21+ u  (x2,0)"]),
        link1688: r["Link 1688"] ? String(r["Link 1688"]) : null,
        fotoUrl: r["Foto principal"] ? String(r["Foto principal"]) : null,
      },
    });
    n++;
  }
  console.log(`Sembrados ${n} productos`);
}
main().finally(() => prisma.$disconnect());
```

- [ ] **Step 2: Correr el seed**

Run: `npm run seed`
Expected: "Sembrados 117 productos".

- [ ] **Step 3: Verificar conteo**

Run: `npx prisma studio` (o una query) → tabla Producto con 117 filas.

- [ ] **Step 4: Commit**

```bash
git add prisma/seed.ts && git commit -m "feat: seed del catálogo desde Excel (117 productos)"
```

> Nota: las "Foto principal" del Excel son URLs de la app Alila (pueden expirar). En v1 se usan tal cual; migrar fotos a Blob es mejora futura.

---

### Task 6: Autenticación (Auth.js + roles)

**Files:**
- Create: `src/auth.ts`, `src/app/api/auth/[...nextauth]/route.ts`
- Create: `src/middleware.ts`
- Create: `src/app/api/registro/route.ts`

**Interfaces:**
- Consumes: `prisma`, `Comerciante`.
- Produces: sesión con `{ id, rol: "admin"|"comerciante", estado }`; `auth()` helper; guard de rutas.

- [ ] **Step 1: Config Auth.js (credentials)** (`src/auth.ts`)

```ts
import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt" },
  providers: [Credentials({
    credentials: { email: {}, password: {} },
    async authorize(c) {
      const email = String(c?.email ?? "").toLowerCase();
      const pass = String(c?.password ?? "");
      // admin por env
      if (email === process.env.ADMIN_EMAIL?.toLowerCase()) {
        if (await bcrypt.compare(pass, process.env.ADMIN_PASSWORD_HASH ?? ""))
          return { id: "admin", email, name: "Admin", rol: "admin", estado: "aprobado" } as any;
        return null;
      }
      const u = await prisma.comerciante.findUnique({ where: { email } });
      if (!u || !(await bcrypt.compare(pass, u.clave))) return null;
      return { id: u.id, email: u.email, name: u.nombre, rol: "comerciante", estado: u.estado } as any;
    },
  })],
  callbacks: {
    jwt({ token, user }) { if (user) { (token as any).rol = (user as any).rol; (token as any).estado = (user as any).estado; (token as any).uid = (user as any).id; } return token; },
    session({ session, token }) { (session.user as any).rol = (token as any).rol; (session.user as any).estado = (token as any).estado; (session.user as any).id = (token as any).uid; return session; },
  },
});
```

- [ ] **Step 2: Route handler** (`src/app/api/auth/[...nextauth]/route.ts`)

```ts
import { handlers } from "@/auth";
export const { GET, POST } = handlers;
```

- [ ] **Step 3: Registro de comerciante** (`src/app/api/registro/route.ts`)

```ts
import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  const b = await req.json();
  for (const f of ["nombre","email","clave","rutEmpresa","giro","telefono"])
    if (!b?.[f]) return NextResponse.json({ error: `Falta ${f}` }, { status: 400 });
  const email = String(b.email).toLowerCase();
  if (await prisma.comerciante.findUnique({ where: { email } }))
    return NextResponse.json({ error: "Email ya registrado" }, { status: 409 });
  await prisma.comerciante.create({ data: {
    nombre: b.nombre, email, clave: await bcrypt.hash(b.clave, 10),
    rutEmpresa: b.rutEmpresa, giro: b.giro, telefono: b.telefono,
  }});
  // aviso al admin "nuevo comerciante por aprobar" se conecta en Task 9
  // (cuando exista src/lib/whatsapp.ts): await avisarWhatsApp(`Nuevo comerciante ${b.nombre} por aprobar.`)
  return NextResponse.json({ ok: true });
}
```

- [ ] **Step 4: Guard de rutas** (`src/middleware.ts`)

```ts
import { auth } from "@/auth";
export default auth((req) => {
  const u = (req.auth?.user as any);
  const p = req.nextUrl.pathname;
  if (p.startsWith("/admin") && u?.rol !== "admin")
    return Response.redirect(new URL("/login", req.url));
  if ((p.startsWith("/catalogo") || p.startsWith("/checkout")) && !u)
    return Response.redirect(new URL("/login", req.url));
});
export const config = { matcher: ["/admin/:path*", "/catalogo/:path*", "/checkout/:path*", "/mis-pedidos/:path*"] };
```

- [ ] **Step 5: Verificar build y commit**

Run: `npm run build` → compila.
```bash
git add -A && git commit -m "feat: auth.js con roles + registro + guard"
```

---

### Task 7: Páginas de registro, login y "cuenta en revisión"

**Files:**
- Create: `src/app/(comerciante)/registro/page.tsx`, `src/app/(comerciante)/login/page.tsx`, `src/app/(comerciante)/revision/page.tsx`

**Interfaces:**
- Consumes: `POST /api/registro`, `signIn` de Auth.js.
- Produces: rutas `/registro`, `/login`, `/revision`. UI adaptada de la maqueta (login de comerciante).

- [ ] **Step 1: Formulario de registro** — form con nombre, email, clave, RUT empresa, giro, teléfono → `fetch("/api/registro")` → al éxito redirige a `/login?registrado=1`. (Markup adaptado del login de la maqueta "Venta por Mayor".)

- [ ] **Step 2: Login** — form email/clave → `signIn("credentials", {...})`. Si la sesión vuelve con `estado != aprobado`, redirige a `/revision`.

- [ ] **Step 3: "Cuenta en revisión"** — pantalla estática: "Tu cuenta está en revisión, te avisaremos al aprobarla."

- [ ] **Step 4: Probar a mano** — registrar un comerciante, intentar login → cae en `/revision`. Aprobar manual en Prisma Studio → login entra al catálogo.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: registro/login/revisión comerciante"`

---

### Task 8: Catálogo (comerciante aprobado)

**Files:**
- Create: `src/app/(comerciante)/catalogo/page.tsx`
- Create: `src/app/(comerciante)/catalogo/buscar.tsx` (filtro cliente)

**Interfaces:**
- Consumes: `prisma.producto.findMany({ where: { activo: true } })`, sesión (estado aprobado).
- Produces: grilla con foto, nombre, y los 3 precios por tramo; buscador + filtro por `categoria`.

- [ ] **Step 1: Server component** — si `session.user.estado !== "aprobado"` → redirige a `/revision`. Carga productos activos y los pasa a la grilla. Muestra precios T1/T2/T3 con etiqueta de tramo.

- [ ] **Step 2: Búsqueda/filtro** — input de texto (filtra por nombre) + select de categoría (client component sobre la lista ya cargada).

- [ ] **Step 3: Probar** — con comerciante aprobado se ven los 117; sin login redirige a `/login`.

- [ ] **Step 4: Commit** — `git add -A && git commit -m "feat: catálogo con precios por tramo"`

---

### Task 9: Carrito, checkout, comprobante y creación de pedido

**Files:**
- Create: `src/lib/whatsapp.ts`
- Create: `src/app/(comerciante)/carrito/page.tsx`, `src/app/(comerciante)/checkout/page.tsx`
- Create: `src/app/api/pedidos/route.ts`, `src/app/api/comprobante/route.ts`

**Interfaces:**
- Consumes: `precioPorCantidad`, `subtotalLinea` (Task 3); `prisma`; Vercel Blob `put`.
- Produces: `POST /api/comprobante` → `{ url }`; `POST /api/pedidos` → crea Pedido en `pago_en_validacion` con items y total recalculados en el server.

- [ ] **Step 1: Aviso WhatsApp no bloqueante** (`src/lib/whatsapp.ts`)

```ts
export async function avisarWhatsApp(texto: string): Promise<void> {
  try {
    const u = new URL("https://api.callmebot.com/whatsapp.php");
    u.searchParams.set("phone", process.env.WA_PHONE!);
    u.searchParams.set("apikey", process.env.WA_KEY!);
    u.searchParams.set("text", texto);
    await fetch(u, { signal: AbortSignal.timeout(8000) });
  } catch { /* nunca bloquea la venta */ }
}
```

- [ ] **Step 2: Subida de comprobante a Blob** (`src/app/api/comprobante/route.ts`)

```ts
import { put } from "@vercel/blob";
import { NextResponse } from "next/server";
import { auth } from "@/auth";
const OK = ["image/jpeg","image/png","image/webp","application/pdf"];

export async function POST(req: Request) {
  const s = await auth(); if (!s) return NextResponse.json({ error: "no auth" }, { status: 401 });
  const form = await req.formData();
  const file = form.get("file") as File | null;
  if (!file) return NextResponse.json({ error: "Falta archivo" }, { status: 400 });
  if (!OK.includes(file.type)) return NextResponse.json({ error: "Solo imagen o PDF" }, { status: 400 });
  if (file.size > 8_000_000) return NextResponse.json({ error: "Máx 8MB" }, { status: 400 });
  const blob = await put(`comprobantes/${crypto.randomUUID()}-${file.name}`, file, { access: "public", addRandomSuffix: false });
  return NextResponse.json({ url: blob.url });
}
```

- [ ] **Step 3: Crear pedido (total recalculado en server)** (`src/app/api/pedidos/route.ts`)

```ts
import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { precioPorCantidad, subtotalLinea } from "@/lib/precios";
import { avisarWhatsApp } from "@/lib/whatsapp";

export async function POST(req: Request) {
  const s = await auth();
  const u = s?.user as any;
  if (!u || u.rol !== "comerciante" || u.estado !== "aprobado")
    return NextResponse.json({ error: "no autorizado" }, { status: 403 });
  const b = await req.json(); // { region, direccion, comprobanteUrl, items:[{productoId, cantidad}] }
  if (!b.region || !b.direccion || !b.comprobanteUrl || !b.items?.length)
    return NextResponse.json({ error: "datos incompletos" }, { status: 400 });

  const ids = b.items.map((i: any) => i.productoId);
  const prods = await prisma.producto.findMany({ where: { id: { in: ids }, activo: true } });
  const map = new Map(prods.map(p => [p.id, p]));
  let total = 0;
  const items = b.items.map((i: any) => {
    const p = map.get(i.productoId); if (!p) throw new Error("producto inválido");
    const cant = Math.max(1, Math.floor(i.cantidad));
    const precio = precioPorCantidad(p, cant);
    const sub = subtotalLinea(p, cant);
    total += sub;
    return { productoId: p.id, cantidad: cant, precioAplicado: precio, subtotal: sub };
  });

  const pedido = await prisma.pedido.create({ data: {
    comercianteId: u.id, estado: "pago_en_validacion", total,
    region: b.region, direccion: b.direccion, comprobanteUrl: b.comprobanteUrl,
    items: { create: items },
  }});
  await avisarWhatsApp(`Nuevo pedido mayorista #${pedido.id.slice(-6)} por ${u.name}. Total ${total}. Revisar comprobante en el panel.`);
  return NextResponse.json({ ok: true, pedidoId: pedido.id });
}
```

- [ ] **Step 4: UI carrito + checkout** — carrito en estado local (o cookie): lista items, cantidad editable, muestra precio por tramo y total (usando la misma regla). Checkout: select región, dirección, **muestra datos de transferencia (Scotiabank Cta Cte 000993556831)**, sube comprobante (`/api/comprobante`) y envía pedido (`/api/pedidos`). Markup adaptado de la maqueta.

- [ ] **Step 5: Conectar aviso de registro** — en `src/app/api/registro/route.ts` (Task 6), importar `avisarWhatsApp` y llamarlo antes del `return`: `await avisarWhatsApp(\`Nuevo comerciante \${b.nombre} por aprobar.\`)`.

- [ ] **Step 6: Probar el flujo** — agregar productos, checkout con comprobante → pedido creado en `pago_en_validacion`, llega WhatsApp.

- [ ] **Step 7: Commit** — `git add -A && git commit -m "feat: carrito, checkout, comprobante y creación de pedido"`

---

### Task 10: "Mis pedidos" (comerciante)

**Files:**
- Create: `src/app/(comerciante)/mis-pedidos/page.tsx`

**Interfaces:**
- Consumes: `prisma.pedido.findMany({ where: { comercianteId } })`.
- Produces: lista de pedidos del comerciante con estado, total, y tracking si existe.

- [ ] **Step 1: Listar pedidos del comerciante logueado** con su estado (etiqueta legible), total, fecha, y tracking/transportista cuando `estado` sea `despachado`/`entregado`.

- [ ] **Step 2: Probar** — el comerciante ve solo SUS pedidos.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: mis pedidos (comerciante)"`

---

### Task 11: Aprobar/rechazar comerciantes (admin)

**Files:**
- Create: `src/app/(admin)/admin/comerciantes/page.tsx`
- Create: `src/app/api/admin/comerciantes/route.ts`

**Interfaces:**
- Consumes: `prisma.comerciante`, guard admin (middleware).
- Produces: `POST /api/admin/comerciantes` `{ id, accion: "aprobar"|"rechazar" }` → cambia `estado`.

- [ ] **Step 1: API acción** — valida sesión admin; setea `estado` a `aprobado`/`rechazado`.

```ts
import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
export async function POST(req: Request) {
  const s = await auth(); if ((s?.user as any)?.rol !== "admin") return NextResponse.json({ error: "no auth" }, { status: 403 });
  const { id, accion } = await req.json();
  const estado = accion === "aprobar" ? "aprobado" : "rechazado";
  await prisma.comerciante.update({ where: { id }, data: { estado } });
  return NextResponse.json({ ok: true });
}
```

- [ ] **Step 2: UI** — lista de comerciantes (filtrable por estado) con botones Aprobar/Rechazar para los `pendiente`.

- [ ] **Step 3: Probar** — aprobar a un pendiente → ese comerciante ya entra al catálogo.

- [ ] **Step 4: Commit** — `git add -A && git commit -m "feat: admin aprobar/rechazar comerciantes"`

---

### Task 12: Pagos por validar (admin)

**Files:**
- Create: `src/app/(admin)/admin/pagos/page.tsx`
- Create: `src/app/api/admin/pedidos/estado/route.ts`

**Interfaces:**
- Consumes: `puedeTransicionar` (Task 4), `prisma`.
- Produces: `POST /api/admin/pedidos/estado` `{ id, a }` → valida transición y actualiza.

- [ ] **Step 1: API de transición de estado** (reutilizable por pagos/OC/despacho)

```ts
import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { puedeTransicionar } from "@/lib/pedido-estado";
export async function POST(req: Request) {
  const s = await auth(); if ((s?.user as any)?.rol !== "admin") return NextResponse.json({ error: "no auth" }, { status: 403 });
  const { id, a, transportista, tracking } = await req.json();
  const p = await prisma.pedido.findUnique({ where: { id } });
  if (!p) return NextResponse.json({ error: "no existe" }, { status: 404 });
  if (!puedeTransicionar(p.estado as any, a)) return NextResponse.json({ error: "transición inválida" }, { status: 400 });
  await prisma.pedido.update({ where: { id }, data: { estado: a, transportista, tracking } });
  return NextResponse.json({ ok: true });
}
```

- [ ] **Step 2: UI pagos** — lista de pedidos en `pago_en_validacion`, cada uno con link al comprobante (Blob) y botones **Validar** (→`validado`) / **Rechazar** (→`rechazado`).

- [ ] **Step 3: Probar** — validar un pago → pasa a `validado`; intentar saltar a `despachado` da error 400.

- [ ] **Step 4: Commit** — `git add -A && git commit -m "feat: admin validar/rechazar pagos"`

---

### Task 13: Generar OC a AlilaTop (admin)

**Files:**
- Create: `src/app/(admin)/admin/pedidos/page.tsx`
- Create: `src/app/api/admin/oc/route.ts`

**Interfaces:**
- Consumes: `prisma`, `puedeTransicionar`.
- Produces: `POST /api/admin/oc` `{ pedidoId }` → crea `OC` (numeroOc), pasa pedido a `oc_generada`. La OC lista los `codigoAlila` + cantidades (para que Victor compre en AlilaTop).

- [ ] **Step 1: API generar OC**

```ts
import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { puedeTransicionar } from "@/lib/pedido-estado";
export async function POST(req: Request) {
  const s = await auth(); if ((s?.user as any)?.rol !== "admin") return NextResponse.json({ error: "no auth" }, { status: 403 });
  const { pedidoId } = await req.json();
  const p = await prisma.pedido.findUnique({ where: { id: pedidoId } });
  if (!p || !puedeTransicionar(p.estado as any, "oc_generada")) return NextResponse.json({ error: "no válido" }, { status: 400 });
  const numeroOc = `OC-${Date.now().toString(36).toUpperCase()}`;
  await prisma.$transaction([
    prisma.oC.create({ data: { pedidoId, numeroOc } }),
    prisma.pedido.update({ where: { id: pedidoId }, data: { estado: "oc_generada" } }),
  ]);
  return NextResponse.json({ ok: true, numeroOc });
}
```

- [ ] **Step 2: UI pedidos** — lista de pedidos `validado` con botón **Generar OC**; al generarla muestra el N° OC y el detalle (códigos Alila + cantidades) para comprar en AlilaTop.

- [ ] **Step 3: Probar** — generar OC de un pedido validado → estado `oc_generada`, OC con número y detalle.

- [ ] **Step 4: Commit** — `git add -A && git commit -m "feat: generar OC a AlilaTop"`

---

### Task 14: Despacho y entrega (admin)

**Files:**
- Modify: `src/app/(admin)/admin/pedidos/page.tsx`

**Interfaces:**
- Consumes: `POST /api/admin/pedidos/estado` (Task 12), con `transportista` y `tracking`.
- Produces: pedido pasa `oc_generada → despachado → entregado`.

- [ ] **Step 1: UI despacho** — para pedidos `oc_generada`, formulario con transportista + tracking → botón **Despachar** (→`despachado`). Para `despachado`, botón **Marcar entregado** (→`entregado`).

- [ ] **Step 2: Probar** — despachar con tracking → el comerciante lo ve en "Mis pedidos"; marcar entregado.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: despacho y entrega"`

---

### Task 15: Dashboard mínimo + navegación admin

**Files:**
- Create: `src/app/(admin)/admin/page.tsx`, `src/app/(admin)/admin/layout.tsx`

**Interfaces:**
- Consumes: `prisma` (conteos).
- Produces: sidebar admin (Comerciantes, Pagos, Pedidos) + resumen con conteos (pendientes por aprobar, pagos por validar, pedidos por estado). Mantener mínimo; KPIs ricos = v2.

- [ ] **Step 1: Layout admin** con sidebar (links a las secciones) y guard (ya cubierto por middleware).

- [ ] **Step 2: Resumen** con 3-4 conteos (comerciantes pendientes, pagos por validar, pedidos en proceso).

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: layout y resumen admin"`

---

### Task 16: Deploy a Vercel + Neon + Blob + dominio

**Files:**
- Create: `README.md` (pasos de deploy y env vars)

**Interfaces:**
- Produces: portal en producción en `comercialsolutions.cl`.

- [ ] **Step 1: Crear proyecto en Vercel** y conectar el repo. Provisionar **Neon Postgres** (Vercel Marketplace) y **Blob**; copiar `DATABASE_URL` y `BLOB_READ_WRITE_TOKEN`. Setear `AUTH_SECRET`, `WA_PHONE`, `WA_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`.

- [ ] **Step 2: Migrar y sembrar en prod** — `npx prisma migrate deploy` + `npm run seed` apuntando a la DB de prod.

- [ ] **Step 3: Dominio** — agregar `comercialsolutions.cl` en Vercel; en Cloudflare apuntar el registro de la web a Vercel **dejando los MX del correo intactos**. ⚠️ Bloqueado hasta restaurar el dominio en nic.cl (antes del 10-07).

- [ ] **Step 4: Smoke test en prod** — registrar comerciante de prueba, aprobarlo, hacer un pedido con comprobante, validar pago, generar OC, despachar. Verificar WhatsApp.

- [ ] **Step 5: Commit** — `git add README.md && git commit -m "docs: pasos de deploy"`

---

## Notas de ejecución
- La **UI** de cada pantalla se adapta de la maqueta del proyecto "Venta por Mayor" en Claude Design (exportar su handoff y reutilizar markup/estilos), traduciendo cualquier voseo a español de Chile.
- **Pendientes de datos** (no bloquean el desarrollo, sí el lanzamiento real): regiones + tarifas de despacho, `unidCaja`/`minCompra` por producto, contacto de AlilaTop para enviar la OC, correo para comprobantes, y los 2 productos sin costo. Ver `MAYORISTA_DATOS_REALES.md`.
- **Bloqueante de deploy:** restaurar `comercialsolutions.cl` en nic.cl.
