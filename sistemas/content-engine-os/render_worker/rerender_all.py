#!/usr/bin/env python3
"""Re-renderiza TODAS as peças (creatives com asset_url) EM LUGAR, aplicando o design atual
(ex.: gradiente preto). Preserva status/asset_url (nomes determinísticos). Carrossel reusa cache Higgsfield."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_daemon as rd
rows = json.loads(rd.psql("select coalesce(json_agg(t),'[]') from (select id::text, format, network, script from creatives where asset_url is not null) t;"))
ok=err=0
for c in rows:
    outdir = os.path.join(rd.RENDERS, c["id"])
    if os.path.isdir(outdir):
        for f in os.listdir(outdir):
            try: os.remove(os.path.join(outdir, f))
            except OSError: pass
    try:
        slides = rd.build_slides(c)
        paths=[]
        for i, sp in enumerate(slides, 1):
            paths += rd.gen_foto.render(sp, outdir, "slide_%02d" % i)
        ok+=1
    except Exception as e:
        print("[erro]", c["id"], str(e)[:80], flush=True); err+=1
print(f"re-render: {ok} ok, {err} erros de {len(rows)} peças", flush=True)
