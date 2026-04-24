#!/usr/bin/env bash
# ops/skills-sync/install-hook.sh
#
# Instala git hooks no clone local do cérebro (VPS) para sincronizar
# automaticamente as skills com /root/.openclaw/workspace/skills/ após
# cada git pull / git merge / git checkout.
#
# Rodar UMA vez na VPS, depois de clonar ou pull'ar o cérebro:
#   bash ops/skills-sync/install-hook.sh
#
# Os hooks criados:
#   .git/hooks/post-merge      → dispara após git pull com merge
#   .git/hooks/post-checkout   → dispara após git checkout de branch
#   .git/hooks/post-rewrite    → dispara após git rebase
#
# Todos chamam ops/skills-sync/sync-skills.sh em modo silencioso.

set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:${PATH:-}"

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo /root/cerebro-vital-slim)}"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"
SYNC_SCRIPT="${REPO_ROOT}/ops/skills-sync/sync-skills.sh"

if [ ! -d "${REPO_ROOT}/.git" ]; then
  echo "ERRO: ${REPO_ROOT} não é um repositório git." >&2
  exit 1
fi

if [ ! -f "$SYNC_SCRIPT" ]; then
  echo "ERRO: sync-skills.sh não encontrado em $SYNC_SCRIPT" >&2
  exit 2
fi

chmod +x "$SYNC_SCRIPT"

HOOK_CONTENT='#!/usr/bin/env bash
# Auto-gerado por ops/skills-sync/install-hook.sh
# Sincroniza cerebro/empresa/skills/ -> /root/.openclaw/workspace/skills/
export PATH="/usr/local/sbin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:${PATH:-}"
SYNC="$(git rev-parse --show-toplevel)/ops/skills-sync/sync-skills.sh"
if [ -x "$SYNC" ]; then
  bash "$SYNC" >/dev/null 2>&1 || true
fi
'

mkdir -p "$HOOKS_DIR"

for hook in post-merge post-checkout post-rewrite; do
  HOOK_PATH="${HOOKS_DIR}/${hook}"

  # Preservar hook existente se já tem conteúdo customizado
  if [ -f "$HOOK_PATH" ] && ! grep -q "ops/skills-sync/sync-skills.sh" "$HOOK_PATH" 2>/dev/null; then
    echo "AVISO: $HOOK_PATH já existe com conteúdo customizado. Fazendo backup em ${HOOK_PATH}.bak"
    cp "$HOOK_PATH" "${HOOK_PATH}.bak"
    # Anexar a chamada de sync ao final do hook existente
    printf '\n# --- skill sync (auto-gerado) ---\nSYNC="$(git rev-parse --show-toplevel)/ops/skills-sync/sync-skills.sh"\n[ -x "$SYNC" ] && bash "$SYNC" >/dev/null 2>&1 || true\n' >> "$HOOK_PATH"
  else
    printf '%s' "$HOOK_CONTENT" > "$HOOK_PATH"
  fi

  chmod +x "$HOOK_PATH"
  echo "  ✓ instalado: $HOOK_PATH"
done

# Validar dependências
echo
echo "=== validação ==="
for cmd in rsync git; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ✓ $cmd: $(command -v "$cmd")"
  else
    echo "  ✗ $cmd: NÃO INSTALADO — rodar 'apt-get install -y $cmd'"
  fi
done

echo
echo "=== fazendo primeiro sync agora ==="
bash "$SYNC_SCRIPT" || {
  echo
  echo "ERRO no primeiro sync. Verifique o log em ops/skills-sync/logs/"
  exit 3
}

echo
echo "============================================================"
echo "  Instalação concluída."
echo "  A partir de agora, todo 'git pull' sincroniza automaticamente"
echo "  cerebro/empresa/skills/ -> /root/.openclaw/workspace/skills/"
echo
echo "  Para rodar sync manualmente:"
echo "    bash $SYNC_SCRIPT"
echo
echo "  Para preview sem mudar nada:"
echo "    bash $SYNC_SCRIPT --dry-run"
echo "============================================================"
