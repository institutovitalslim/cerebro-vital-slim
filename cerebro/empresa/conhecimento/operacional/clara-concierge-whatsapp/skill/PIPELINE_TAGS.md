# Pipeline de Tags WhatsApp

Source: MEMORIA_CONSOLIDADA_2026-04-28.md, secao 7.

## Tags oficiais

| Tag | Volume atual | Definicao | Clara age? |
|-----|--------------|-----------|------------|
| **Lead** | 63 | Conduzir ate agendamento ou negativa | ✅ Sim |
| **Nao Qualificado** | 70 | Sem perfil financeiro / quer servico diferente / <14 anos | 🔄 Recupera D+60 |
| **Agendou** | 1 | Followup ate comparecer a consulta | ✅ Sim |
| **Paciente** | 15 | 1+ atendimentos no QuarkClinic | ❌ NAO (so crons) |
| **VIP** | 22 | Paciente importante - tag transversal | ❌ NAO (so crons) |
| **Programa** | 15 | Grupos de Programa de Acompanhamento | ❌ NAO (humanos) |
| **Referido** | 3 | Indicacao - tag transversal | ✅ Sim (template referencia) |

## Pipeline visual

```
LEAD (63) ─────► AGENDOU (1) ─────► PACIENTE (15) ─────► [STOP CLARA]
   │                                       │
   └──► NAO QUALIFICADO (70)               └──► PROGRAMA (15 grupos)
            │                                       │
            └──► RECUPERACAO D+60                   └──► VIP (22, transversal)
```

## Transicoes

- **Lead → Agendou**: paga pre-consulta R$ 300
- **Agendou → Paciente**: comparece a consulta (cadastra no QuarkClinic)
- **Paciente → Programa**: adere ao Programa de Acompanhamento
- **Lead → Nao Qualificado**: criterios RC-13

## Fonte de verdade vs tags

⚠️ **IMPORTANTE**: as tags do WhatsApp SOZINHAS nao sao confiaveis. Sempre validar com QuarkClinic (RC-21).

```
LEAD = 0 atendimentos no QuarkClinic
PACIENTE = 1+ atendimentos no QuarkClinic
```

A tag pode estar desatualizada. O sistema e a fonte unica.

## Estrutura de nomes (gramatica)

```
[MES] [LETRA?] - [TIPO] - [Nome] - [Plano] [Subplano?] [Relacao?]
```

### Componentes
- **Mes**: JANEIRO, FEVEREIRO, ..., DEZEMBRO (mes de entrada)
- **Letra**: ABRIL A apenas (cohort temporaria Google Ads abril/2026)
- **Tipo**: LEAD, Lead, Pac, Pct., Agen, Agend, Canc, Nao, Referido, VIP
- **Plano**: Bradesco / SulAmerica / Amil / Particular / Mamaes Baianas
- **Sub-Bradesco**: Saude, Mediservice, Flex, Torres, Souza, Empresarial
- **Relacao**: Marido X, Esposa Y, Mae Z, Amiga W, Esposo V, Filha Evelyn

### Exemplos reais

```
JANEIRO - Aristoteles da Costa             (paciente JAN, sem plano explicito)
ABRIL A - Dora Ribeiro                     (lead da campanha Google Ads)
DEZEMBRO - Patrick Mascarenhas - Bradesco  (paciente Bradesco)
13-01-26 - LEAD - Patricia - Amiga Daniela Vitorio  (referida)
17-07-25 - Pac - Elisia Amiga Josefa - Particular   (paciente)
VIP - Daniel Rodrigo - Bradesco                     (VIP recorrente)
```

### Estrutura de grupos VIP/Programa
```
VIP - [Nome] [idade]a - Acompanhamento [3m / 6m / Anual] - [data fechamento DD.MM.YY]
```

Ex: `VIP - Felipe Alencar - Acompanhamento 6m - 32a - 14.10.25`

## Relevancia para Clara

Quando Clara recebe mensagem entrante:
1. Identifica fone do contato
2. Consulta QuarkClinic (fonte de verdade) → atendimentos > 0?
3. Se SIM → escala humano (RC-12). FIM.
4. Se NAO → trata como Lead, segue fluxo de qualificacao SPIN
5. Detecta persona pelo conteudo da mensagem
6. Aplica template adequado
