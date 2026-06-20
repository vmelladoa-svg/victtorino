-- CreateEnum
CREATE TYPE "EstadoComerciante" AS ENUM ('pendiente', 'aprobado', 'rechazado');

-- CreateEnum
CREATE TYPE "EstadoPedido" AS ENUM ('pago_en_validacion', 'validado', 'oc_generada', 'despachado', 'entregado', 'rechazado');

-- CreateTable
CREATE TABLE "Comerciante" (
    "id" TEXT NOT NULL,
    "nombre" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "clave" TEXT NOT NULL,
    "rutEmpresa" TEXT NOT NULL,
    "giro" TEXT NOT NULL,
    "telefono" TEXT NOT NULL,
    "estado" "EstadoComerciante" NOT NULL DEFAULT 'pendiente',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Comerciante_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Producto" (
    "id" TEXT NOT NULL,
    "codigoAlila" TEXT NOT NULL,
    "nombre" TEXT NOT NULL,
    "categoria" TEXT,
    "costo" INTEGER,
    "precioT1" INTEGER,
    "precioT2" INTEGER,
    "precioT3" INTEGER,
    "unidCaja" INTEGER,
    "minCompra" INTEGER NOT NULL DEFAULT 1,
    "fotoUrl" TEXT,
    "link1688" TEXT,
    "activo" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "Producto_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Pedido" (
    "id" TEXT NOT NULL,
    "comercianteId" TEXT NOT NULL,
    "estado" "EstadoPedido" NOT NULL DEFAULT 'pago_en_validacion',
    "total" INTEGER NOT NULL,
    "region" TEXT NOT NULL,
    "direccion" TEXT NOT NULL,
    "comprobanteUrl" TEXT,
    "transportista" TEXT,
    "tracking" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Pedido_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PedidoItem" (
    "id" TEXT NOT NULL,
    "pedidoId" TEXT NOT NULL,
    "productoId" TEXT NOT NULL,
    "cantidad" INTEGER NOT NULL,
    "precioAplicado" INTEGER NOT NULL,
    "subtotal" INTEGER NOT NULL,

    CONSTRAINT "PedidoItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "OC" (
    "id" TEXT NOT NULL,
    "pedidoId" TEXT NOT NULL,
    "proveedor" TEXT NOT NULL DEFAULT 'AlilaTop',
    "numeroOc" TEXT NOT NULL,
    "estado" TEXT NOT NULL DEFAULT 'emitida',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "OC_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Comerciante_email_key" ON "Comerciante"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Producto_codigoAlila_key" ON "Producto"("codigoAlila");

-- CreateIndex
CREATE UNIQUE INDEX "OC_pedidoId_key" ON "OC"("pedidoId");

-- CreateIndex
CREATE UNIQUE INDEX "OC_numeroOc_key" ON "OC"("numeroOc");

-- AddForeignKey
ALTER TABLE "Pedido" ADD CONSTRAINT "Pedido_comercianteId_fkey" FOREIGN KEY ("comercianteId") REFERENCES "Comerciante"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PedidoItem" ADD CONSTRAINT "PedidoItem_pedidoId_fkey" FOREIGN KEY ("pedidoId") REFERENCES "Pedido"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PedidoItem" ADD CONSTRAINT "PedidoItem_productoId_fkey" FOREIGN KEY ("productoId") REFERENCES "Producto"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "OC" ADD CONSTRAINT "OC_pedidoId_fkey" FOREIGN KEY ("pedidoId") REFERENCES "Pedido"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
