import { describe, it, expect } from "vitest";
import { puedeTransicionar } from "@/lib/pedido-estado";
describe("estados", () => {
  it("validar tras pago", () => expect(puedeTransicionar("pago_en_validacion","validado")).toBe(true));
  it("rechazar pago", () => expect(puedeTransicionar("pago_en_validacion","rechazado")).toBe(true));
  it("no se genera OC sin validar", () => expect(puedeTransicionar("pago_en_validacion","oc_generada")).toBe(false));
  it("OC tras validar", () => expect(puedeTransicionar("validado","oc_generada")).toBe(true));
  it("despacho tras OC", () => expect(puedeTransicionar("oc_generada","despachado")).toBe(true));
  it("entrega tras despacho", () => expect(puedeTransicionar("despachado","entregado")).toBe(true));
  it("no salta de validado a despachado", () => expect(puedeTransicionar("validado","despachado")).toBe(false));
  it("se puede rechazar un pedido ya validado (libera reserva)", () => expect(puedeTransicionar("validado","rechazado")).toBe(true));
  it("no se rechaza un pedido ya despachado", () => expect(puedeTransicionar("despachado","rechazado")).toBe(false));
});
