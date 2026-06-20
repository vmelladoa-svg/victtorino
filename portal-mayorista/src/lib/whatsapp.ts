export async function avisarWhatsApp(texto: string): Promise<void> {
  try {
    const u = new URL("https://api.callmebot.com/whatsapp.php");
    u.searchParams.set("phone", process.env.WA_PHONE!);
    u.searchParams.set("apikey", process.env.WA_KEY!);
    u.searchParams.set("text", texto);
    await fetch(u, { signal: AbortSignal.timeout(8000) });
  } catch { /* nunca bloquea la venta */ }
}
