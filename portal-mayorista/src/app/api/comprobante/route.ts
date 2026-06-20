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
