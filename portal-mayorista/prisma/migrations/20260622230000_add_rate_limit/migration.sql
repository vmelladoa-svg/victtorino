-- Rate-limit de login/registro: contador de ventana fija en la propia base (sin Upstash).
CREATE TABLE IF NOT EXISTS "RateLimit" (
    "key" TEXT NOT NULL,
    "count" INTEGER NOT NULL DEFAULT 0,
    "resetAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "RateLimit_pkey" PRIMARY KEY ("key")
);
