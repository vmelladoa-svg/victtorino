# Informe Gerente Comercial - Victtorino
**Fecha:** 13 de mayo de 2026
**Cuentas:** PREMIUMGRIFERIAS1 (C1) | VICTTORINOFICIAL2 (C2) | NOVAGRIFERIAS3 (C3)

---

## 1. RESUMEN EJECUTIVO

| Indicador | C1 | C2 | C3 |
|---|---|---|---|
| Reputacion | 5_green ATENCION | 5_green OK | 5_green OK |
| Items activos | 171 | 174 | 176 |
| Ventas 60d (ordenes) | 53 | — | 138 |
| Facturacion 60d | $1.322.775 | — | $5.629.131 |
| Preguntas sin responder | 0 | — | 2 (*) |
| Stock critico | 1 item | — | 2 items |
| Stock muerto | 10 items | — | 8 items |

(*) Items pausados/sin stock — responder manualmente desde panel ML

---

## 2. REPUTACION

### C1 - PREMIUMGRIFERIAS1 — ATENCION REQUERIDA

| Metrica | Actual | Limite | Estado |
|---|---|---|---|
| Reclamos | 1.75% | 1% | SOBRE LIMITE |
| Demoras despacho | 1.85% | 1% | SOBRE LIMITE |
| Cancelaciones | 1.75% | 1% | SOBRE LIMITE |

**Causa raiz — Demoras (1.85%):**
processing_time=None en todos los items hace que ML cuente envios al dia siguiente como demora. Hay 9 ordenes con 3-4 dias de retraso registradas en el periodo.

**Causa raiz — Reclamos y cancelaciones (1.75%):**
2 mediaciones en marzo 2026 sobre el Espejo Redondo Doble Cara Con Aumento X3. Incidentes aislados sin problema de calidad confirmado. El espejo sigue siendo el 4to y 6to mas vendido en C1 (9u en 60d, $140.110).

**Accion requerida (Victor):**
Seller Center → Configuracion → Tiempo de preparacion → **1 dia habil**
No es modificable por API. Las metricas de marzo saldran del computo de 60 dias en ~2 semanas.

### C2 - VICTTORINOFICIAL2

Reputacion sana. Sin alertas.

### C3 - NOVAGRIFERIAS3

| Metrica | Actual | Limite | Estado |
|---|---|---|---|
| Reclamos | 0.68% | 1% | OK |
| Demoras | 0.78% | 1% | OK |
| Cancelaciones | 0.68% | 1% | OK |

---

## 3. VENTAS 60 DIAS

### C1 — 53 ordenes | $1.322.775 CLP

| Item | Unidades | Facturacion |
|---|---|---|
| Lavaplatos Sobre Cubierta 80x44 Inox | 10u | $394.923 |
| Lavaplatos Lavacopas Empotrado 37x32 (v1) | 6u | $77.940 |
| Lavaplatos Lavacopas Empotrado 37x32 (v2) | 5u | $64.950 |
| Espejo Redondo Doble Cara X3 Al Muro | 5u | $74.950 |
| Valvula Desvio Diverter 3 Vias 1/2 y 3/8 | 4u | $92.002 |
| Espejo Redondo Doble Cara X3 Pedestal | 4u | $65.160 |
| Llave Lavadora Duplex He-He 1/2 x 3/4 | 4u | $33.560 |
| Porta Toalla Barra 60 Cm Acero | 2u | $36.780 |
| Lavaplatos 100x50 Sobreponer | 2u | $84.380 |
| Lavaplatos Simple 100x44 Sec.Izquierdo | 2u | $87.180 |

### C3 — 138 ordenes | $5.629.131 CLP

| Item | Unidades | Facturacion |
|---|---|---|
| Lavaplatos Simple 80x44 Sec. Derecho | 22u | $761.088 |
| Lavaplatos Empotrado Simple 100x44 | 13u | $483.442 |
| Lavaplatos Empotrado Simple 80x44 Izq | 11u | $350.287 |
| Lavaplatos Empotrado Simple 100x44 Izq | 10u | $324.121 |
| Pack 6 Rollos Papel Higienico Industrial | 9u | $64.470 |
| Lavaplatos Sobre Cubierta 80x44 Inox | 8u | $273.520 |
| Receptaculo Ducha Metacrilato + Fibra | 6u | $766.740 |
| Pack Lavaplatos 80x44 + Llave | 6u | $411.640 |
| Receptaculo Piso Ducha 70x70 Acero | 5u | $188.714 |
| Pack Lavaplatos 37x32 + Llave Lavacopa | 5u | $121.265 |

> C3 factura 4,3x mas que C1 en el mismo periodo. La reputacion danada de C1 reduce visibilidad en algoritmo ML.

---

## 4. PREGUNTAS SIN RESPONDER

| Cuenta | Preguntas | Detalle |
|---|---|---|
| C1 | 0 | Sin pendientes |
| C2 | — | Auditoria sesion anterior |
| C3 | 2 | Items pausados — responder manualmente |

**C3 — Preguntas pendientes (items sin stock, no se pueden responder por API):**

| Item | Pregunta | Respuesta sugerida |
|---|---|---|
| Pack Lavaplatos 37x32 + Llave | "Viene con desague" | El pack incluye lavaplatos y llave lavacopa. El desague no esta incluido y debe adquirirse por separado. |
| Lavaplatos Sobreponer 150x50 2 Bachas | "Lo manda por que medio?" | Por dimensiones (150x50 cm) el envio se realiza por servicio de carga/flete. Tambien disponible retiro en local. |

---

## 5. STOCK CRITICO — REPOSICION URGENTE

| Cuenta | Item | Stock | Velocidad | Dias restantes |
|---|---|---|---|---|
| C1 | Llave Lavadora Duplex He-He 1/2x3/4 | **3u** | 4u/60d | ~45 dias |
| C3 | Jabonera Colomba Cromada Vidrio | **1u** | 3u/60d | ~20 dias |
| C3 | Receptaculo Piso Ducha 70x70 Acero | **3u** | 5u/60d | ~36 dias |

---

## 6. STOCK MUERTO — REVISION DE PRECIO Y VISIBILIDAD

### C1 (10 items sin movimiento)

| Item | Stock | Precio | Situacion |
|---|---|---|---|
| Toalla Interfoliada 200u (pub 1) | 173u | $2.774 | Duplicado — igual en C2 y C3 |
| Toalla Interfoliada 200u (pub 2) | 173u | $2.774 | Duplicado — igual en C2 y C3 |
| Rollo Higienico Industrial 216m | 94u | $1.193 | Sin movimiento |
| Desague Lavaplatos 3.5" Plastico | 58u | $5.887 | Sin movimiento |
| Flexible Lavadora Curva Hi-Hi 3/4 150cm | 29u | $3.876 | Sin movimiento |

### C3 (8 items sin movimiento)

| Item | Stock | Precio | Situacion |
|---|---|---|---|
| Toalla Interfoliada 200u (pub 1) | 173u | $2.920 | Duplicado — igual en C1 y C2 |
| Toalla Interfoliada 200u (pub 2) | 173u | $2.920 | Duplicado — igual en C1 y C2 |
| Rollo Higienico Industrial 216m | 81u | $1.790 | Sin movimiento |
| Lavaplatos 37x32 Chocolate Plateado | 78u | $17.850 | Sin movimiento |
| Desague Lavaplatos 3.5" | 58u | $6.197 | Sin movimiento |

> Alerta: la Toalla Interfoliada 200u aparece duplicada en C1, C2 Y C3 (6 publicaciones en total con ~1.000 unidades de stock acumulado entre las 3 cuentas). Requiere decision: liquidar precio, consolidar publicaciones o revisar canal de venta.

---

## 7. OPTIMIZACION DE FICHAS — TRABAJO REALIZADO EN SESION

### Atributos completados automaticamente

| Cuenta | Items procesados | Atributos aplicados |
|---|---|---|
| C1 - PREMIUMGRIFERIAS1 | 163 | 272 |
| C2 - VICTTORINOFICIAL2 | 163 | 230 |
| C3 - NOVAGRIFERIAS3 | 175 | 291 |
| **TOTAL** | **501** | **793** |

### Fotos mejoradas (cruce entre cuentas por SKU)

| Cuenta | Publicaciones mejoradas | Bloqueadas (has_bids) |
|---|---|---|
| C1 | 14 | 8 |
| C2 | 51 | 14 |
| C3 | 18 | 12 |
| **TOTAL** | **83** | **34** |

Las 34 publicaciones bloqueadas se actualizaran automaticamente cuando venzan las transacciones activas.

### Descripciones mejoradas

| Cuenta | Mejoradas | Ya OK (>=350 chars) | Catalogo bloqueado |
|---|---|---|---|
| C1 | 3 | 88 | 80 |
| C2 | 3 | 79 | 92 |
| C3 | 2 | 77 | 97 |
| **TOTAL** | **8** | **244** | **269** |

---

## 8. ESTADO OBJETIVO HEALTH SCORE 80%

| Palanca | C1 | C2 | C3 |
|---|---|---|---|
| Atributos | COMPLETADO | COMPLETADO | COMPLETADO |
| Fotos | COMPLETADO | COMPLETADO | COMPLETADO |
| Descripciones | COMPLETADO | COMPLETADO | COMPLETADO |
| Videos espejos | Pendiente YouTube | Pendiente YouTube | Pendiente YouTube |

El health score en ML se actualiza en 1 a 24 horas. Los cambios de atributos, fotos y descripciones realizados hoy se reflejaran en el dashboard manana.

---

## 9. ACCIONES PENDIENTES

### Urgentes

| # | Responsable | Accion | Impacto |
|---|---|---|---|
| 1 | Victor | Seller Center C1: Tiempo de preparacion → 1 dia habil | Corrige demoras 1.85% |
| 2 | Victor | Reponer Jabonera Colomba C3 (1u, 20 dias) | Evita quiebre de stock |
| 3 | Victor | Reponer Receptaculo Ducha 70x70 C3 (3u, 36 dias) | Evita quiebre de stock |

### Proximas sesiones

| # | Responsable | Accion | Impacto |
|---|---|---|---|
| 4 | Victor | Subir video espejos a YouTube → dar URL | Palanca health score + conversion |
| 5 | Victor | Decision Toalla Interfoliada: liquidar / consolidar (6 pubs, ~1.000u en 3 cuentas) | Liberar capital |
| 6 | Victor | Responder manualmente 2 preguntas C3 (items pausados) | Atencion al cliente |
| 7 | Victor | Datos de costo C1 para auditoria de margenes | Detectar productos en perdida |
| 8 | Sistema | Reponer Llave Lavadora Duplex C1 (3u, 45 dias) | Evita quiebre |

---

## 10. ARCHIVOS DE AUTOMATIZACION

| Archivo | Descripcion |
|---|---|
| `refresh_token.py` | Renueva tokens de las 3 cuentas (ejecutar cada 5h) |
| `completar_atributos_c1.py` | Completa atributos C1 automaticamente |
| `completar_atributos_c2.py` | Completa atributos C2 automaticamente |
| `completar_atributos_c3.py` | Completa atributos C3 automaticamente |
| `mejorar_fotos_c1_c3.py` | Mejora fotos C1 y C3 cruzando imagenes por SKU |
| `mejorar_descripciones.py` | Mejora descripciones cortas en items no-catalogo |
| `auditoria_c1.py` | Auditoria completa C1 (ventas, stock, preguntas, rentabilidad) |
| `auditoria_c3.py` | Auditoria completa C3 (ventas, stock, preguntas, rentabilidad) |

---

*Informe generado por Gerente Comercial ML — Victtorino | 13 de mayo de 2026*
