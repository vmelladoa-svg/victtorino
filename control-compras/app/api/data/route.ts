import { NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { emptyData } from "@/lib/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const KEY = "control-compras:data";

function getRedis(): Redis | null {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  return new Redis({ url, token });
}

/** Si hay APP_PIN configurado, exige que coincida. Si no, no bloquea. */
function pinOk(req: Request): boolean {
  const expected = process.env.APP_PIN;
  if (!expected) return true;
  return req.headers.get("x-pin") === expected;
}

export async function GET(req: Request) {
  const r = getRedis();
  if (!r) return NextResponse.json({ error: "no-cloud" }, { status: 503 });
  if (!pinOk(req)) return NextResponse.json({ error: "pin" }, { status: 401 });
  const data = (await r.get(KEY)) ?? emptyData();
  return NextResponse.json({ data });
}

export async function POST(req: Request) {
  const r = getRedis();
  if (!r) return NextResponse.json({ error: "no-cloud" }, { status: 503 });
  if (!pinOk(req)) return NextResponse.json({ error: "pin" }, { status: 401 });
  const body = await req.json();
  await r.set(KEY, body);
  return NextResponse.json({ ok: true });
}
