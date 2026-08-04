#!/usr/bin/env python3
"""Gera SQL de seed dos 38 dispositivos narrativos (lendo a biblioteca md) + tipos de CTA globais.
Saida: SQL no stdout (aplicar via psql). Idempotente: limpa os globais e reinsere."""
import re, sys

MD = sys.argv[1] if len(sys.argv) > 1 else \
    "/root/cerebro-vital-slim/sistemas/content-engine-os/docs/biblioteca-dispositivos-stories10x.md"

def esc(s):
    return (s or "").replace("'", "''").strip()

rows = []
for ln in open(MD, encoding="utf-8"):
    ln = ln.strip()
    m = re.match(r"^\|\s*(\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|\s*$", ln)
    if m:
        num, name, logic, example = (x.strip() for x in m.groups())
        rows.append((int(num), name, logic, example))

print("begin;")
print("delete from narrative_devices where tenant_id is null;")
for num, name, logic, example in rows:
    print(
        "insert into narrative_devices (tenant_id, code, name, logic, example, ai_instruction, category) values "
        f"(null, 'D{num}', '{esc(name)}', '{esc(logic)}', '{esc(example)}', "
        f"'Use o dispositivo \"{esc(name)}\": {esc(logic)} Adapte ao nicho/persona e ao tom da marca; mantenha compliance.', "
        "'engajamento');"
    )
# Tipos de CTA globais (semente)
ctas = [
    ("inbox", "Me manda no inbox", None),
    ("enquete", "Responda a enquete", None),
    ("link_vendas", "Garanta sua vaga", None),
    ("link_conteudo", "Acesse o conteúdo completo", None),
    ("captura", "Cadastre-se para receber", None),
    ("caixinha", "Manda sua dúvida na caixinha", None),
    ("sem_cta", "", None),
]
print("delete from ctas where tenant_id is null;")
for t, txt, dest in ctas:
    d = "null" if dest is None else f"'{esc(dest)}'"
    print(f"insert into ctas (tenant_id, type, text, destination) values (null, '{t}', '{esc(txt)}', {d});")
print("commit;")
print(f"-- {len(rows)} dispositivos + {len(ctas)} CTAs", file=sys.stderr)
