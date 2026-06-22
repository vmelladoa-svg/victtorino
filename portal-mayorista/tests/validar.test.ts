import { describe, it, expect } from "vitest";
import { esEmail, esRut, texto, cantidadValida } from "@/lib/validar";

describe("validar", () => {
  it("email válido/ inválido", () => {
    expect(esEmail("a@b.cl")).toBe(true);
    expect(esEmail("nope")).toBe(false);
    expect(esEmail("")).toBe(false);
  });
  it("RUT con dígito verificador", () => {
    expect(esRut("78.103.712-5")).toBe(true);  // RUT real de Trade Global Solutions
    expect(esRut("781037125")).toBe(true);
    expect(esRut("78.103.712-4")).toBe(false);  // DV incorrecto
    expect(esRut("11.111.111-1")).toBe(true);
    expect(esRut("basura")).toBe(false);
  });
  it("texto recorta y acota", () => {
    expect(texto("  hola  ")).toBe("hola");
    expect(texto("x".repeat(300), 10)).toHaveLength(10);
    expect(texto(123)).toBe("");
  });
  it("cantidad: entero >=1 acotado", () => {
    expect(cantidadValida(3)).toBe(3);
    expect(cantidadValida("5")).toBe(5);
    expect(cantidadValida(0)).toBe(null);
    expect(cantidadValida(-2)).toBe(null);
    expect(cantidadValida("abc")).toBe(null);
    expect(cantidadValida(999999, 1000)).toBe(1000);
  });
});
