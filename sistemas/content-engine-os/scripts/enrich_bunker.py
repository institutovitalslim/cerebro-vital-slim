#!/usr/bin/env python3
"""Enriquece bunker.roteiros com referencias_json/ideia_prompt/plataforma/fonte_raw a partir do bruto."""
import sqlite3, re, json
DB="/root/cerebro-vital-slim/cerebro/areas/marketing/projetos/bunker-roteiros-ivs/bunker.db"
con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
for col in ("referencias_json TEXT","ideia_prompt TEXT","plataforma TEXT","fonte_raw TEXT"):
    try: con.execute("alter table roteiros add column "+col)
    except Exception: pass
con.commit()
URLRE=re.compile(r'https?://[^\s)>\]"]+')
def dom(u): return ('drive' if 'drive.google' in u else 'tiktok' if 'tiktok' in u else 'instagram' if 'instagram' in u else 'youtube' if ('youtube' in u or 'youtu.be' in u) else 'outro')
def extract(raw):
    raw=raw or ""
    refs=[{"url":u,"tipo":dom(u)} for u in sorted(set(URLRE.findall(raw)))]
    m=re.search(r'(?:ideia de prompt|prompt[^\n]*)\n+(.{20,800}?)(?:\n[A-ZÁ-Ú][^\n]{0,40}\n|\Z)', raw, re.I|re.S)
    prompt=m.group(1).strip() if m else ""
    m=re.search(r'Plataforma\s*\n+(.+?)(?:\n[A-ZÁ-Ú])', raw, re.S)
    plat=m.group(1).strip()[:140] if m else ""
    return refs, prompt, plat
rows=con.execute("select r.id, b.conteudo_raw as raw from roteiros r left join roteiros_brutos b on b.id=r.bruto_id").fetchall()
for r in rows:
    refs,prompt,plat=extract(r["raw"])
    con.execute("update roteiros set referencias_json=?, ideia_prompt=?, plataforma=?, fonte_raw=? where id=?",
        (json.dumps(refs,ensure_ascii=False), prompt or None, plat or None, r["raw"], r["id"]))
con.commit()
print(f"enriquecidos {len(rows)} | com refs {sum(1 for r in rows if extract(r['raw'])[0])}")
