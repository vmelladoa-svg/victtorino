// ============================================================
//  TRANSBANK WEBPAY PLUS — CAPA DE PAGO (STUB / MOCK)
// ============================================================
//  Esta maqueta NO procesa pagos reales. Las funciones de abajo
//  devuelven datos simulados para mostrar la pantalla de
//  confirmación. Para integrar Webpay Plus de verdad:
//
//  1. Instalar el SDK oficial:   npm i transbank-sdk
//  2. Crear estas funciones como ROUTE HANDLERS del servidor
//     (app/api/webpay/create/route.ts y .../commit/route.ts),
//     NUNCA en el cliente — las credenciales van solo en el server.
//  3. Variables de entorno (.env.local):
//       TBK_COMMERCE_CODE=...
//       TBK_API_KEY=...
//       TBK_ENV=integration | production
//  4. Reemplazar los cuerpos MOCK por el SDK (ver ejemplo comentado).
//  5. En checkout, el botón "Pagar con Webpay" debe:
//       - llamar a createWebpayTransaction() -> recibir { url, token }
//       - redirigir el navegador a `url` con el `token` (POST form),
//       - al volver, llamar a commitWebpayTransaction(token).
// ============================================================

export interface WebpayCreateInput {
  buyOrder: string;
  sessionId: string;
  amount: number; // CLP, entero
  returnUrl: string;
}

export interface WebpayCreateResult {
  token: string;
  url: string; // URL del formulario de pago de Transbank
}

export interface WebpayCommitResult {
  status: "AUTHORIZED" | "FAILED";
  buyOrder: string;
  amount: number;
  authorizationCode?: string;
  cardLast4?: string;
}

/** MOCK — crea una "transacción". En prod, usar el SDK (ver abajo). */
export async function createWebpayTransaction(
  input: WebpayCreateInput
): Promise<WebpayCreateResult> {
  await new Promise((r) => setTimeout(r, 400));
  // --- PRODUCCIÓN (descomentar y borrar el mock) -------------------
  // import { WebpayPlus, Options, Environment } from "transbank-sdk";
  // const tx = new WebpayPlus.Transaction(
  //   new Options(process.env.TBK_COMMERCE_CODE!, process.env.TBK_API_KEY!,
  //     process.env.TBK_ENV === "production" ? Environment.Production : Environment.Integration)
  // );
  // const res = await tx.create(input.buyOrder, input.sessionId, input.amount, input.returnUrl);
  // return { token: res.token, url: res.url };
  // -----------------------------------------------------------------
  return {
    token: "MOCK_TOKEN_" + Math.random().toString(36).slice(2, 10),
    url: "/checkout/confirmacion", // en la maqueta redirige a la pantalla simulada
  };
}

/** MOCK — confirma el pago tras el retorno de Transbank. */
export async function commitWebpayTransaction(token: string): Promise<WebpayCommitResult> {
  await new Promise((r) => setTimeout(r, 400));
  // --- PRODUCCIÓN -------------------------------------------------
  // const res = await tx.commit(token);
  // return { status: res.response_code === 0 ? "AUTHORIZED" : "FAILED",
  //   buyOrder: res.buy_order, amount: res.amount,
  //   authorizationCode: res.authorization_code, cardLast4: res.card_detail?.card_number };
  // -----------------------------------------------------------------
  return {
    status: "AUTHORIZED",
    buyOrder: "DB-" + Date.now(),
    amount: 0,
    authorizationCode: "1213" + Math.floor(Math.random() * 9000 + 1000),
    cardLast4: "6623",
  };
}
