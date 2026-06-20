#!/usr/bin/env bash
# Chequeo de aprobaciones en Google Merchant Center + aviso WhatsApp.
# Compara los productos rechazados por "url_does_not_match_homepage" contra el baseline (167).
KEY="$HOME/.ssh/cloudways_victtorino_rsa"
LOG="/c/Users/dell/victtorino/trade_check_merchant.log"
BASE=167

N=$(ssh -i "$KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=30 master_hvfkgdweqe@164.92.65.11 \
  'cd applications/fdgkhxzdsv/public_html && wp db query "SELECT COUNT(*) FROM TNxaWC_gla_merchant_issues WHERE code=\"url_does_not_match_homepage\"" --skip-column-names' 2>/dev/null | tr -d '[:space:]')

if [ -z "$N" ]; then
  MSG="Trade Merchant: no se pudo consultar el servidor (revisar SSH). Baseline 167 rechazados."
elif [ "$N" -eq 0 ]; then
  MSG="Trade Merchant: 0 productos rechazados (eran 167). Catalogo APROBADO. Ya puedes ENCENDER la campana de Google Shopping (Google Ads cuenta 5005852466, estaba en pausa)."
elif [ "$N" -lt "$BASE" ]; then
  MSG="Trade Merchant: bajaron a $N rechazados (eran 167). Aprobaciones avanzando. Cuando llegue a 0 (o cerca) enciende la campana Shopping."
else
  MSG="Trade Merchant: siguen $N rechazados (eran 167). Google aun no re-revisa. Esperar otras 24h o revisar el feed."
fi

curl -s -G "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=56996953815" \
  --data-urlencode "text=$MSG" \
  --data-urlencode "apikey=5759352" >/dev/null 2>&1

echo "$(date '+%Y-%m-%d %H:%M') | rechazados=$N | $MSG" >> "$LOG"
