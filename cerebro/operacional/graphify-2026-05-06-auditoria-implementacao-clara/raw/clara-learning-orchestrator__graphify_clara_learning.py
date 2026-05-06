#!/usr/bin/env python3
import json, shutil, re
from pathlib import Path
from datetime import datetime
import networkx as nx
from graphify.cluster import cluster, score_all
from graphify.export import to_json, to_html
from graphify.report import generate

REPORTS=Path('/root/.openclaw/reports/clara-learning')
ROOT=Path('/root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify')

def nid(s):
    return re.sub(r'[^a-zA-Z0-9]+','_',str(s)).strip('_').lower() or 'node'

def add_node(G, key, label, typ, **attrs):
    G.add_node(key, id=key, label=label, type=typ, **attrs)

def add_edge(G, a, b, typ, **attrs):
    if a and b and a in G and b in G:
        G.add_edge(a,b,type=typ, relationship=typ, confidence=attrs.pop('confidence','EXTRACTED'), **attrs)

def main():
    day=datetime.now().strftime('%Y-%m-%d')
    out=ROOT/day
    raw=out/'raw'; gout=out/'graphify-out'
    raw.mkdir(parents=True, exist_ok=True); gout.mkdir(parents=True, exist_ok=True)
    files=sorted(REPORTS.glob('latest-*.json'))
    copied=[]
    for f in files:
        dest=raw/f.name
        shutil.copy2(f,dest); copied.append(dest)
    G=nx.Graph()
    add_node(G,'clara','Clara WhatsApp','agent')
    add_node(G,'conselho_growth','Conselho Growth','council')
    add_node(G,'agendamento_premium','Agendamento premium de pacientes/leads','capability')
    add_edge(G,'clara','agendamento_premium','must_master')
    add_edge(G,'conselho_growth','clara','sabatina')
    for f in copied:
        try: data=json.loads(f.read_text())
        except Exception: continue
        slot=data.get('slot') or f.stem
        sk='slot_'+nid(slot)
        add_node(G,sk,slot,'learning_slot',source_file=str(f))
        add_edge(G,'clara',sk,'learns_from')
        fonte=data.get('fonte')
        if fonte:
            fk='fonte_'+nid(fonte)
            add_node(G,fk,fonte,'source')
            add_edge(G,sk,fk,'uses_source')
        busca=data.get('buscar') or data.get('query') or ''
        if busca:
            bk='tema_'+nid(busca[:80])
            add_node(G,bk,busca[:160],'topic')
            add_edge(G,sk,bk,'extracts_topic')
        entrega=data.get('entrega') or ''
        if entrega:
            ek='entrega_'+nid(entrega[:80])
            add_node(G,ek,entrega[:160],'deliverable')
            add_edge(G,sk,ek,'produces')
        coleta=data.get('coleta') or {}
        stdout=coleta.get('stdout','') if isinstance(coleta,dict) else ''
        try:
            parsed=json.loads(stdout) if stdout.strip().startswith('{') else {}
        except Exception: parsed={}
        for item in (parsed.get('items') or parsed.get('sample') or [])[:8]:
            title=(item.get('title') or item.get('text') or item.get('screen_name') or '')[:180]
            if not title: continue
            ik='item_'+nid(title[:80])
            add_node(G,ik,title,'external_learning_item',source_file=str(f), url=item.get('url',''), profile=item.get('screen_name') or item.get('channel',''))
            add_edge(G,sk,ik,'observed')
            txt=(item.get('description_full') or item.get('description') or item.get('text') or '')[:500]
            if txt:
                ck='conceito_'+nid(txt[:70])
                add_node(G,ck,txt[:160],'concept')
                add_edge(G,ik,ck,'contains_concept')
    communities=cluster(G)
    scores=score_all(G, communities)
    labels={cid: (' / '.join(G.nodes[n].get('label',n) for n in nodes[:3]))[:80] for cid,nodes in communities.items()}
    to_json(G, communities, str(gout/'graph.json'), force=True)
    to_html(G, communities, str(gout/'graph.html'), labels)
    report=generate(G, communities, scores, labels, [], [], {'total_files':len(copied),'files':{'docs':[str(x) for x in copied]},'total_words':0}, {'input_tokens':0,'output_tokens':0}, str(out), suggested_questions=[])
    (gout/'GRAPH_REPORT.md').write_text(report)
    (out/'README.md').write_text(f"""# Clara Learning Graphify — {day}\n\nCorpus diário de aprendizado da Clara processado via Graphify/RC-25.\n\n- Raw: `{raw}`\n- Graph JSON: `{gout/'graph.json'}`\n- Graph HTML: `{gout/'graph.html'}`\n- Report: `{gout/'GRAPH_REPORT.md'}`\n\nArquivos processados: {len(copied)}.\n""")
    latest=ROOT/'latest'
    if latest.exists() or latest.is_symlink(): latest.unlink()
    latest.symlink_to(out, target_is_directory=True)
    print(json.dumps({'ok':True,'day':day,'dir':str(out),'files':len(copied),'nodes':G.number_of_nodes(),'edges':G.number_of_edges(),'graph':str(gout/'graph.json')}, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
