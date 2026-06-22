export type EstadoPedido = "pago_en_validacion"|"validado"|"oc_generada"|"despachado"|"entregado"|"rechazado";
export const SIGUIENTE: Record<EstadoPedido, EstadoPedido[]> = {
  pago_en_validacion: ["validado","rechazado"],
  validado: ["oc_generada","rechazado"],
  oc_generada: ["despachado"],
  despachado: ["entregado"],
  entregado: [],
  rechazado: [],
};
export function puedeTransicionar(de: EstadoPedido, a: EstadoPedido): boolean {
  return SIGUIENTE[de]?.includes(a) ?? false;
}
