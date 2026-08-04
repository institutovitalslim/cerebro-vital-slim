#!/usr/bin/env python3
"""Importa os roteiros virais do nucleo do bunker IVS -> SQL de seed (acervo global).
Le 03-bunker-ivs/nucleo-inicial-bunker-ivs.md (fonte unica). Idempotente (delete global + insert)."""
import re, sys, json

MD = sys.argv[1] if len(sys.argv) > 1 else \
    "/root/cerebro-vital-slim/cerebro/areas/marketing/projetos/bunker-roteiros-ivs/03-bunker-ivs/nucleo-inicial-bunker-ivs.md"

def esc(s): return (s or "").replace("'", "''").strip()

raw = open(MD, encoding="utf-8").read()
blocks = re.split(r"\n##\s+IVS-BKR-", raw)
items = []
for b in blocks[1:]:
    codigo = "IVS-BKR-" + b.split("\n", 1)[0].strip()
    def field(label):
        m = re.search(rf"\*\*{label}:\*\*\s*(.+)", b)
        return m.group(1).strip() if m else ""
    # Adaptação IVS costuma vir em sub-bullet na linha seguinte
    adap = field("Adaptação IVS")
    if not adap:
        m = re.search(r"\*\*Adaptação IVS:\*\*\s*\n\s*-\s*\"?(.+?)\"?\s*\n", b, re.S)
        adap = m.group(1).strip().strip('"') if m else ""
    uso = field("Uso recomendado")
    uso_list = [u.strip() for u in re.split(r"[,/]", uso) if u.strip()] if uso else []
    items.append({
        "codigo": codigo, "origem": field("Origem"), "objetivo": field("Objetivo"),
        "classe_ivs": field("Classe IVS"), "mecanismo": field("Mecanismo"),
        "hook_base": field("Hook-base") or field("Hook base"),
        "tese_central": field("Tese central"), "objecao_principal": field("Objeção principal"),
        "leitura_ivs": field("Leitura IVS"), "adaptacao_ivs": adap,
        "uso_recomendado": uso_list, "status": field("Status") or "adaptado",
    })

print("begin;")
print("delete from viral_scripts where tenant_id is null;")
for it in items:
    print(
        "insert into viral_scripts (tenant_id,codigo,origem,objetivo,classe_ivs,mecanismo,hook_base,"
        "tese_central,objecao_principal,leitura_ivs,adaptacao_ivs,uso_recomendado,status) values "
        f"(null,'{esc(it['codigo'])}','{esc(it['origem'])}','{esc(it['objetivo'])}','{esc(it['classe_ivs'])}',"
        f"'{esc(it['mecanismo'])}','{esc(it['hook_base'])}','{esc(it['tese_central'])}',"
        f"'{esc(it['objecao_principal'])}','{esc(it['leitura_ivs'])}','{esc(it['adaptacao_ivs'])}',"
        f"'{esc(json.dumps(it['uso_recomendado'], ensure_ascii=False))}'::jsonb,'{esc(it['status'])}');"
    )
print("commit;")
print(f"-- {len(items)} roteiros virais", file=sys.stderr)
