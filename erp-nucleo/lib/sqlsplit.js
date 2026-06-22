// Divide un script SQL en sentencias individuales para drivers que solo
// aceptan una por llamada (Neon serverless).
// ponytail: split por ';' simple; nuestro DDL no contiene ';' dentro de
// literales, así que basta. Si algún día el SQL trae literales con ';',
// cambiar a un parser real.
export function splitSql(sql) {
  return sql.split(';').map((s) => s.trim()).filter(Boolean);
}
