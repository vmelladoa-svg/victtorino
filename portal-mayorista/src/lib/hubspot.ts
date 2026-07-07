// Sincroniza los leads del portal con HubSpot (CRM). Fire-and-forget: si HubSpot
// falla o no está configurado, NUNCA bloquea el registro.
//
// Configuración (una sola vez):
//   1. Crear una Private App en HubSpot con el scope `crm.objects.contacts.write`.
//   2. Poner su token en la variable de entorno HUBSPOT_TOKEN.
//   3. (Opcional) Crear una propiedad de contacto `rut_empresa` (texto). Si no
//      existe, el contacto se crea igual y el RUT simplemente no se sincroniza.

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

  // Propiedades estándar: siempre existen en HubSpot, nunca hacen fallar el create.
  const base: Record<string, string> = {
    email: lead.email,
    firstname: lead.nombre,
    lifecyclestage: "lead",
  };
  if (lead.telefono) base.phone = lead.telefono;
  if (lead.giro) base.company = lead.giro;
  if (lead.comuna) base.city = lead.comuna;
  if (lead.region) base.state = lead.region;

  // Propiedades personalizadas: pueden no existir. Se aplican aparte (best-effort)
  // para que una propiedad inexistente NO impida crear el contacto.
  const custom: Record<string, string> = {};
  if (lead.rutEmpresa) custom.rut_empresa = lead.rutEmpresa;

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  try {
    let contactId: string | undefined;

    const res = await fetch(`${HS_BASE}/crm/v3/objects/contacts`, {
      method: "POST",
      headers,
      body: JSON.stringify({ properties: base }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });

    if (res.ok) {
      const data = await res.json().catch(() => null);
      contactId = data?.id;
    } else if (res.status === 409) {
      // Email duplicado → HubSpot devuelve "Existing ID: <n>": actualizamos.
      const data = await res.json().catch(() => null);
      const id = String(data?.message ?? "").match(/Existing ID:\s*(\d+)/)?.[1];
      if (id) {
        contactId = id;
        await fetch(`${HS_BASE}/crm/v3/objects/contacts/${id}`, {
          method: "PATCH",
          headers,
          body: JSON.stringify({ properties: base }),
          signal: AbortSignal.timeout(TIMEOUT_MS),
        });
      }
    }

    // RUT (propiedad custom) en un PATCH aparte que puede fallar sin consecuencias.
    if (contactId && Object.keys(custom).length > 0) {
      await fetch(`${HS_BASE}/crm/v3/objects/contacts/${contactId}`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ properties: custom }),
        signal: AbortSignal.timeout(TIMEOUT_MS),
      }).catch(() => {});
    }
  } catch {
    /* nunca bloquea el registro */
  }
}
