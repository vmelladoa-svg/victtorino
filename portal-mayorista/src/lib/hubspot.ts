// Sincroniza los leads del portal con HubSpot (CRM). Fire-and-forget: si HubSpot
// falla o no está configurado, NUNCA bloquea el registro.
//
// Requisitos de configuración (una sola vez):
//   1. Crear una Private App en HubSpot (Settings → Integrations → Private Apps)
//      con el scope `crm.objects.contacts.write` y copiar su token.
//   2. Poner ese token en la variable de entorno HUBSPOT_TOKEN.
//   3. Crear una propiedad de contacto personalizada `rut_empresa` (texto de una
//      línea) en HubSpot. Si no existe, el RUT simplemente no se sincroniza.

interface LeadContacto {
  email: string;
  nombre: string;
  telefono?: string;
  giro?: string;
  comuna?: string;
  region?: string;
  rutEmpresa?: string;
}

const HS_BASE = "https://api.hubapi.com";
const TIMEOUT_MS = 8000;

export async function sincronizarLeadHubSpot(lead: LeadContacto): Promise<void> {
  const token = process.env.HUBSPOT_TOKEN;
  if (!token) return; // sin token configurado → no-op silencioso

  const properties: Record<string, string> = {
    email: lead.email,
    firstname: lead.nombre,
    lifecyclestage: "lead",
  };
  if (lead.telefono) properties.phone = lead.telefono;
  if (lead.giro) properties.company = lead.giro;
  if (lead.comuna) properties.city = lead.comuna;
  if (lead.region) properties.state = lead.region;
  if (lead.rutEmpresa) properties.rut_empresa = lead.rutEmpresa;

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  try {
    const res = await fetch(`${HS_BASE}/crm/v3/objects/contacts`, {
      method: "POST",
      headers,
      body: JSON.stringify({ properties }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });

    // Email duplicado → HubSpot devuelve 409 con "Existing ID: <n>": actualizamos.
    if (res.status === 409) {
      const data = await res.json().catch(() => null);
      const id = String(data?.message ?? "").match(/Existing ID:\s*(\d+)/)?.[1];
      if (id) {
        await fetch(`${HS_BASE}/crm/v3/objects/contacts/${id}`, {
          method: "PATCH",
          headers,
          body: JSON.stringify({ properties }),
          signal: AbortSignal.timeout(TIMEOUT_MS),
        });
      }
    }
  } catch {
    /* nunca bloquea el registro */
  }
}
