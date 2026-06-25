#!/usr/bin/env python3
"""Sincroniza o cérebro IVS canônico para o sidecar GBrain.

Regras:
- Não escreve no cérebro canônico, exceto o relatório operacional em cerebro/gbrain/sync/latest-health.md.
- Atualiza apenas a cópia de importação do sidecar e roda import/extract/embed/doctor/stats.
- Serve para cron diário e validação pós-RC-25.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/root/cerebro-vital-slim')
GBRAIN_REPO = ROOT / 'tmp/repo-reverse/gbrain'
IMPORT = Path('/root/.local/share/ivs-gbrain/import/ivs-brain')
REPORT_DIR = Path('/root/.local/share/ivs-gbrain/reports')
CANONICAL_LATEST = ROOT / 'cerebro/gbrain/sync/latest-health.md'
LOCK = Path('/root/.local/share/ivs-gbrain/gbrain_ivs_sync.lock')
CONTEXT_COMPRESSOR = ROOT / 'tools/ivs-context-compressor/ivs_context_compressor.py'

ENV = os.environ.copy()
ENV['GBRAIN_HOME'] = '/root/.local/share/ivs-gbrain/home'
ENV['OPENCLAW_WORKSPACE'] = '/root/.local/share/ivs-gbrain/agent-workspace'
ENV['PATH'] = '/usr/local/bin:/root/.bun/bin:' + ENV.get('PATH', '')

# Carrega a chave do provider de embedding (OpenAI) a partir do arquivo seguro,
# de forma transitoria -- usada so para chamar a API de embedding durante o sync.
# Nunca e gravada no GBrain (config/brain), preservando a governanca de segredos.
def _load_secret_env(*paths):
    for p in paths:
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    if line.startswith('export '):
                        line = line[len('export '):]
                    k, _, v = line.partition('=')
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and v and not ENV.get(k):
                        ENV[k] = v
        except FileNotFoundError:
            continue


_load_secret_env('/root/.openclaw/secure/openai.env', '/root/.openclaw/.env.runtime')

EXCLUDE_DIRS = {
    '.git', 'node_modules', '.venv', '__pycache__', 'secure', 'tmp', 'backups',
    'backup', '.mypy_cache', '.pytest_cache', 'dist', 'build'
}
INCLUDE_SUFFIXES = {'.md', '.json', '.jsonl', '.yaml', '.yml', '.txt'}


def should_copy(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.name.startswith('.') and path.name not in {'.graphify_detect.json'}:
        return False
    return path.suffix.lower() in INCLUDE_SUFFIXES


def acquire_lock() -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            age = time.time() - LOCK.stat().st_mtime
        except Exception:
            age = 0
        if age < 6 * 3600:
            raise SystemExit(f'gbrain_sync_already_running lock={LOCK} age_seconds={int(age)}')
        LOCK.unlink(missing_ok=True)
    LOCK.write_text(str(os.getpid()), encoding='utf-8')


def release_lock() -> None:
    try:
        if LOCK.exists() and LOCK.read_text(encoding='utf-8').strip() == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


def mirror(clean: bool = True) -> int:
    if clean and IMPORT.exists():
        shutil.rmtree(IMPORT)
    IMPORT.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in ROOT.rglob('*'):
        if not src.is_file() or not should_copy(src):
            continue
        dst = IMPORT / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    return copied


def run(args: list[str], timeout: int = 900) -> dict:
    started = time.time()
    proc = subprocess.run(
        args,
        cwd=str(GBRAIN_REPO),
        env=ENV,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return {
        'cmd': args,
        'returncode': proc.returncode,
        'duration_seconds': round(time.time() - started, 2),
        'stdout': proc.stdout[-12000:],
        'stderr': proc.stderr[-12000:],
    }


def parse_stats(text: str) -> dict:
    out = {}
    for key in ['Pages', 'Chunks', 'Embedded', 'Links', 'Tags', 'Timeline']:
        m = re.search(rf'^{key}:\s+(\d+)', text, re.M)
        if m:
            out[key.lower()] = int(m.group(1))
    return out


def parse_health(text: str) -> dict:
    out = {}
    m = re.search(r'Overall health score:\s*(\d+)/100', text)
    if m:
        out['overall_health'] = int(m.group(1))
    m = re.search(r'Weighted brain score: Brain score\s*(\d+)/100', text)
    if m:
        out['brain_score'] = int(m.group(1))
    # Captura apenas linhas canônicas do doctor, evitando linhas-resumo com setas que podem conter múltiplos warnings no mesmo bloco.
    warnings = re.findall(r'^\s*\[WARN\]\s+([a-zA-Z0-9_\-]+)\s*[:→]\s*(.*)$', text, re.M)
    seen = set()
    parsed_warnings = []
    for a, b in warnings:
        key = (a.strip(), b.strip())
        if key in seen:
            continue
        seen.add(key)
        parsed_warnings.append({'check': a.strip(), 'message': b.strip()})
    out['warnings'] = parsed_warnings
    stale_ok = 'embed_staleness: No stale chunks' in text
    out['embed_staleness_ok'] = stale_ok
    return out



def compress_context(path: Path, kind: str = 'gbrain-results') -> dict:
    if not CONTEXT_COMPRESSOR.exists():
        return {'ok': False, 'error': f'compressor not found: {CONTEXT_COMPRESSOR}'}
    try:
        raw = subprocess.check_output(
            [sys.executable, str(CONTEXT_COMPRESSOR), '--input', str(path), '--type', kind, '--format', 'json'],
            text=True,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
        payload = json.loads(raw)
        return {
            'ok': bool(payload.get('ok')),
            'sha256': payload.get('sha256'),
            'outputs': payload.get('outputs'),
            'evidence': payload.get('evidence'),
            'critical_line_count': (payload.get('summary') or {}).get('critical_line_count'),
            'redactions': (payload.get('summary') or {}).get('redactions'),
        }
    except Exception as exc:
        return {'ok': False, 'error': str(exc)[:500]}

def build_markdown(payload: dict) -> str:
    stats = payload.get('stats_parsed', {})
    health = payload.get('health_parsed', {})
    lines = [
        '# GBrain IVS — Health Report',
        '',
        f"Gerado em: `{payload['generated_at']}`",
        f"Modo: `{payload['mode']}`",
        f"Arquivos espelhados: **{payload.get('mirrored_files', 0)}**",
        '',
        '## Estatísticas',
        f"- Pages: **{stats.get('pages', 'n/d')}**",
        f"- Chunks: **{stats.get('chunks', 'n/d')}**",
        f"- Embedded: **{stats.get('embedded', 'n/d')}**",
        f"- Links: **{stats.get('links', 'n/d')}**",
        f"- Tags: **{stats.get('tags', 'n/d')}**",
        f"- Timeline: **{stats.get('timeline', 'n/d')}**",
        '',
        '## Saúde',
        f"- Overall health: **{health.get('overall_health', 'n/d')}/100**",
        f"- Brain score: **{health.get('brain_score', 'n/d')}/100**",
        f"- Embed staleness: **{'OK' if health.get('embed_staleness_ok') else 'verificar'}**",
        '',
        '## Warnings',
    ]
    warnings = health.get('warnings') or []
    if warnings:
        for w in warnings:
            lines.append(f"- `{w['check']}` — {w['message']}")
    else:
        lines.append('- Nenhum warning.')
    lines += ['', '## Comandos']
    for step in payload.get('commands', []):
        status = 'OK' if step.get('returncode') == 0 else 'FALHA'
        lines.append(f"- **{status}** `{ ' '.join(step.get('cmd', [])) }` ({step.get('duration_seconds')}s)")
    lines += [
        '',
        '## Regra operacional',
        '- Fonte de verdade continua sendo o markdown do `cerebro-vital-slim`.',
        '- GBrain é retrieval/grafo/embeddings/resolver.',
        '- Escrita persistente continua via Graphify/RC-25.',
    ]
    return '\n'.join(lines).strip() + '\n'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--doctor-only', action='store_true', help='não espelha/importa; roda só doctor/stats')
    ap.add_argument('--no-clean', action='store_true', help='não limpa a pasta de importação antes de espelhar')
    ap.add_argument('--mode', default='manual', choices=['manual', 'cron', 'post-rc25', 'doctor-only'])
    ap.add_argument('--compress-context', action='store_true', help='Run IVS Context Compressor on the generated health report (read-only, optional).')
    args = ap.parse_args()

    if not GBRAIN_REPO.exists():
        raise SystemExit(f'gbrain_repo_missing: {GBRAIN_REPO}')

    acquire_lock()
    try:
        generated_at = datetime.now(timezone.utc).isoformat()
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        mirrored = 0
        commands = []
        mode = 'doctor-only' if args.doctor_only else args.mode

        if not args.doctor_only:
            mirrored = mirror(clean=not args.no_clean)
            for cmd in [
                ['bun', 'run', 'src/cli.ts', 'import', str(IMPORT), '--no-embed'],
                ['bun', 'run', 'src/cli.ts', 'extract', '--stale', '--catch-up'],
                ['bun', 'run', 'src/cli.ts', 'embed', '--stale'],
            ]:
                res = run(cmd)
                commands.append(res)
                if res['returncode'] != 0:
                    break

        if all(c['returncode'] == 0 for c in commands):
            commands.append(run(['bun', 'run', 'src/cli.ts', 'doctor']))
            commands.append(run(['bun', 'run', 'src/cli.ts', 'stats']))

        doctor_text = next((c['stdout'] + '\n' + c['stderr'] for c in commands if c['cmd'][-1] == 'doctor'), '')
        stats_text = next((c['stdout'] + '\n' + c['stderr'] for c in commands if c['cmd'][-1] == 'stats'), '')
        payload = {
            'generated_at': generated_at,
            'mode': mode,
            'mirrored_files': mirrored,
            'commands': commands,
            'health_parsed': parse_health(doctor_text),
            'stats_parsed': parse_stats(stats_text),
            'ok': all(c['returncode'] == 0 for c in commands),
        }
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        json_path = REPORT_DIR / f'gbrain-ivs-health-{stamp}.json'
        md_path = REPORT_DIR / f'gbrain-ivs-health-{stamp}.md'
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        md = build_markdown(payload)
        md_path.write_text(md, encoding='utf-8')
        compressed_context = compress_context(md_path) if args.compress_context else None
        if compressed_context is not None:
            payload['compressed_context'] = compressed_context
            json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        CANONICAL_LATEST.parent.mkdir(parents=True, exist_ok=True)
        CANONICAL_LATEST.write_text(md, encoding='utf-8')
        (REPORT_DIR / 'latest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        (REPORT_DIR / 'latest.md').write_text(md, encoding='utf-8')
        print(json.dumps({
            'ok': payload['ok'],
            'mode': mode,
            'mirrored_files': mirrored,
            'health': payload['health_parsed'],
            'stats': payload['stats_parsed'],
            'report': str(md_path),
            'canonical_latest': str(CANONICAL_LATEST),
            **({'compressed_context': compressed_context} if compressed_context is not None else {}),
        }, ensure_ascii=False, indent=2))
        return 0 if payload['ok'] else 2
    finally:
        release_lock()


if __name__ == '__main__':
    raise SystemExit(main())
