-- AlterTable
ALTER TABLE "Producto" ADD COLUMN     "codigoProveedor" TEXT,
ADD COLUMN     "descripcion" TEXT,
ADD COLUMN     "dimensiones" TEXT,
ADD COLUMN     "embalaje" TEXT,
ADD COLUMN     "fotos" TEXT[],
ADD COLUMN     "keywords" TEXT,
ADD COLUMN     "linkML" TEXT,
ADD COLUMN     "nArticulo" TEXT;
