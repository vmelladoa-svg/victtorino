# Plan de fix definitivo — victtorino.cl

**Fecha:** 2026-05-26
**Síntoma:** Error 500 / pantalla blanca intermitente, en wp-admin y en páginas públicas, sin patrón claro.
**Causa raíz:** Elementor Pro 3.35.1 incompatible con Elementor Core 4.0.4 (cambio mayor de arquitectura en v4).

---

## ANTES DE EMPEZAR — backup obligatorio

Sin acceso a cPanel/FTP, tu única red de seguridad es un backup de plugin desde wp-admin.

1. Entrar a `https://victtorino.cl/wp-admin/`
2. Si **no** tienes UpdraftPlus o similar:
   - Plugins → Añadir nuevo → buscar "UpdraftPlus"
   - Instalar y activar
3. Ajustes → UpdraftPlus Backups → "Hacer copia de seguridad ahora"
4. Marcar las 4 casillas (bases de datos, plugins, themes, uploads)
5. Esperar a que termine y verificar que aparece en "Existing backups"

**No avances al paso 1 hasta tener backup verde.**

---

## PASO 1 (crítico) — Actualizar Elementor Pro a 4.x

### 1.1 Verificar licencia activa
- wp-admin → Elementor → Licencia
- Debe decir "Activado" en verde. Si no, activar con la clave antes de seguir.

### 1.2 Habilitar Modo Mantenimiento
- wp-admin → Elementor → Herramientas → pestaña "Modo Mantenimiento"
- Modo: **Mantenimiento**
- Quién puede acceder: **Solo administradores**
- Guardar cambios.

### 1.3 Actualizar el plugin
- wp-admin → Plugins → Plugins instalados
- Buscar "Elementor Pro" → click "Actualizar ahora"
- Esperar a que termine (no cerrar la pestaña).

### 1.4 Verificar
- En la misma página debería leerse `Elementor Pro 4.0.x` o superior.
- Plugins → comprobar que no aparezca un aviso rojo de "incompatible" debajo de Elementor o Elementor Pro.

### 1.5 Quitar Modo Mantenimiento
- Elementor → Herramientas → Modo Mantenimiento → **Deshabilitado**
- Guardar.

### 1.6 Smoke test (lo verifico yo después)
- Abrir en incógnito: home, /tienda/, una página de producto, /carrito/
- Las 4 deben cargar sin error.
- Avísame cuando termines y reviso desde acá.

---

## PASO 2 (alto) — Activar Redis Object Cache

Tienes el plugin instalado pero **desactivado** (la API reporta `external_object_cache: None`). Activarlo baja la carga de DB y reduce probabilidad de 500 por timeout.

1. wp-admin → Ajustes → Redis
2. Verificar que diga "Status: Connected" en verde.
   - Si dice "Not connected": tu hosting puede no tener Redis levantado. En ese caso saltar este paso y pedirle al hosting que active Redis (es gratis en planes business de la mayoría).
3. Si conecta: click "Enable Object Cache"
4. La página debería recargar y mostrar "Status: Connected ✅"
5. Verificar mejora: navegar 3-4 páginas en incógnito; deberían sentirse más rápidas.

---

## PASO 3 (medio) — Limpiar plugins redundantes

Tienes pares de plugins haciendo lo mismo (causa común de 500 intermitente):

### 3.1 Optimización CSS/JS — elegir UNO
- **LiteSpeed Cache** (ya activo, integrado al servidor) ← **mantener**
- **Autoptimize** (duplica funciones de LiteSpeed) ← **desactivar**

Pasos:
1. Plugins → Autoptimize → "Desactivar"
2. LiteSpeed Cache → Caché → Purge All
3. Smoke test: home + producto + carrito en incógnito.
4. Si todo OK por 24 hrs → Plugins → Autoptimize → "Borrar"

### 3.2 Optimización imágenes — elegir UNO
- **EWWW Image Optimizer** ← **mantener** (más estable y usado por catálogo)
- **Smush** ← **desactivar**

Pasos:
1. Plugins → Smush → "Desactivar"
2. Smoke test
3. Si todo OK por 24 hrs → "Borrar"

### 3.3 Reducir superficie
Otros plugins a revisar si no los usas activamente:
- **ElementsKit Lite** — addon de Elementor, solo lo necesitas si tus páginas usan sus widgets
- **ShopLentor** — addon de WooCommerce, mismo criterio
- **YITH Request a Quote** — solo si pides cotizaciones
- **Hotjar** — solo si revisas grabaciones; si no, desactivar (acelera bastante el front)

**Regla:** desactivar uno a la vez. Esperar 24 hrs. Si nada se rompió → borrar.

---

## PASO 4 (medio) — Activar log de errores PHP

Para que la PRÓXIMA vez que caiga (si vuelve a caer) tengamos log.

1. Plugins → Añadir nuevo → buscar **"WP Debugging"** (por Andy Fragen)
2. Instalar y activar
3. Herramientas → WP Debugging → marcar:
   - `WP_DEBUG`
   - `WP_DEBUG_LOG`
   - **NO** marcar `WP_DEBUG_DISPLAY` (eso mostraría errores a visitantes)
4. Guardar
5. Si vuelve a caer: el log queda en `/wp-content/debug.log` y se puede leer con un plugin tipo "WP File Manager" o pedirme yo que lo lea por la API.

---

## PASO 5 (medio) — Subir `max_input_vars`

Actualmente en 1000. Recomendado 5000+ para sitios con muchos productos.

Sin cPanel no se puede tocar `php.ini` directo. Opciones:

### 5.1 Vía `.htaccess` (probar primero)
1. Plugins → Añadir nuevo → "WP Htaccess Editor"
2. Editar `.htaccess` y agregar al final:
   ```
   <IfModule mod_php.c>
   php_value max_input_vars 5000
   </IfModule>
   ```
3. Guardar
4. Verificar: wp-admin → Herramientas → Salud del sitio → Info → Servidor → buscar "Variables máximas de entrada". Debería decir 5000.
5. Si sigue en 1000: tu hosting tiene PHP-FPM y `.htaccess` no funciona. Saltar a 5.2.

### 5.2 Pedírselo al hosting
Mandar este mensaje:
> "Hola, necesito subir `max_input_vars` de 1000 a 5000 en mi cuenta. Mi sitio es victtorino.cl. Gracias."

Hostings buenos lo hacen en 1 hora.

---

## CHECKLIST FINAL

- [ ] Backup UpdraftPlus completo y verificado
- [ ] Elementor Pro actualizado a 4.x
- [ ] Sin avisos rojos de incompatibilidad
- [ ] Redis Object Cache habilitado
- [ ] Autoptimize desactivado (LiteSpeed se queda)
- [ ] Smush desactivado (EWWW se queda)
- [ ] WP Debugging activo (WP_DEBUG_LOG, sin DISPLAY)
- [ ] `max_input_vars` ≥ 5000
- [ ] Smoke test: home, /tienda/, producto, carrito → todos OK 24 hrs

---

## Si algo se rompe en el paso 1

1. UpdraftPlus → "Existing backups" → restaurar el del backup pre-update
2. Avisarme con el mensaje exacto que aparezca en pantalla
3. Plan B: bajar Core a 3.x con "WP Rollback" en vez de subir Pro
