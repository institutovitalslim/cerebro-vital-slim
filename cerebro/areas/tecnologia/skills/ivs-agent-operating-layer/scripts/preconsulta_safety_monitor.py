#!/usr/bin/env python3
"""Pré-consulta Safety Monitor — read-only audit for IVS pre-consultation app."""
import argparse, json, time, re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

DATA_DIR = Path('/root/ivs-preconsulta-data')
PACIENTES_DIR = Path('/root/cerebro-vital-slim/cerebro/empresa/pacientes')
FALLBACK_QUEUE = Path('/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/state/fallback_telegram_queue.jsonl')
APP_URL = 'http://127.0.0.1:3001'

REQUIRED_ID = ['nome', 'telefone']
REQUIRED_CORE = ['dataNascimento','altura','pesoAtual','pesoIdeal','spin_p_principalIncomodo','tresObjetivos']


def load_json_file(path: Path) -> Tuple[Dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else None, 'invalid_root'
    except Exception as exc:
        return None, str(exc)


def slug(v: str) -> str:
    import unicodedata
    s = unicodedata.normalize('NFD', v or '').encode('ascii','ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+','-',s).strip('-').lower()[:40]
    return s or 'sem-nome'


def parse_ts(v: Any, fallback: float) -> float:
    if isinstance(v, str) and v:
        try:
            from datetime import datetime
            return datetime.fromisoformat(v.replace('Z','+00:00')).timestamp()
        except Exception:
            pass
    return fallback


def http_probe(url: str, timeout=3) -> Dict[str, Any]:
    try:
        req = Request(url, method='GET')
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read(500).decode('utf-8', errors='replace')
            return {'ok': 200 <= resp.status < 500, 'status': resp.status, 'preview': body[:160]}
    except HTTPError as exc:
        return {'ok': exc.code < 500, 'status': exc.code, 'preview': exc.read(500).decode('utf-8', errors='replace')[:160]}
    except URLError as exc:
        return {'ok': False, 'error': str(exc)}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def fallback_queue_info() -> Dict[str, Any]:
    if not FALLBACK_QUEUE.exists():
        return {'exists': False, 'count': 0, 'latest': None}
    try:
        lines = [l for l in FALLBACK_QUEUE.read_text(encoding='utf-8', errors='replace').splitlines() if l.strip()]
        latest = None
        if lines:
            try: latest = json.loads(lines[-1])
            except Exception: latest = {'raw': lines[-1][:300]}
        return {'exists': True, 'count': len(lines), 'latest': latest}
    except Exception as exc:
        return {'exists': True, 'count': None, 'error': str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--no-http', action='store_true')
    args = ap.parse_args()
    now = time.time()
    files = sorted([p for p in DATA_DIR.glob('*.json') if not p.name.startswith('.') and not p.name.endswith('_state.json') and 'audit_state' not in p.name]) if DATA_DIR.exists() else []
    records=[]; invalid=[]; drafts=[]; submissions=[]; stale_drafts=[]; incomplete=[]; missing_md=[]; duplicate_keys={}
    for path in files:
        stat = path.stat()
        data, err = load_json_file(path)
        if data is None:
            invalid.append({'file': path.name, 'error': err}); continue
        is_draft = data.get('draft') is True or path.name.startswith('draft-')
        t = parse_ts(data.get('updatedAt') or data.get('submittedAt'), stat.st_mtime)
        name = str(data.get('nome') or 'Sem nome')
        phone = re.sub(r'\D+','', str(data.get('telefone') or ''))
        rec = {'file': path.name, 'nome': name, 'phone': phone, 'draft': is_draft, 'ts': int(t), 'updated_or_submitted': data.get('updatedAt') or data.get('submittedAt')}
        records.append(rec)
        key = phone or slug(name)+'|'+str(data.get('email') or '')
        duplicate_keys.setdefault(key, []).append(rec)
        missing = [k for k in REQUIRED_ID if not str(data.get(k) or '').strip()]
        if not is_draft:
            submissions.append(rec)
            missing += [k for k in REQUIRED_CORE if not str(data.get(k) or '').strip()]
            md = PACIENTES_DIR / f"preconsulta-{slug(name)}-{time.strftime('%Y-%m-%d', time.gmtime(t))}.md"
            if not md.exists():
                # handle route uses current date at submit, so also try any date for slug
                any_md = list(PACIENTES_DIR.glob(f"preconsulta-{slug(name)}-*.md"))
                if not any_md:
                    missing_md.append({**rec, 'expected': md.name})
        else:
            drafts.append(rec)
            age_h = (now - t) / 3600
            if age_h >= 2:
                stale_drafts.append({**rec, 'age_hours': round(age_h, 1)})
        if missing:
            incomplete.append({**rec, 'missing': missing})
    duplicates = []
    for key, vals in duplicate_keys.items():
        if key and len(vals) > 1:
            duplicates.append({'key': key, 'count': len(vals), 'items': vals[:10]})
    findings=[]
    if invalid: findings.append({'severity':'HIGH','code':'invalid_json_files','count':len(invalid)})
    if missing_md: findings.append({'severity':'HIGH','code':'submission_without_markdown','count':len(missing_md)})
    if stale_drafts: findings.append({'severity':'MEDIUM','code':'stale_drafts_over_2h','count':len(stale_drafts)})
    if incomplete: findings.append({'severity':'MEDIUM','code':'incomplete_records','count':len(incomplete)})
    fq = fallback_queue_info()
    if fq.get('count'): findings.append({'severity':'MEDIUM','code':'telegram_fallback_queue_not_empty','count':fq.get('count')})
    app = None if args.no_http else http_probe(APP_URL)
    if app and not app.get('ok'): findings.append({'severity':'HIGH','code':'preconsulta_app_unavailable','detail':app})
    report={
        'ok': True,
        'generated_at': int(now),
        'mode': 'read_only_no_patient_contact',
        'app_probe': app,
        'totals': {'json_files':len(files),'valid_records':len(records),'submissions':len(submissions),'drafts':len(drafts),'invalid':len(invalid)},
        'latest_records': sorted(records, key=lambda x:x['ts'], reverse=True)[:20],
        'stale_drafts_count': len(stale_drafts), 'stale_drafts_sample': sorted(stale_drafts, key=lambda x:x['ts'])[:20],
        'incomplete_count': len(incomplete), 'incomplete_sample': incomplete[:30],
        'missing_markdown_count': len(missing_md), 'missing_markdown_sample': missing_md[:30],
        'duplicates_count': len(duplicates), 'duplicates_sample': duplicates[:20],
        'fallback_queue': fq,
        'findings': findings,
        'next_actions': ['Não pedir paciente para preencher novamente sem validação humana.', 'Investigar missing_markdown/invalid_json antes de prometer dados.', 'Drafts antigos devem ser tratados como oportunidade de recuperação interna, não contato automático.']
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
