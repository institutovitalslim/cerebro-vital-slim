#!/usr/bin/env bash
# ops/skills-sync/verify-sync.sh
#
# Safety-net da Clara: verifica se todas as skills do cérebro estão
# presentes no workspace. Útil no startup de sessão ou antes de invocar
# uma skill específica.
#
# Uso:
#   bash ops/skills-sync/verify-sync.sh
#     → exit 0 se tudo alinhado, exit 1 se há skill faltando
#     → imprime diff com o que falta
#
#   bash ops/skills-sync/verify-sync.sh --fix
#     → se houver diferença, roda sync-skills.sh automaticamente

set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:${PATH:-}"

CEREBRO_ROOT="${CEREBRO_ROOT:-/root/cerebro-vital-slim}"
SRC="${CEREBRO_ROOT}/cerebro/empresa/skills"
DST="${WORKSPACE_SKILLS:-/root/.openclaw/workspace/skills}"

FIX=""
[ "${1:-}" = "--fix" ] && FIX="1"

missing=()
outdated=()

for skill_dir in "$SRC"/*/; do
  name="$(basename "$skill_dir")"
  # pular metadados do cerebro
  case "$name" in
    _*|logs|state) continue ;;
  esac

  skill_md_src="${skill_dir}SKILL.md"
  skill_md_dst="${DST}/${name}/SKILL.md"

  if [ ! -f "$skill_md_src" ]; then
    continue  # pasta sem SKILL.md não é skill canônica
  fi

  if [ ! -f "$skill_md_dst" ]; then
    missing+=("$name")
    continue
  fi

  # Comparar hash do SKILL.md (rápido, suficiente como sinal)
  src_hash="$(sha256sum "$skill_md_src" | cut -d' ' -f1)"
  dst_hash="$(sha256sum "$skill_md_dst" | cut -d' ' -f1)"
  if [ "$src_hash" != "$dst_hash" ]; then
    outdated+=("$name")
  fi
done

if [ "${#missing[@]}" -eq 0 ] && [ "${#outdated[@]}" -eq 0 ]; then
  echo "✓ todas as skills do cérebro estão sincronizadas com o workspace"
  exit 0
fi

echo "⚠ desalinhamento detectado entre cérebro e workspace"
echo
if [ "${#missing[@]}" -gt 0 ]; then
  echo "skills faltando no workspace:"
  for s in "${missing[@]}"; do echo "  - $s"; done
  echo
fi
if [ "${#outdated[@]}" -gt 0 ]; then
  echo "skills com versão diferente no workspace (SKILL.md divergente):"
  for s in "${outdated[@]}"; do echo "  - $s"; done
  echo
fi

if [ -n "$FIX" ]; then
  echo "=== rodando sync automaticamente (--fix) ==="
  bash "${CEREBRO_ROOT}/ops/skills-sync/sync-skills.sh"
  exit $?
else
  echo "Para corrigir, rode:"
  echo "  bash ${CEREBRO_ROOT}/ops/skills-sync/sync-skills.sh"
  echo "  (ou: bash ${CEREBRO_ROOT}/ops/skills-sync/verify-sync.sh --fix)"
  exit 1
fi
