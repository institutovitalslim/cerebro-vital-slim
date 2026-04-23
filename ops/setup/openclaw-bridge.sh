#!/usr/bin/env bash
# ops/setup/openclaw-bridge.sh
#
# Configura nginx + Let's Encrypt + bearer auth como bridge HTTPS para o
# gateway local do OpenClaw (localhost:18789), expondo via dominio publico
# (default: openclaw.institutovitalslim.com.br).
#
# Resultado: Claude (rodando fora da VPS, com HTTPS only) consegue chamar
# o OpenClaw atraves de https://openclaw.institutovitalslim.com.br/...
# desde que envie header "Authorization: Bearer <BRIDGE_TOKEN>".
#
# Uso (na VPS, root):
#   bash ops/setup/openclaw-bridge.sh
#
# Variaveis opcionais:
#   DOMAIN=openclaw.exemplo.com           default: openclaw.institutovitalslim.com.br
#   UPSTREAM_PORT=18789                   default: 18789
#   LE_EMAIL=email@exemplo.com            default: tiarofernandes@gmail.com
#
# Saida final: imprime URL e BRIDGE_TOKEN.

set -euo pipefail

DOMAIN="${DOMAIN:-openclaw.institutovitalslim.com.br}"
UPSTREAM_PORT="${UPSTREAM_PORT:-18789}"
LE_EMAIL="${LE_EMAIL:-tiarofernandes@gmail.com}"
NGINX_SITE_NAME="openclaw-bridge"
TOKEN_DIR="/root/.openclaw/secure"
TOKEN_FILE="${TOKEN_DIR}/bridge-token.env"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERRO: rode como root (sudo bash $0)"
  exit 1
fi

echo "================================================="
echo " OpenClaw bridge setup"
echo " dominio:   $DOMAIN"
echo " upstream:  127.0.0.1:${UPSTREAM_PORT}"
echo " token em:  $TOKEN_FILE"
echo "================================================="

# 1. Confere se o gateway local esta de pe (avisa se nao, mas continua)
echo ""
echo "[1/8] gateway local em :${UPSTREAM_PORT}..."
if ss -tln 2>/dev/null | grep -q ":${UPSTREAM_PORT}\b"; then
  echo "      OK"
else
  echo "      AVISO: nada escutando em :${UPSTREAM_PORT} (nginx vai responder 502)"
fi

# 2. Confere portas 80/443 (so aborta se alguem que nao seja nginx ja tomou)
echo ""
echo "[2/8] portas 80/443..."
for port in 80 443; do
  HOLDER="$(ss -tlnp 2>/dev/null | awk -v p=":${port}\$" '$4 ~ p {print $0; exit}')"
  if [ -n "$HOLDER" ]; then
    if echo "$HOLDER" | grep -q nginx; then
      echo "      :${port} ja em uso por nginx (ok, vamos reaproveitar)"
    else
      echo "      ERRO: porta ${port} ocupada por outro processo:"
      echo "      $HOLDER"
      echo ""
      echo "      Pare o processo que esta usando e rode novamente,"
      echo "      ou ajuste a config dele para liberar a porta."
      exit 2
    fi
  else
    echo "      :${port} livre"
  fi
done

# 3. Confere DNS (so avisa, nao aborta)
echo ""
echo "[3/8] DNS de ${DOMAIN}..."
apt-get install -y -qq dnsutils >/dev/null 2>&1 || true
DNS_IP="$(dig +short "$DOMAIN" @1.1.1.1 2>/dev/null | head -1)"
THIS_IP="$(curl -sS --max-time 5 https://api.ipify.org 2>/dev/null || echo unknown)"
echo "      DNS aponta:  ${DNS_IP:-(nada)}"
echo "      VPS public:  ${THIS_IP}"
if [ -z "$DNS_IP" ]; then
  echo "      ERRO: DNS nao resolveu. Confirme o A record na HostGator."
  exit 3
fi
if [ "$THIS_IP" != "unknown" ] && [ "$DNS_IP" != "$THIS_IP" ]; then
  echo "      AVISO: DNS != IP da VPS — Let's Encrypt vai falhar se DNS nao chegar aqui"
fi

# 4. Instala nginx + certbot
echo ""
echo "[4/8] instalando nginx + certbot..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx certbot python3-certbot-nginx openssl >/dev/null
echo "      OK"

# 5. Gera ou reutiliza BRIDGE_TOKEN
echo ""
echo "[5/8] BRIDGE_TOKEN..."
mkdir -p "$TOKEN_DIR"
chmod 700 "$TOKEN_DIR"
if [ -f "$TOKEN_FILE" ] && grep -qE '^BRIDGE_TOKEN=.{32,}' "$TOKEN_FILE"; then
  TOKEN="$(grep -E '^BRIDGE_TOKEN=' "$TOKEN_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")"
  echo "      reutilizando token existente"
else
  TOKEN="$(openssl rand -hex 32)"  # 64 hex chars
  printf 'BRIDGE_TOKEN=%s\n' "$TOKEN" > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
  echo "      token novo gerado"
fi
TOKEN_LEN="${#TOKEN}"
TOKEN_PREVIEW_HEAD="${TOKEN:0:6}"
TOKEN_PREVIEW_TAIL="${TOKEN: -6}"

# 6. Configura nginx (HTTP first, certbot depois adiciona HTTPS)
echo ""
echo "[6/8] gerando config nginx..."
cat > "/etc/nginx/sites-available/${NGINX_SITE_NAME}" <<NGINX
# Auto-gerado por ops/setup/openclaw-bridge.sh
# Bridge: ${DOMAIN} -> http://127.0.0.1:${UPSTREAM_PORT}

map \$http_authorization \$bridge_auth_ok {
  default 0;
  "Bearer ${TOKEN}" 1;
}

limit_req_zone \$binary_remote_addr zone=openclaw_bridge:10m rate=30r/s;

server {
  listen 80;
  listen [::]:80;
  server_name ${DOMAIN};

  # Liveness publico (sem auth) — pra checagem externa
  location = /__bridge_alive {
    access_log off;
    add_header Content-Type text/plain;
    return 200 "ok\n";
  }

  # ACME HTTP-01 challenge (certbot)
  location ^~ /.well-known/acme-challenge/ {
    root /var/www/html;
  }

  location / {
    if (\$bridge_auth_ok = 0) {
      add_header WWW-Authenticate "Bearer realm=openclaw" always;
      return 401;
    }
    limit_req zone=openclaw_bridge burst=60 nodelay;

    proxy_pass http://127.0.0.1:${UPSTREAM_PORT};
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;

    # Bridge token NAO chega no upstream — gateway tem auth interna propria
    proxy_set_header Authorization "";

    proxy_read_timeout 600s;
    proxy_send_timeout 600s;
    proxy_connect_timeout 30s;
  }

  client_max_body_size 50M;
}
NGINX

ln -sf "/etc/nginx/sites-available/${NGINX_SITE_NAME}" \
       "/etc/nginx/sites-enabled/${NGINX_SITE_NAME}"

mkdir -p /var/www/html

if ! nginx -t 2>&1; then
  echo "ERRO: config do nginx invalida. Rode 'nginx -t' pra detalhes."
  exit 4
fi

systemctl enable --now nginx >/dev/null 2>&1 || true
systemctl reload nginx
echo "      OK"

# 7. Solicita cert TLS
echo ""
echo "[7/8] cert Let's Encrypt para ${DOMAIN}..."
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  echo "      cert existente encontrado, reaplicando config nginx (--reinstall)"
  certbot --nginx --non-interactive --reinstall \
    --agree-tos --email "${LE_EMAIL}" --no-eff-email \
    --domains "${DOMAIN}" --redirect || {
      echo "      AVISO: certbot --reinstall falhou, mas cert existente permanece"
    }
else
  certbot --nginx --non-interactive \
    --agree-tos --email "${LE_EMAIL}" --no-eff-email \
    --domains "${DOMAIN}" --redirect || {
      echo "ERRO: certbot falhou. veja /var/log/letsencrypt/letsencrypt.log"
      exit 5
    }
fi

systemctl reload nginx
systemctl enable --now certbot.timer >/dev/null 2>&1 || true
echo "      OK (renovacao automatica ativada via certbot.timer)"

# 8. Sanity test
echo ""
echo "[8/8] testando bridge..."
sleep 2
ALIVE="$(curl -sS --max-time 8 "https://${DOMAIN}/__bridge_alive" 2>&1 || true)"
AUTH401="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "https://${DOMAIN}/" 2>&1 || true)"
AUTHOK="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 \
  -H "Authorization: Bearer ${TOKEN}" "https://${DOMAIN}/" 2>&1 || true)"

echo "      /__bridge_alive ......... ${ALIVE}"
echo "      / sem token ............. ${AUTH401}  (esperado: 401)"
echo "      / com token ............. ${AUTHOK}   (esperado: 2xx ou 5xx do upstream)"

cat <<EOF

============================================================
  OpenClaw bridge UP

  URL              https://${DOMAIN}
  Liveness         https://${DOMAIN}/__bridge_alive
  Token (preview)  ${TOKEN_PREVIEW_HEAD}...${TOKEN_PREVIEW_TAIL}  (${TOKEN_LEN} chars)
  Token (file)     ${TOKEN_FILE}

  Pra ver o token completo (e copiar pra mandar ao Claude):
    cat ${TOKEN_FILE}

  Pra revogar acesso (rotaciona token + recarrega nginx):
    bash /root/cerebro-vital-slim/ops/setup/rotate-bridge-token.sh

  Pra checar status:
    systemctl status nginx
    tail -f /var/log/nginx/access.log

============================================================
EOF
