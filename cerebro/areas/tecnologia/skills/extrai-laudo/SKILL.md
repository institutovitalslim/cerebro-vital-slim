# Skill: extrai_laudo.py

## Propósito
Extrai automaticamente todos os resultados de exames de laudos laboratoriais em PDF
e classifica cada exame como OK, ALTO, BAIXO, CRÍTICO ALTO ou CRÍTICO BAIXO.

## Formatos suportados
| Formato | Laboratórios | Identificação |
|---------|-------------|---------------|
| `CRMBA1865` | SSA Trade Center, Itapoan, Villas do Atlântico | "Laboratorio registrado no CRM/BA 1865" |
| `SABIN` | Sabin Diagnósticos | "SABIN" no header |
| `CRMLPC` | Hermes Pardini, CRM-LPC | "VALORES ENCONTRADOS" ou "CRM-LPC" |
| `DBRECIFE` | DB Recife / Instituto Vital Slim | "DB RECIFE" ou "INSTITUTO VITAL SLIM" |

## Uso
```bash
# Saída formatada (legivel)
python3 extrai_laudo.py <arquivo.pdf> --sexo M|F

# Saída JSON (para integração)
python3 extrai_laudo.py <arquivo.pdf> --sexo M --json

# Com idade
python3 extrai_laudo.py <arquivo.pdf> --sexo F --idade 45
```

## Uso como módulo
```python
from extrai_laudo import extrai

paciente, resultados, grupos = extrai("/path/to/laudo.pdf", sexo="M")

# resultados: lista de dicts {exame, valor, unidade, referencia, status}
# grupos: dict agrupado por categoria (Hemograma, Lipidograma, etc.)
# status: "ok" | "alto" | "baixo" | "critico_alto" | "critico_baixo" | "?"

# Filtrar apenas alterados
alterados = [r for r in resultados if r["status"] not in ("ok", "?")]
```

## Grupos temáticos gerados
- Hemograma
- Glicemia / Insulina (inclui HOMA-IR calculado)
- Lipidograma
- Inflamação / Coagulação
- Fígado / Rins
- Minerais
- Vitaminas
- Tireoide
- Hormônios
- Outros

## Cálculos automáticos
- **HOMA-IR**: calculado automaticamente se Insulina + Glicose presentes
  - Fórmula: (Glicose × Insulina) / 405
  - Ref: ≤2.7 = normal, 2.7-4.0 = resistência, >4.0 = crítico

## Correções de classificação embutidas
- **Vitamina D**: 20-100 ng/mL = OK, >100 = Alto (toxicidade), <20 = Baixo
- **IGF-1 / Somatomedina**: usa range adulto (80-350 ng/mL)
- **Zinco**: adultos 60-130 µg/dL
- **Magnésio**: adultos 1.6-2.6 mg/dL
- **Progesterona masculina**: ≤0.2 ng/mL = normal

## Limitações conhecidas
- Hemograma em formato de tabela (pág 1 de alguns laudos) não é extraído — apenas exames com linha "RESULTADO:"
- Testosterona Livre em nmol/L removida (mantém pg/mL, mais interpretável)
- Referências por faixa etária complexas: pode não classificar exames pediátricos corretamente
- Requires: pdfplumber (`pip install pdfplumber`)

## Laudos de referência usados para desenvolvimento
- Tiaro Fernandes Neves — Sabin Mar/2026 (CRM/BA 1865)
- Erick Magalhães Santos — Trade Center Abr/2026 (CRM/BA 1865)
- Francisco de Assis de Lima — Itapoan Abr/2026 (CRM/BA 1865)
- Silvana Modesto Rodrigues — Itapoan Abr/2026 (CRM/BA 1865)
- Mario Gomes de Abreu Filho — CRM-LPC Abr/2026

## Versão
v1.0 — 2026-04-28 — Clara (Instituto Vital Slim)
