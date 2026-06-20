# PENDIENTES Trade — tablero vivo
_Actualizado: 2026-06-20_

> Fuente para el resumen diario "¿qué tenemos para hoy?". Mantener al día: marcar [x] lo hecho, agregar nuevos pendientes arriba.

## 🚨 URGENTE
- [ ] **Renovar `comercialsolutions.cl` en nic.cl ANTES del 10-07-2026** — VENCIÓ el 09-06, está en gracia. Si no se renueva, se elimina y se pierde (afecta el CORREO @comercialsolutions.cl y el futuro portal mayorista). tradeglobalchile.cl está OK (hasta 09-06-2027).

## 🔔 Programado (rutinas en la nube — avisan por WhatsApp)
- [ ] **06/07** — Recordatorio WhatsApp renovar dominio comercialsolutions.cl (vence 10-07). Routine `trig_01TjuCBDsndoeyovGxdueJP7`
- [ ] **21/06** — Revisar reaprobación Merchant (167 desaprobados). Routine `trig_01FBHUjQUzXyHbsF8xTYpEZR`
- [ ] **23/07** — Renovar specials Falabella (vencen 25/07). Routine `trig_011zpEKNQEtT69yKa66uweSF`

## 🟢 Mercado Libre (lo de más trabajo)
- [ ] **EN PAUSA** — Etiquetar ~50 publicaciones sin código interno = causa de cancelaciones por falso "sin stock". Hoja `ML_Verificar_codigos_2026-06-19.xlsx` (Victor verifica match → yo escribo por API). NO tocar stock.
- [ ] Publicar los **24 faltantes** en ML (solo con stock real → esperar inventario)
- [ ] Reactivar **29 pausados** (solo stock>0 + confirmación)
- [ ] Consolidar **23 duplicados** activos en varias cuentas → concentrar en C3

## 🟡 Otros canales
- [ ] **Paris/Walmart** — precio en lista (hoja Resumen); verificar publicación (vía Defontana)
- [ ] **Mayorista** — definir lista/canal
- [ ] **Merchant — cargar dirección comercial EN Merchant Center** (Información del negocio → Dirección comercial; campo de cuenta, aparte de WooCommerce que ya está OK): `Madame Adriana Bolland 430, La Cisterna, RM, CP 7970000`. Es el error de cuenta "Missing business address" que puede estar tumbando los 167. Tarea de navegador. (CP ya guardado en WooCommerce 20/06.)

## ⏳ Esperando
- [ ] Inventario físico de Victor → cruzar stock real para decidir qué publicar/pausar
- [ ] Merchant: re-revisión de Google de los 167 (1-3 días)

## ✅ Cerrado reciente (avances)
- [x] 18/06 Precios Web (164 prods = Tienda Física + $3.500 despacho)
- [x] 18/06 Precios Falabella (157, descuento en reversa −30%, vence 25/07)
- [x] 18/06 Maestra de precios por canal + stock real Defontana
- [x] 18/06 Diagnóstico cancelaciones ML (50 sin código)
- [x] 19/06 Merchant: dirección de tienda agregada + 2 imágenes "×" corregidas + diagnóstico 167
- [x] 20/06 Merchant: diagnóstico 76 "not synced" = 66 sin stock + ~19 ocultos → NO es problema, exclusión correcta (cierran solos al reponer stock). El problema real son los 167 desaprobados + dirección comercial faltante en Merchant Center

## 🎨 Proyectos en Claude Design (claude.ai/design)
_Barrido 20/06. Tablero central de todos tus trabajos ahí._

### 🔴 Atrasados / detenidos (necesitan empujón o definición)
- [ ] **Pantalla de Ventas en Vivo** — solo un sketch del 27/05, nunca se diseñó. → definir si se hace o se funde con el Monitor KDS de bodega. [link](https://claude.ai/design/p/446f8e0c-07a4-4c52-bad9-3a3e535dda50)
- [ ] **Untitled** y **Bot Comerciales** — vacíos, sin iniciar. → definir alcance o borrar. [Untitled](https://claude.ai/design/p/595a6a84-b6a9-4504-bf77-d6fcb18be95a) · [Bot Comerciales](https://claude.ai/design/p/5b64dfff-b197-4ce1-836a-b39bbf79252e)

### 🟡 Maqueta lista — esperan decisión/datos tuyos
- [ ] **Venta por Mayor** (portal B2B) — el más rentable del lote (apalanca sourcing 1688/Alila; modelo venta CONTRA compra validada, cero inventario). Avance 20/06: ✅ admin terminado y verificado · ✅ catálogo piloto `mayorista_catalogo.xlsx` (117 prods = 63 monopolio + 54 oportunidad, costo 1688 + 3 tramos ×2,5/×2,2/×2,0; 2 sin costo por completar) · ✅ banco Scotiabank cuenta 000993556831 · ✅ spec + plan de implementación (`docs/superpowers/`) · ✅ **lista PDF para WhatsApp** `Lista_Precios_Mayorista.pdf` (enviable HOY) · rama git `portal-mayorista` creada. **Decidido:** Next.js+Vercel sobre `comercialsolutions.cl` (raíz); plan dual = lista PDF ya + build de la página en paralelo + conectar dominio al restaurarlo. **Falta:** tipo de cuenta + correo comprobantes · embalaje (unid x caja, mín. compra) · logo sin recuadro · **llevar portal a producción y cargar el catálogo**. [link](https://claude.ai/design/p/ef87aa3b-967d-47c9-bbbe-ab1aa17567a6)
- [ ] **Etiqueta de precios** — elegir versión A o B → luego armar hoja A4 imprimible en serie. [link](https://claude.ai/design/p/402e8416-bb0d-4225-8d80-203b04bca366)
- [ ] **Bodega: Arriendo + Fulfillment** — elegir nombre (Despega/Enkaja/La Central/Almacena) + WhatsApp/IG reales + tarifas internas; exportar PNG del kit de redes. [link](https://claude.ai/design/p/d2dd348d-9927-4dbd-97b3-c593cec2c096)
- [ ] **Base de Maestros/Técnicos** — falta WhatsApp real, URL del Tally, fotos reales de obra. [link](https://claude.ai/design/p/b1345f73-88c2-4da4-aa0c-26f5d2a8e1e2)
- [ ] **Play Park** (cliente agencia) — reemplazar fotos placeholder por las del IG del cliente. [link](https://claude.ai/design/p/9a9f204e-cdbf-48f8-bc3f-5685606a7611)
- [ ] **Pagina Web Trade (Trade Pro)** — decidir período del programa (trimestre fijo recomendado) + ajustar cortes/% a margen real; backend en producción. [link](https://claude.ai/design/p/20488726-9ce3-4533-8117-c5727f18c869)
- [ ] **Paginas Web / Cumbre** (agencia) — conectar casos reales cuando existan; opción: demo navegable "Verde Café" como pieza de venta. [link](https://claude.ai/design/p/bba8da08-cf8e-4e20-9740-cb9f3a7a36c0)

### 🟢 Material listo — a ejecutar
- [ ] **Marketing** — kit de creativos + plan de automatización; siguiente paso = montar las **3 automatizaciones que recuperan plata** (carrito abandonado, chatbot FAQ, pedido de reseñas). [link](https://claude.ai/design/p/f41843cd-5c1b-4b1a-b0df-db07fed4fb98)
- [ ] **Inventario On Line** — prototipo + paquete handoff a Claude Code listos; pendiente backend real (parser, sync celular↔PC, Defontana). [link](https://claude.ai/design/p/3dc552be-fe9b-476f-a69d-a2ed2ea0d799)
- [x] **Mi página web** — almacén de wireframes ya llevados a producción como mu-plugins (sin pendiente). [link](https://claude.ai/design/p/7cf3b8b1-39b5-4c9e-bc52-089f8d67a7a1)

---
_Otros proyectos (web victtorino, apps, agencia, etc.) → ver MEMORY.md en la carpeta de memoria._
