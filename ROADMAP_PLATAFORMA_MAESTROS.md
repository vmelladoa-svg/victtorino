# Roadmap — Plataforma de Maestros TradeGlobalChile ("Uber de maestros")

> Marketplace de servicios de instalación (grifería, gasfitería, lavaplatos…) que conecta
> **clientes** (demanda) con **maestros** (oferta), con **Trade en el medio** validando maestros
> y trabajos. Todo en **PWA** (se instala como app desde un link, sin App/Play Store). Escalable por fases.

## El gancho del maestro = 2 necesidades
La app engancha al maestro por **dos motivos** (lo que ya promete la ficha):
1. **Precio de club (socio)** 🛒 — al pertenecer al club, ve **precio preferente** en el catálogo de Trade, **aunque compre una sola unidad** (NO es compra por mayor / por volumen — el mejor precio es por ser socio). Muestra "precio club" vs "precio normal" para que vea el ahorro. Refuerza pertenencia.
2. **Recibir trabajos** 💼 — pegas que Trade le asigna y le paga semanalmente.
> Clave de estrategia: la **tienda con precio de club se puede lanzar primero** (es un flujo de catálogo/pedido, buildable ya — reusa el patrón del e-commerce que ya hicimos), y **engancha y retiene maestros desde el día 1** mientras el motor de asignación de trabajos (más pesado) madura. Los trabajos son el upside; el precio de socio es el imán inmediato.

## Las 3 apps (sobre un mismo backend Express/PostgreSQL)
1. **App Maestro** 🔧 — se registra → Trade lo valida → instala la app → **(a) Comprar** productos a precio de club y **(b) Trabajos** asignados (aceptar, marcar "terminado", ver liquidaciones).
2. **App Cliente** 🏠 — instala la app → pide un servicio, sigue el estado del trabajo, califica.
3. **Panel Admin (Trade)** 🎛️ — valida maestros, valida/crea trabajos, asigna, ve liquidaciones y todo el flujo.

## Flujo central (con las dos validaciones)
```
MAESTRO:  registro ──▶ [VALIDACIÓN Trade: Pendiente→Aprobado] ──▶ habilitado para recibir trabajos
CLIENTE:  pide servicio ──▶ [VALIDACIÓN Trade: revisa el trabajo] ──▶ Trade asigna a un maestro aprobado
          ──▶ maestro acepta ──▶ ejecuta ──▶ marca "terminado"
          ──▶ [VALIDACIÓN cierre: Trade/cliente confirma OK] ──▶ liquidación al maestro + cobro al cliente
```
Las validaciones (maestro y trabajo) son **manuales por Trade** en el MVP, y se van automatizando después.

## Fases (cada una ya es usable y deja valor)
- **Fase 0 — Captación (EN CURSO).** Ficha de maestros (✅ lista, en vivo) + landing de captación de clientes (pendiente). Llena oferta y demanda desde ya. Conectar fallback (Google Sheets) para no perder leads mientras no hay backend.
- **Fase 1A — Tienda precio de club para maestros (gancho rápido).** App Maestro con login simple + catálogo a **precio de club** y pedidos. Es lo más rápido de construir (reusa el patrón e-commerce) y **engancha/retiene maestros desde ya**, aunque los trabajos aún no fluyan. Recomendado como primer entregable funcional tras la captación.
- **Fase 1B — MVP de trabajos (asignación manual).**
  - App Maestro: sección "mis trabajos asignados", aceptar/terminar.
  - App Cliente mínima: pedir servicio (qué, dónde, cuándo) + seguimiento básico.
  - Admin: validar maestros (Pendiente/Aprobado/Rechazado), crear/validar trabajos y asignarlos a mano.
  - Ya se opera de verdad, con poco código y control total de calidad.
- **Fase 2 — Portal del maestro completo.** Liquidaciones en la app, historial, estados del trabajo, notificaciones (WhatsApp/push).
- **Fase 3 — Lo "Uber".** Cliente agenda online con precio (tarifas), **auto-asignación por zona/disponibilidad**, estados en vivo, calificaciones que afectan el ranking.
- **Fase 4 — Escala.** Pagos automáticos (Webpay / transferencias), geolocalización, métricas, y recién evaluar app nativa si hace falta.
- **Fase 5 — Crecimiento viral / efecto red.** Que los usuarios **se recomienden la app** para conseguir maestros: programa de **referidos** (link/código por usuario), incentivos (descuento o crédito por traer a otro), botón "compartir", y confianza por **calificaciones** visibles. Cada cliente satisfecho trae más clientes y más maestros — crecimiento barato.

> **Regla de oro de la viralidad:** la gente solo recomienda lo que YA funciona bien. Primero hay que entregar una **buena experiencia** (productos baratos de verdad + maestros confiables + trabajos bien hechos). El motor de referidos se activa DESPUÉS de eso, no antes. Por eso el orden: tienda → trabajos → calidad → recién ahí potenciar la recomendación.

## Reparto de trabajo
- **Front (yo):** las 3 PWA y todos los flujos de pantalla, validaciones de formulario, estados. Dejo todo listo para conectar al backend (capa de servicios como en las fichas).
- **Backend (equipo Express/PostgreSQL):** lógica de asignación, validaciones de negocio, pagos, tiempo real, escala. Tablas ya previstas: maestros, trabajos, tarifas, liquidaciones, auditoria.

## Lo que ya existe y se reusa
- **Ficha maestros** (`tradeglobal-maestros`) = puerta de entrada de la oferta (Fase 0). Su capa de envío (`lib/submit.ts`) y validaciones (RUT, etc.) se reutilizan en la App Maestro.
- Patrón **PWA instalable** (ícono en celular, sin tiendas) ya probado.

## Decisiones pendientes (antes/durante Fase 1)
- **Piloto:** ¿comuna(s) y servicio inicial? (sugerido: grifería/gasfitería en la RM).
- **Tarifas/precios:** ¿precio fijo por tipo de trabajo, o cotización por trabajo?
- **Validación de cierre:** ¿la confirma Trade, el cliente, o ambos?
- **Backend:** ¿está vivo el Express/PostgreSQL o hay que levantarlo? (define cuánto se puede automatizar ya).

## Próximo paso recomendado
1. **Cerrar Fase 0:** conectar el fallback de la ficha de maestros (Google Sheets) para capturar ya.
2. **Fase 1A — la tienda de club del maestro:** primer entregable funcional, rápido y de alto enganche (precio de club). Mientras tanto el equipo backend levanta lo de trabajos.
3. La captación/landing de **clientes** y el **MVP de trabajos** vienen después (Fase 1B).
