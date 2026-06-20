#!/bin/bash
# Verifica el estado de sincronización de Google Merchant Center de victtorino.cl
# y manda el resumen por WhatsApp (CallMeBot). Pensado para correr una vez (12 jun 2026)
# vía Tarea Programada de Windows (Git Bash).

KEY="$HOME/.ssh/cloudways_victtorino_rsa"
HOST="master_hvfkgdweqe@164.92.65.11"
APP="applications/fdgkhxzdsv/public_html"
WA_PHONE="56996953815"
WA_KEY="5759352"

# Consulta el servidor por SSH y arma el resumen (prefijo de tablas = TNxaWC_)
MSG=$(ssh -i "$KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=25 "$HOST" "cd $APP && \
SYNC=\$(wp db query \"SELECT COUNT(DISTINCT post_id) FROM TNxaWC_postmeta WHERE meta_key='_wc_gla_synced_at';\" --skip-column-names 2>/dev/null); \
APR=\$(wp db query \"SELECT COUNT(*) FROM TNxaWC_postmeta WHERE meta_key='_wc_gla_mc_status' AND meta_value='approved';\" --skip-column-names 2>/dev/null); \
DIS=\$(wp db query \"SELECT COUNT(*) FROM TNxaWC_postmeta WHERE meta_key='_wc_gla_mc_status' AND meta_value='disapproved';\" --skip-column-names 2>/dev/null); \
PEN=\$(wp db query \"SELECT COUNT(*) FROM TNxaWC_postmeta WHERE meta_key='_wc_gla_mc_status' AND meta_value IN ('pending','expiring','unaffected');\" --skip-column-names 2>/dev/null); \
printf 'Sincronizados: %s\nAprobados: %s\nRechazados: %s\nPendientes/otros: %s' \"\${SYNC:-0}\" \"\${APR:-0}\" \"\${DIS:-0}\" \"\${PEN:-0}\"" 2>&1)

if [ -z "$MSG" ] || echo "$MSG" | grep -qiE 'permission denied|timed out|could not resolve|connection refused'; then
  FULL="⚠️ Merchant Center victtorino.cl: no pude conectarme al servidor para revisar. Detalle: $(echo "$MSG" | head -c 120)"
else
  FULL="📊 Merchant Center victtorino.cl ($(date +%d/%m))
$MSG

Revisa rechazos en Merchant Center > Diagnóstico si hay productos rechazados."
fi

curl -s -G -m 35 "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=$WA_PHONE" \
  --data-urlencode "apikey=$WA_KEY" \
  --data-urlencode "text=$FULL" >/dev/null
echo "[$(date)] enviado: $FULL"
