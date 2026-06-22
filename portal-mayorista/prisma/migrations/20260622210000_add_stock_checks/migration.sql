-- Red de seguridad a nivel de BD para stock/reserva.
-- Impide que cualquier carrera o bug deje stock negativo o reservado > stock.
ALTER TABLE "Producto"
  ADD CONSTRAINT "producto_stock_no_neg" CHECK ("stock" IS NULL OR "stock" >= 0),
  ADD CONSTRAINT "producto_reservado_no_neg" CHECK ("reservado" >= 0),
  ADD CONSTRAINT "producto_reservado_lte_stock" CHECK ("stock" IS NULL OR "reservado" <= "stock");
