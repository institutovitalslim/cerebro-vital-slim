#!/usr/bin/env bash
# ops/diag/expose-openclaw-tunnel.sh
#
# Sobe um Cloudflare Quick Tunnel apontando para o gateway local do OpenClaw
# (default localhost:18789) para que o Claude (rodando fora da VPS, com
# outbound HTTPS apenas) consiga acessar o OpenClaw temporariamente.
#
# Uso (na VPS, como root):
#   bash ops/diag/expose-openclaw-tunnel.sh           # default porta 18789
#   bash ops/diag/expose-openclaw-tunnel.sh 18789     # explicito
#
# Ao subir, imprime uma URL https://xxx-xxx-xxx.trycloudflare.com
# Para encerrar: Ctrl+C (mata o cloudflared, fecha o tunel).
#
# IMPORTANTE:
#   - URL trycloudflare e PUBLICA. Qualquer um com a URL bate no gateway.
#   - A unica protecao e o token de auth do gateway (gateway.auth.token).
#   - APOS USO: encerrar com Ctrl+C E rotacionar o token do gateway.

set -euo pipefail

PORT="${1:-18789}"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERRO: rode como root (sudo bash $0)"
  exit 1
fi

# 1) Verifica se o gateway esta escutando antes de subir o tunel
echo "[1/3] Conferindo se ha algo escutando em localhost:${PORT}..."
if ! ss -tln "( sport = :${PORT} )" 2>/dev/null | grep -q ":${PORT}"; then
  echo "AVISO: nada escutando em localhost:${PORT}."
  echo "       Verifique 'pm2 status' / 'systemctl status openclaw' antes de continuar."
  echo "       (vou subir o tunel mesmo assim, mas as chamadas vao retornar 502)"
fi

# 2) Instala cloudflared se nao estiver instalado
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "[2/3] cloudflared nao encontrado, instalando..."
  ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
  case "$ARCH" in
    amd64|x86_64) PKG_ARCH="amd64" ;;
    arm64|aarch64) PKG_ARCH="arm64" ;;
    armhf|armv7l) PKG_ARCH="armhf" ;;
    *) echo "ERRO: arquitetura nao suportada: $ARCH"; exit 2 ;;
  esac
  TMP_DEB="/tmp/cloudflared.deb"
  curl -fsSL --max-time 60 \
    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${PKG_ARCH}.deb" \
    -o "$TMP_DEB"
  dpkg -i "$TMP_DEB" >/dev/null
  rm -f "$TMP_DEB"
  echo "      cloudflared instalado: $(cloudflared --version 2>&1 | head -1)"
else
  echo "[2/3] cloudflared ja instalado: $(cloudflared --version 2>&1 | head -1)"
fi

# 3) Sobe o tunel em foreground (Ctrl+C encerra)
echo ""
echo "============================================================"
echo " [3/3] Subindo Cloudflare Quick Tunnel"
echo "       Origem: http://localhost:${PORT}"
echo ""
echo "  Aguarde aparecer a linha 'https://xxx-xxx-xxx.trycloudflare.com'"
echo "  Copie essa URL e envie ao Claude."
echo ""
echo "  Para encerrar o tunel: Ctrl+C neste terminal."
echo "  APOS USO: rotacionar gateway.auth.token no config do OpenClaw."
echo "============================================================"
echo ""

exec cloudflared tunnel --no-autoupdate --url "http://localhost:${PORT}"
