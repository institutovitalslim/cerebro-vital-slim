#!/usr/bin/env python3
"""Sincroniza Bunker (SQLite) -> content-engine viral_scripts (Postgres), COM dados ricos:
referencias (links vídeo), ideia_prompt, plataforma e fonte_raw (conteúdo Notion completo).
Uso: python3 sync_bunker_to_viral.py | docker exec -i content-engine-postgres psql -U content_engine -d content_engine
"""
import json, sqlite3, sys
DB = "/root/cerebro-vital-slim/cerebro/areas/marketing/projetos/bunker-roteiros-ivs/bunker.db"
con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
def has(col):
    return col in [r[1] for r in con.execute("PRAGMA table_info(roteiros)")]
rows = con.execute("select * from roteiros").fetchall()
def e(s): return "'" + str(s if s is not None else "").replace("'", "''") + "'"
print("begin;")
print("delete from viral_scripts where tenant_id is null;")
for r in rows:
    try: uso = json.loads(r["uso_recomendado_json"] or "[]")
    except Exception: uso = []
    refs = r["referencias_json"] if has("referencias_json") and r["referencias_json"] else "[]"
    ideia = r["ideia_prompt"] if has("ideia_prompt") else None
    plat = r["plataforma"] if has("plataforma") else None
    fraw = r["fonte_raw"] if has("fonte_raw") else None
    print("insert into viral_scripts (tenant_id,codigo,origem,objetivo,classe_ivs,mecanismo,hook_base,"
          "tese_central,objecao_principal,leitura_ivs,adaptacao_ivs,uso_recomendado,status,"
          "referencias,ideia_prompt,plataforma,fonte_raw) values "
          f"(null,{e(r['codigo'])},{e(r['origem'])},{e(r['objetivo'])},{e(r['classe_ivs'])},{e(r['mecanismo'])},"
          f"{e(r['hook_base'])},{e(r['tese_central'])},{e(r['objecao_principal'])},{e(r['leitura_ivs'])},"
          f"{e(r['adaptacao_ivs'])},{e(json.dumps(uso,ensure_ascii=False))}::jsonb,{e(r['status'] or 'adaptado')},"
          f"{e(refs)}::jsonb,{e(ideia)},{e(plat)},{e(fraw)});")
print("commit;")
print(f"-- {len(rows)} roteiros (com refs/prompt/fonte)", file=sys.stderr)
