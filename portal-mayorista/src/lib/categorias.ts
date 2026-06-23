// Agrupación de las categorías del catálogo en 9 grupos de navegación.
// Los productos guardan `categoria = "Categoría>Subcategoría"`. El PRIMER NIVEL
// ("Categoría") es lo que se agrupa; el filtrado compara contra ese primer nivel,
// así sigue funcionando con los datos existentes sin migrar nada.

export const GRUPOS: { nombre: string; cats: string[] }[] = [
  { nombre: "Tecnología", cats: ["Computación", "Celulares y Telefonía", "Electrónica, Audio y Video", "Cámaras y Accesorios"] },
  { nombre: "Herramientas y Construcción", cats: ["Herramientas", "Construcción"] },
  { nombre: "Hogar y Jardín", cats: ["Hogar y Muebles", "Electrodomésticos"] },
  { nombre: "Salud y Deporte", cats: ["Salud y Equipamiento Médico", "Deportes y Fitness"] },
  { nombre: "Infantil", cats: ["Bebés", "Juegos y Juguetes"] },
  { nombre: "Moda y Belleza", cats: ["Vestuario y Calzado", "Belleza y Cuidado Personal"] },
  { nombre: "Vehículos", cats: ["Accesorios para Vehículos"] },
  { nombre: "Industria y Oficina", cats: ["Industrias y Oficinas", "Instrumentos Musicales"] },
  { nombre: "Mascotas", cats: ["Animales y Mascotas"] },
];

// Grupo para categorías de primer nivel no mapeadas (p.ej. una categoría nueva
// que aparezca en el refresco diario de AlilaTop). Así nunca desaparece del catálogo.
export const OTROS = "Otros";

// Primer nivel de la categoría (texto antes del primer ">").
export function nivel1(categoria: string | null | undefined): string {
  if (!categoria) return "";
  const i = categoria.indexOf(">");
  return (i === -1 ? categoria : categoria.slice(0, i)).trim();
}

const GRUPO_DE = new Map<string, string>();
for (const g of GRUPOS) for (const c of g.cats) GRUPO_DE.set(c, g.nombre);

// Grupo al que pertenece una categoría de primer nivel (o "Otros" si no está mapeada).
export function grupoDe(cat1: string): string {
  return GRUPO_DE.get(cat1) ?? OTROS;
}
