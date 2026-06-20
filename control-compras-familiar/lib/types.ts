// ====== Modelo de datos — Control de Compras ======

export const CATEGORIAS = [
  { key: "productos", label: "Productos", color: "#2563eb", grupo: "gasto" },
  { key: "insumos", label: "Insumos", color: "#d97706", grupo: "gasto" },
  { key: "servicios", label: "Servicios básicos", color: "#7c3aed", grupo: "gasto" },
  { key: "gastos", label: "Gastos generales", color: "#e11d48", grupo: "gasto" },
  { key: "retiros", label: "Retiros", color: "#475569", grupo: "retiro" },
] as const;

export type CatKey = (typeof CATEGORIAS)[number]["key"];

export const METODOS = ["Efectivo", "Transferencia", "Débito", "Crédito", "Cheque"] as const;

export interface Movimiento {
  id: string;
  fecha: string; // YYYY-MM-DD
  categoria: CatKey;
  descripcion: string;
  proveedor: string;
  monto: number; // CLP
  metodo: string;
  nota: string;
}

export interface AppData {
  movimientos: Movimiento[];
  presupuestos: Record<CatKey, number>; // presupuesto mensual por categoría
}

export const emptyData = (): AppData => ({
  movimientos: [],
  presupuestos: { productos: 0, insumos: 0, servicios: 0, gastos: 0, retiros: 0 },
});

export const catMeta = (k: CatKey) => CATEGORIAS.find((c) => c.key === k)!;
