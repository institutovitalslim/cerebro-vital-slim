#!/usr/bin/env python3
"""Marketing OS Monitor — read-only audit for João/IVS marketing operation."""
import argparse, json, os, re, time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path('/root/cerebro-vital-slim')
MARKETING = ROOT/'cerebro/areas/marketing'
DELIVERABLES = Path('/root/deliverables')
MEDIA_OUT = Path('/root/.openclaw/media/outbound')
JOAO_SESS = Path('/root/.openclaw/agents/agente-reels-intel/sessions')
BACKLOG = ROOT/'cerebro/empresa/projetos/PAINEL-UNICO-BACKLOG-STATUS-IVS-V1.md'
RECURRENT = ROOT/'cerebro/operacional/INDEX-PEDIDOS-RECORRENTES.md'
JOAO_RULES = MARKETING/'agentes/agente-reels-intel/JOAO-REGRAS-DE-OPERACAO.md'

MARKETING_CODES = ['A4','A5','A6','A7','A16','A17']
RECENT_DAYS = 7


def stat_file(p: Path) -> Dict[str, Any] | None:
    try:
        s=p.stat()
        return {'path': str(p), 'name': p.name, 'size': s.st_size, 'mtime': int(s.st_mtime), 'age_hours': round((time.time()-s.st_mtime)/3600,1)}
    except Exception:
        return None


def read_text(p: Path, max_chars=250000) -> str:
    try: return p.read_text(encoding='utf-8', errors='replace')[:max_chars]
    except Exception: return ''


def extract_backlog() -> List[Dict[str, Any]]:
    text=read_text(BACKLOG)
    items=[]
    for m in re.finditer(r'###\s+(A\d+)\.\s+([^\n]+)(.*?)(?=\n###\s+[AF]\d+\.|\n##\s+|\Z)', text, re.S):
        code,title,body=m.group(1),m.group(2).strip(),m.group(3)
        if code in MARKETING_CODES or re.search(r'Marketing|Reels|João|HTML|ferramenta|Vídeo|Instagram|Conteúdo', body, re.I):
            status=re.search(r'\*\*Status:\*\*\s*([^\n]+)', body)
            nexts=re.search(r'\*\*Próximo passo:\*\*\s*([^\n]+)', body)
            source=re.search(r'\*\*Fonte de verdade:\*\*\s*([^\n]+)', body)
            items.append({'code':code,'title':title,'status':status.group(1).strip() if status else None,'next_step':nexts.group(1).strip() if nexts else None,'source':source.group(1).strip() if source else None})
    return items


def is_marketing_deliverable(p: Path) -> bool:
    n=p.name.lower()
    positive=['marketing','joao','reels','blueprint-sistema-marketing','cockpit-marketing','soul-super-joao','arquitetura-funcional-super-joao','matriz-super-joao','notion-bunkers-joao','rotina-manutencao-intertopicos','painel-unico-backlog','abertos-reais-vs-fechados-reais']
    negative=['apresentacao-','dados-','clara','preconsulta','relatorio_sugestao_compra','logo-','dra-daniely']
    if any(x in n for x in positive): return True
    if any(x in n for x in negative): return False
    return False

def recent_files(base: Path, patterns: List[str], limit=80, marketing_only=False) -> List[Dict[str, Any]]:
    out=[]
    if not base.exists(): return out
    cutoff=time.time()-RECENT_DAYS*86400
    for pat in patterns:
        for p in base.glob(pat):
            if p.is_file():
                if marketing_only and not is_marketing_deliverable(p): continue
                st=stat_file(p)
                if st and st['mtime']>=cutoff: out.append(st)
    out.sort(key=lambda x:x['mtime'], reverse=True)
    return out[:limit]


def marketing_docs() -> List[Dict[str,Any]]:
    if not MARKETING.exists(): return []
    cutoff=time.time()-RECENT_DAYS*86400
    out=[]
    for p in MARKETING.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.md','.html','.json']:
            st=stat_file(p)
            if st and st['mtime']>=cutoff: out.append(st)
    out.sort(key=lambda x:x['mtime'], reverse=True)
    return out[:120]


def joao_sessions() -> List[Dict[str,Any]]:
    if not JOAO_SESS.exists(): return []
    out=[]
    for p in JOAO_SESS.glob('*.jsonl'):
        if '.trajectory' in p.name: continue
        st=stat_file(p)
        if st: out.append(st)
    out.sort(key=lambda x:x['mtime'], reverse=True)
    return out[:40]


def session_risks(files: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    risks=[]
    for f in files[:12]:
        p=Path(f['path'])
        txt=read_text(p, 180000)
        if 'Previous run is still shutting down' in txt:
            risks.append({'code':'joao_session_shutdown_lock_seen','file':p.name,'severity':'MEDIUM'})
        if 'LocalMediaAccessError' in txt or 'not under an allowed directory' in txt:
            risks.append({'code':'joao_media_delivery_error_seen','file':p.name,'severity':'MEDIUM'})
        if re.search(r'falh|erro|failed|timeout|EADDRINUSE', txt, re.I):
            risks.append({'code':'joao_recent_error_terms_seen','file':p.name,'severity':'LOW'})
    return risks[:30]


def rule_health() -> Dict[str,Any]:
    checks={}
    txt=read_text(JOAO_RULES)
    full_marketing = txt + '\n' + read_text(MARKETING/'skills/validacao-reels-tribe-v2/SKILL.md') + '\n' + read_text(MARKETING/'regra-canonica-nomenclatura-instituto-vital-slim-2026-05-07.md')
    direct = {
        'preserva_estrutura_validada': ('estrutura validada manda', txt),
        'html_anexo': ('arquivo `.html` direto', txt),
        'subagentes_sob_demanda': ('subagentes sob demanda', txt),
        'design_impeccable': ('design-impeccable', txt),
        'tribe_v2_canonico': ('tribe v2', full_marketing),
        'nome_publico_instituto_canonico': ('instituto vital slim', full_marketing)
    }
    for key, pair in direct.items():
        term, corpus = pair
        checks[key] = term.lower() in corpus.lower()
    return {'rules_file_exists': JOAO_RULES.exists(), 'checks': checks, 'missing': [k for k,v in checks.items() if not v]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json', action='store_true'); args=ap.parse_args()
    deliverables=recent_files(DELIVERABLES, ['*.html','*.md','*.json','*.pdf','*.zip'], 120, marketing_only=True)
    outbound=recent_files(MEDIA_OUT, ['*.html','*.md','*.pdf','*.jpg','*.png','*.mp4','*.zip'], 120, marketing_only=True)
    mkdocs=marketing_docs(); backlog=extract_backlog(); sessions=joao_sessions(); risks=session_risks(sessions); rh=rule_health()
    html_deliv=[f for f in deliverables if f['name'].endswith('.html')]
    html_out=[f for f in outbound if f['name'].endswith('.html')]
    delivered_names={f['name'] for f in outbound}
    html_not_out=[f for f in html_deliv if f['name'] not in delivered_names]
    findings=[]
    if not rh['rules_file_exists'] or rh['missing']: findings.append({'severity':'HIGH','code':'joao_rules_missing_terms','detail':rh})
    if html_not_out: findings.append({'severity':'MEDIUM','code':'html_deliverables_not_in_outbound','count':len(html_not_out)})
    medium_risks=[x for x in risks if str(x.get('severity')).upper() in ['HIGH','MEDIUM']]
    if medium_risks: findings.append({'severity':'MEDIUM','code':'joao_session_risk_markers','count':len(medium_risks)})
    elif risks: findings.append({'severity':'LOW','code':'joao_session_low_signal_terms','count':len(risks)})
    if len(backlog)>=4: findings.append({'severity':'LOW','code':'marketing_backlog_active','count':len(backlog)})
    report={
        'ok': True, 'generated_at': int(time.time()), 'mode':'read_only_no_external_posting',
        'totals': {'marketing_backlog_items':len(backlog),'recent_deliverables':len(deliverables),'recent_html_deliverables':len(html_deliv),'recent_outbound_files':len(outbound),'recent_marketing_docs':len(mkdocs),'joao_session_files':len(sessions)},
        'rule_health': rh,
        'marketing_backlog': backlog,
        'recent_html_deliverables': html_deliv[:30],
        'html_deliverables_not_in_outbound': html_not_out[:30],
        'recent_outbound': outbound[:30],
        'recent_marketing_docs': mkdocs[:40],
        'joao_sessions': sessions[:20],
        'session_risks': risks,
        'findings': findings,
        'next_actions': ['Cobrar João por backlog A16/A17 nas próximas entregas.', 'Manter HTML importante como anexo direto no Telegram.', 'Se houver risco de sessão travada, resetar apenas mapeamento/sessão alvo preservando histórico.']
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
