import { describe, it, expect } from "vitest";
import { precioPorCantidad, subtotalLinea } from "@/lib/precios";
const P = { precioT1: 10000, precioT2: 8800, precioT3: 8000 };

describe("precioPorCantidad", () => {
  it("1-5 u usa T1", () => expect(precioPorCantidad(P, 1)).toBe(10000));
  it("borde 5 usa T1", () => expect(precioPorCantidad(P, 5)).toBe(10000));
  it("6-20 u usa T2", () => expect(precioPorCantidad(P, 6)).toBe(8800));
  it("borde 20 usa T2", () => expect(precioPorCantidad(P, 20)).toBe(8800));
  it("21+ u usa T3", () => expect(precioPorCantidad(P, 21)).toBe(8000));
  it("subtotal = precio x cantidad", () => expect(subtotalLinea(P, 6)).toBe(52800));
});
