#!/usr/bin/env bash
# ops/setup/rotate-bridge-token.sh
#
# Rotaciona o BRIDGE_TOKEN usado pelo openclaw-bridge (nginx) e recarrega.
# O token novo passa a valer imediatamente; o antigo para de funcionar.
#
# Uso (na VPS, root):
#   bash ops/setup/rotate-bridge-token.sh
#
# Saida: imprime o novo token.

set -euo pipefail

TOKEN_FILE="/root/.openclaw/secure/bridge-token.env"
NGINX_SITE="/etc/nginx/sites-available/openclaw-bridge"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERRO: rode como root"
  exit 1
fi

if [ ! -f "$NGINX_SITE" ]; then
  echo "ERRO: $NGINX_SITE nao existe. Rode openclaw-bridge.sh antes."
  exit 2
fi

OLD_TOKEN=""
[ -f "$TOKEN_FILE" ] && OLD_TOKEN="$(grep -E '^BRIDGE_TOKEN=' "$TOKEN_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")"

NEW_TOKEN="$(openssl rand -hex 32)"
printf 'BRIDGE_TOKEN=%s\n' "$NEW_TOKEN" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"

# Substitui o token na linha do map
if [ -n "$OLD_TOKEN" ]; then
  sed -i "s|\"Bearer ${OLD_TOKEN}\"|\"Bearer ${NEW_TOKEN}\"|g" "$NGINX_SITE"
else
  sed -i -E "s|(\"Bearer )[a-f0-9]+\"|\1${NEW_TOKEN}\"|g" "$NGINX_SITE"
fi

if ! nginx -t 2>&1; then
  echo "ERRO: nginx -t falhou apos rotacao. Revertendo nao implementado."
  exit 3
fi

systemctl reload nginx

echo "============================================================"
echo "  Token rotacionado."
echo "  Novo token (file): $TOKEN_FILE"
echo ""
echo "  Valor:"
echo "    $NEW_TOKEN"
echo "============================================================"
