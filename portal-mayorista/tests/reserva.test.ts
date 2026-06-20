import { describe, it, expect } from "vitest";
import { disponible, puedeReservar } from "@/lib/reserva";

describe("disponible", () => {
  it("stock null = sin límite (Infinity)", () => expect(disponible(null, 0)).toBe(Infinity));
  it("stock - reservado", () => expect(disponible(10, 3)).toBe(7));
  it("no baja de 0", () => expect(disponible(5, 9)).toBe(0));
});

describe("puedeReservar", () => {
  it("sin dato de stock permite cualquier cantidad", () => expect(puedeReservar(null, 0, 50)).toBe(true));
  it("permite hasta lo disponible", () => expect(puedeReservar(10, 0, 10)).toBe(true));
  it("rechaza si excede disponible", () => expect(puedeReservar(10, 0, 11)).toBe(false));
  it("considera lo ya reservado", () => {
    expect(puedeReservar(10, 7, 3)).toBe(true);
    expect(puedeReservar(10, 7, 4)).toBe(false);
  });
  it("cantidad 0 o negativa = false", () => {
    expect(puedeReservar(10, 0, 0)).toBe(false);
    expect(puedeReservar(null, 0, -1)).toBe(false);
  });
});
