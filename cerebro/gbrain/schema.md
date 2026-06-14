# GBrain IVS — Schema Canônico Adaptado

## Princípio
A estrutura GBrain aplicada ao IVS é uma camada de organização, busca e grafo sobre o cérebro existente. Ela não apaga a taxonomia IVS; ela a torna resolvível.

## Tipos canônicos

| Tipo GBrain | Uso IVS | Diretório primário |
|---|---|---|
| `policy` | regra permanente, governança, compliance | `cerebro/areas/governanca/` |
| `operation` | processo operacional, rotina, SOP | `cerebro/areas/operacoes/` |
| `agent` | memória, identidade, ferramentas e limites dos agentes | `cerebro/agentes/` |
| `skill` | instrução executável/operacional | `skills/` ou `cerebro/areas/*/skills/` |
| `project` | projeto ativo, implantação, campanha | `cerebro/empresa/projetos/` ou área correspondente |
| `marketing` | criativos, tráfego, Reels, João | `cerebro/areas/marketing/` |
| `patient-ops` | operação de apresentação/devolutiva sem contato direto com paciente | `cerebro/areas/operacoes/` |
| `finance` | Omie, boletos, conciliação, financeiro | `cerebro/areas/financeiro/` |
| `technology` | integrações, runtime, automações, OpenClaw | `cerebro/areas/tecnologia/` |
| `concept` | entidades/conceitos resolvíveis no grafo: agentes, pessoas, sistemas e organização | `cerebro/gbrain/entities/` |
| `raw-rc25` | evidência bruta de mudança governada | `cerebro/operacional/graphify-*/raw/` |

## Campos recomendados em novos arquivos

```yaml
---
type: operation|policy|agent|skill|project|marketing|finance|technology|concept|raw-rc25
status: draft|active|deprecated|superseded
owner: maria|joao|clara|pedro|tiaro|equipe
source_of_truth: true|false
created: YYYY-MM-DD
updated: YYYY-MM-DD
rc25: graphify-YYYY-MM-DD-slug
---
```

## Regras de compatibilidade
- Arquivos antigos não precisam ser reescritos imediatamente.
- Novos arquivos devem seguir os campos recomendados.
- Ao tocar arquivo antigo por mudança estrutural, adicionar frontmatter compatível quando seguro.
- Slugs GBrain devem apontar para o arquivo canônico, não duplicar conteúdo.
