# Regras Canônicas — Skill geracao-apresentacao-paciente

Estas regras são **invariantes da skill**. Toda alteração no código deve preservá-las.
Violações são bloqueadas pelo validador (`validador_exames.py`).

---

## RC-01 · Sexo do paciente é obrigatório

**Estabelecida:** 2026-05-05
**Motivo:** Refs clínicas de muitos exames variam por sexo. Aplicar ref masculina a uma paciente mulher (ou vice-versa) gera classificação clínica errada com risco de decisão médica inadequada.

**Exames cujas refs variam por sexo (lista canônica):**
- Hormonal: Testosterona Total, Testosterona Livre, Testo Biodisponível, Estradiol, Progesterona, FSH, LH, Prolactina, SHBG, DHEA-S
- Hemograma: Hemácias, Hemoglobina, Hematócrito
- Hepático: TGO, TGP, GGT, Fosfatase Alcalina
- Renal: Creatinina, Ácido Úrico
- Inflamatório: VHS
- Vitaminas/Minerais: Ferro, Ferritina

**Implementação:**
1. **Extractor LLM** (`extrair_exames_llm.py`): retorna `{"erro": "REGRA CANÔNICA..."}` se `paciente_meta["sexo"]` ausente ou diferente de `M/F`.
2. **Validador** (`validador_exames.py`): Layer 0 rejeita TODOS os exames se sexo ausente.
3. **System prompt** do LLM: inclui a regra explicitamente + exemplos das refs masculinas vs femininas.
4. **User prompt** do LLM: inclui `Sexo: MASCULINO/FEMININO` + faixas de referência específicas.

**Como o orchestrator (`gerar_apresentacao.py`) atende:**
Constrói `paciente_v9 = {"nome": ..., "sexo": paciente.get("sexo", "M"), ...}` antes de chamar o renderer. **Buscar do Quarkclinic** (campo `sexo` ou `gender`) ou do questionário.

**Quando o sexo não está disponível:**
Apresentação NÃO é gerada. Loga em `state/sem_sexo.log` e alerta operador.

---

## RC-02 · Validação multi-layer obrigatória antes do render

**Estabelecida:** 2026-05-05

Nenhum exame extraído via LLM entra na apresentação sem passar pelas 6 camadas:
- L0 Pre-check (sexo)
- L1 Schema (campos obrigatórios)
- L2 Catálogo (nome_canonico conhecido)
- L3 Plausibilidade (range absoluto fisiológico)
- L4 Sex-aware refs (refs específicas por sexo)
- L5 Cross-check (LDL ≈ Total − HDL − VLDL)
- L6 Status recalc (recalcula com refs canônicas)

Exames que falham vão para `revisao_manual` no log de auditoria — **nunca** para a apresentação.

---

## RC-03 · Hemograma diferencial usa valor absoluto

**Estabelecida:** 2026-05-05

Linfócitos/Neutrófilos/Monócitos/Eosinófilos/Basófilos/Bastonetes/Segmentados aparecem nos laudos com 2 colunas (% e absoluto/mm³). **Sempre usar o valor ABSOLUTO em /mm³** para classificar — nunca o percentual.

---

## RC-04 · Plaquetas com multiplicador

**Estabelecida:** 2026-05-05

Quando laudo mostra `242 x10³/mm³` ou `242 mil/mm³`, o LLM **deve multiplicar por 1000** antes de retornar (242000). O validador rejeita Plaquetas < 5000 como implausível.

---

## Auditoria

Cada apresentação gerada salva em `/tmp/<paciente>_audit.json`:
```json
{
  "paciente": "...",
  "sexo": "M",
  "lab": "...",
  "data_coleta": "...",
  "extraidos_pelo_llm": 54,
  "validados": 53,
  "revisao_manual": [...],
  "cross_check_warnings": [...]
}
```

---

## RC-05 · Refs clínicas IVS conservadoras (vs ADA/laboratorial padrão)

**Estabelecida:** 2026-05-05 (Tiaro)

A clínica Vital Slim adota critérios mais conservadores que os limites laboratoriais oficiais, porque o objetivo é **medicina funcional preventiva** — flagar risco metabólico antes do diagnóstico oficial.

| Exame | Padrão laboratorial | IVS conservador | Justificativa |
|-------|--------------------|-----------------:|---------------|
| HbA1c | < 5,7% | **< 5,4%** | Acima de 5,5 já indica risco alto de pré-diabetes |
| Glicemia Média Estimada | < 117 mg/dL | **< 100 mg/dL** | >100 sinaliza pré-diabetes silenciosa mesmo com HbA1c normal |
| HOMA-IR | < 2,7 | < 2,7 (igual) | — |
| Vitamina D | > 30 ng/mL | **> 80 ng/mL** | Função ótima, não apenas suficiência |
| Vitamina B12 | 211-946 pg/mL | **800-1500 pg/mL** | Função neurológica/metabólica ótima |
| Testosterona Total (M) | 264-916 ng/dL | **400-916 ng/dL** | Vitalidade, libido, composição corporal |

**Onde aplicar**: editar `assets/refs_canonicas.json`. Cada range tem campo `fonte` documentando o critério.

**Próximas refs IVS a definir** (pendente confirmação Tiaro):
- HDL mínimo (atual: M >40 / F >50)
- LDL alvo (atual: <130; IVS pode usar <100)
- Ferritina ótima (atual: M 30-400, F 13-150)
- Cortisol matinal (atual: 6,7-22,6 ug/dL)

---

## Versionamento

A versão do catálogo de refs está em `_metadata.versao` no JSON. Bump quando:
- Adicionar exame novo: bump minor (v1.0 → v1.1)
- Mudar ref existente: bump patch (v1.0 → v1.0.1)
- Mudança de schema: bump major (v1.0 → v2.0)

---

## RC-06 · Apresentação enviada SEMPRE pelo tópico Pacientes

**Estabelecida:** 2026-05-05 (Tiaro)

Toda apresentação clínica gerada por esta skill DEVE ser entregue via Telegram no tópico canônico Pacientes:

| Campo | Valor |
|-------|-------|
| Group ID | `-1003803476669` (AI Vital Slim) |
| Topic ID Pacientes | `271` |
| Bot | Maria (VitalSlimBot) |

**Implementação:**
- Função `enviar_apresentacao_para_topico_pacientes(html_path, paciente, exames_parsed)` no orchestrator
- Chamada automaticamente após `gerar_html_apresentacao()` completar
- Caption inclui: nome paciente, idade+sexo, contagem de exames (crit/alert/normal), data/hora

**Fonte da canonicidade:**
- `painel-unico-backlog-status-ivs-v2-2026-05-03.html` (F9): "topic_id do tópico Pacientes confirmado como 271"
- Logs de cron Maria-gerente confirmam: `"to": "-1003803476669:topic:271"`

**Quando o envio falha** (token ausente, network, etc):
- HTML é gerado e salvo normalmente em `deliverables/`
- Erro logado em stderr (não interrompe processamento de outros pacientes)
- Auditoria em `state/auditoria/` registra `telegram_ok: false`
- Operador deve fazer envio manual usando `enviar_apresentacao_para_topico_pacientes()`

---

## RC-07 · Personalização por perfil DISC

**Estabelecida:** 2026-05-05 (Tiaro)

A apresentação clínica DEVE adaptar tom, ênfase e linguagem ao perfil DISC do paciente identificado no questionário pré-consulta.

### Os 4 perfis e suas variações

| Perfil | Tom | Foco | Exemplo de H1 |
|--------|-----|------|---------------|
| **D — Dominante** | Direto, números, binário | ROI, decisão rápida, resultado mensurável | "Próximos 180 dias decidem se a tendência se mantém ou se você reverte agora" |
| **I — Influenciador** | Emocional, conector | Transformação, sentimento, jornada compartilhada | "Vamos transformar juntos como você sente seu corpo todo dia" |
| **S — Estável** | Acolhedor, sem pressão | Segurança, processo gradual, suporte da equipe | "Vamos caminhar juntos, no seu ritmo" |
| **C — Cauteloso/Analítico** | Técnico, científico | Evidências, métricas, biomarcadores | "Biomarcadores mostraram o quadro completo. 180 dias mapeados em 4 fases clínicas" |
| **default** | Neutro/equilibrado | Usado quando DISC ausente ou não detectável | (texto base) |

### Seções personalizadas por DISC

- `hero_eyebrow` — saudação inicial
- `hero_h1` — frase de positioning principal
- `dra_quote` — citação da Dra. Daniely
- `exames_lead` — lead da seção exames
- `spin_situacao_lead` / `spin_implicacao_lead` / `spin_necessidade_lead` — leads do SPIN
- `cta_eyebrow` / `cta_h2` / `cta_lead` — call to action
- `cta_opcao_now_*` / `cta_opcao_depois_*` — opções de decisão

### Implementação

1. **Catálogo:** `assets/disc_textos.json` — 16 chaves × 5 variantes (4 perfis + default)
2. **Detector:** `_detectar_perfil_disc(questionario)` lê campo `discPerfil` ou `disc` do questionário
3. **Selector:** `_t_disc(chave, perfil, **fmt)` retorna texto da variante (fallback default)
4. **Renderer:** `render_apresentacao_v9` detecta DISC e propaga para `render_hero` + `render_cta`

### Detecção de perfis compostos

Aceita formatos:
- Letra única: `"D"`, `"I"`, `"S"`, `"C"`
- Palavra: `"Dominante"`, `"Influente"`, `"Estável"`, `"Cauteloso"`
- Composto: `"Dominante / Influente"` → usa primário (D)
- Vazio ou desconhecido → `default`

### Quando atualizar os textos

Editar `assets/disc_textos.json`. Não precisa mexer em código.
Cada chave tem 5 variantes (default, D, I, S, C). Se uma variante não existe, cai no default automaticamente.

### Auditoria

O log de auditoria em `state/auditoria/<paciente>_<ts>.json` registra qual perfil DISC foi detectado e usado.
