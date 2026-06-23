// Las fotos de AlilaTop llegan con el nombre de archivo en chino crudo
// (ej. .../主图.jpg). next/image las pasa al optimizador y ese fetch falla
// (502) si la ruta no está percent-encoded. encodeURI codifica lo no-ASCII y
// deja intacto el resto; es idempotente sobre URLs ASCII normales.
// ponytail: encode al render, no en la base — el refresco diario re-escribe
// las URLs crudas cada mañana, así que arreglar la base no aguantaría.
export function imgSrc(url: string): string {
  return encodeURI(url);
}
