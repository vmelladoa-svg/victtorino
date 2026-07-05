-- AlterTable
ALTER TABLE "Comerciante" ADD COLUMN     "scoreAjuste" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "tierManual" TEXT,
ADD COLUMN     "notaEval" TEXT,
ADD COLUMN     "evaluadoAt" TIMESTAMP(3);
