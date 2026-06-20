import "dotenv/config";
import { Pool } from "pg";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "../src/generated/prisma/client.ts";
import * as XLSX from "xlsx";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

const num = (v: any) => {
  const n = parseInt(String(v).replace(/\D/g, ""), 10);
  return Number.isFinite(n) ? n : null;
};

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
