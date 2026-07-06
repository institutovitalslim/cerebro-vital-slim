# Aplicações IVS — Loops Creator / Reels Eric Siu

**Fonte:** Instagram Reel público `DaamP-ElalP`  
**Data:** 2026-07-06  
**Responsável:** Maria — Gerência Geral IVS  
**Modo:** RapidAPI tentou e falhou; fallback público via `/embed/` baixou MP4 local. Sem login, sem bypass, sem preservar URL CDN assinada.

## Evidência coletada

- MP4 local: `/root/.hermes/maria-workspace/reel_DaamP_ElalP/reel_DaamP-ElalP.mp4`
- Intake IVS: `/root/.openclaw/reports/ivs-video-intake/20260706-070712-root-.hermes-maria-workspace-reel_DaamP_ElalP-reel_DaamP-ElalP.mp4/relatorio.html`
- Transcrição: `/root/.openclaw/reports/ivs-video-intake/20260706-070712-root-.hermes-maria-workspace-reel_DaamP_ElalP-reel_DaamP-ElalP.mp4/transcript/audio_16k.txt`
- Duração: 114.59s
- Formato: vertical 720x1280, h264 + aac
- Frames: 24

## Estrutura do Reels

O vídeo lista **7 AI loops para gerar dinheiro mais rápido**:

1. Revenue watchdog loop
2. Content loop
3. AEO + SEO loop
4. Outbound loop
5. Finance spend loop
6. Repo + skill loop
7. Codex continuation loop

Visualmente, é um talking head com slides simples no fundo, legenda palavra-a-palavra em laranja e diagramas minimalistas. O valor não está na estética; está na taxonomia operacional dos loops.

## Leitura IVS

A ideia central é converter tarefas recorrentes em sistemas que rodam com:

```text
estado -> observar -> agir -> avaliar -> decidir -> repetir/parar
```

Isso deve virar a base da nossa `ivs-loop-factory`.

---

# 1. Revenue Watchdog Loop → Pipeline comercial IVS

## Ideia do Reels

Monitorar pipeline, negócios parados, stage drift, revival de deals e evolução ao longo do tempo.

## Aplicação IVS

### Clara — Watchdog de leads/agendamentos

Objetivo: não deixar lead elegível morrer por falha de resposta, preço precoce, handoff humano stale ou status travado.

Loop:

```text
1. Ler conversas/logs WhatsApp e agenda QuarkClinic.
2. Identificar leads com:
   - sem resposta da Clara;
   - resposta genérica;
   - preço antes da jornada;
   - qualificado sem oferta D+2;
   - agendamento sem aviso Tiaro/Liane;
   - paciente confirmado ainda sendo tratado como lead.
3. Classificar risco: crítico, alto, médio, baixo.
4. Corrigir fluxo reversível ou escalar.
5. Reavaliar após correção.
6. Registrar evidence gate.
```

Eval:

- 0 leads elegíveis sem resposta no período auditado.
- 0 preço antes da jornada.
- 100% agendamento com aviso operacional.
- Relatório sem PII.

Human gate:

- Enviar mensagem real à lead fora do fluxo Clara.
- Pausar/despausar Clara.
- Alterar regra canônica.

Prioridade: **P0**.

---

# 2. Content Loop → Content Engine do João

## Ideia do Reels

Ingerir conteúdo, detectar spikes, transformar em novo conteúdo, medir o que funcionou e dobrar a aposta semanalmente.

## Aplicação IVS

### João — Weekly Content Compounding Loop

Loop:

```text
1. Ingerir Reels/posts do IVS + referências externas governadas.
2. Detectar spikes: retenção, comentários, salvamentos, leads gerados, CPL quando disponível.
3. Extrair padrões: hook, objeção, mecanismo, prova, CTA, formato visual.
4. Gerar variações IVS-first.
5. Passar por compliance/claim safety.
6. Publicar somente após aprovação do fluxo João/Maria.
7. Medir resultado e atualizar biblioteca de padrões.
```

Eval:

- Cada variação tem hipótese clara.
- Claim suportado.
- Sem promessa clínica.
- Métrica real pós-publicação registrada.

Human gate:

- Publicar.
- Usar imagem/depoimento de paciente.
- Alterar oferta/copy sensível.

Prioridade: **P1**.

---

# 3. AEO + SEO Loop → Autoridade científica/Local SEO IVS

## Ideia do Reels

Analisar concorrentes, conteúdo próprio, falas do founder em podcasts e decidir o que criar, atualizar, consolidar ou manter.

## Aplicação IVS

### Blog/SEO/AEO — Authority Loop

Loop:

```text
1. Coletar buscas locais e perguntas recorrentes de leads/pacientes.
2. Cruzar com conteúdo do blog/site/Instagram.
3. Identificar gaps de autoridade: obesidade, bioimpedância, menopausa, metabolismo, acompanhamento médico.
4. Propor artigos/posts com prova científica.
5. Ana valida quando houver conteúdo clínico sensível.
6. João transforma em post/reels/carrossel.
7. Monitorar ranking, tráfego e leads atribuíveis.
```

Eval:

- Cada pauta responde pergunta real.
- Conteúdo tem fonte ou validação clínica.
- Sem promessa de resultado.
- Possui CTA seguro para consulta/bioimpedância.

Human gate:

- Publicar artigo clínico.
- Alterar posicionamento médico.

Prioridade: **P2**.

---

# 4. Outbound Loop → Parcerias B2B e reativação governada

## Ideia do Reels

Pesquisar leads, enviar emails, medir resposta e melhorar o processo com o tempo.

## Aplicação IVS

No IVS, **não deve virar disparo automático para pacientes/leads**. O uso seguro é B2B/parcerias ou drafts internos.

### Maria/João — Partner Outbound Loop

Loop:

```text
1. Buscar parceiros locais premium: salões, studios, academias boutique, estética, pilates.
2. Score: público compatível, reputação, localização, fit premium, risco de marca.
3. Gerar abordagem institucional.
4. Revisão humana.
5. Envio manual/aprovado.
6. Registrar resposta e melhorar critérios.
```

Eval:

- Lista deduplicada.
- Evidência pública de cada parceiro.
- Score e justificativa.
- Mensagem não invasiva.

Human gate:

- Enviar WhatsApp/e-mail/DM.
- Propor parceria comercial.

Prioridade: **P2**.

---

# 5. Finance Spend Loop → Pedro/Controller

## Ideia do Reels

Encontrar gasto duplicado, ferramentas não usadas, contractor spend, risco de renovação e spikes de gasto.

## Aplicação IVS

### Pedro — Spend Audit Loop

Loop:

```text
1. Ler Omie/planilhas/assinaturas em modo read-only.
2. Classificar gastos recorrentes.
3. Detectar duplicidade, spike, renovação próxima, ferramenta subutilizada.
4. Gerar pauta de economia.
5. Tiaro aprova corte/renegociação.
6. Pedro acompanha resultado financeiro.
```

Eval:

- Potencial de economia estimado.
- Fonte do gasto identificada.
- Risco operacional mapeado.
- Nenhuma escrita financeira sem gate.

Human gate:

- Cancelar serviço.
- Mover dinheiro.
- Alterar Omie.
- Negociar contrato.

Prioridade: **P1**.

---

# 6. Repo + Skill Loop → Evolução dos agentes IVS

## Ideia do Reels

Olhar para correções, falhas, runs ruins e identificar o que deve virar skill.

## Aplicação IVS

### Maria/Jarvis — Skillification Loop

Loop:

```text
1. Ler sessões/processos recentes com falhas ou workflows repetidos.
2. Identificar padrões: erro recorrente, procedimento útil, ajuste operacional.
3. Classificar: memory, skill, cérebro/RC-25, script, nada.
4. Criar/patchar skill quando houver procedimento reutilizável.
5. Validar skill com exemplo real.
6. Registrar trace e evitar duplicidade.
```

Eval:

- Skill tem trigger claro.
- Tem passos executáveis.
- Tem pitfalls e verificação.
- Não grava segredo nem progresso temporário.

Human gate:

- Canonizar regra no cérebro.
- Alterar skill de outro perfil com efeito sensível.

Prioridade: **P0**.

---

# 7. Codex Continuation Loop → Continuidade entre runs/agentes

## Ideia do Reels

Manter trabalho de engenharia atravessando runs sem perder contexto, bloqueadores ou trace.

## Aplicação IVS

### Todos os agentes — Continuation / Handoff Loop

Loop:

```text
1. Ao terminar contexto/processo, salvar state.json + trace.md + next_action.
2. Próximo run lê estado antes de agir.
3. Continua só do ponto validado.
4. Rebaixa status se faltar evidência.
5. Evita repetir trabalho ou declarar conclusão falsa.
```

Aplicações imediatas:

- Light Copy: continuar transcrições sem fingir 100%.
- Voicebox/Jarvis: manter smoke tests e pendências.
- Clara: incidente de conversa com lead.
- João: relatório diário e publication board.
- Pedro: conciliação/Omie.

Eval:

- O próximo agente entende status em 2 minutos.
- Tem artefato/path/log real.
- Tem stop_reason.
- Tem próximo passo claro.

Prioridade: **P0**.

---

# Matriz de prioridade IVS

| Loop | Dono | Impacto | Risco | Prioridade |
|---|---|---:|---:|---:|
| Revenue watchdog / leads | Clara + Maria | Muito alto | Médio | P0 |
| Repo + skill loop | Maria + Jarvis | Muito alto | Baixo | P0 |
| Continuation loop | Todos | Muito alto | Baixo | P0 |
| Finance spend loop | Pedro | Alto | Alto | P1 |
| Content loop | João | Alto | Médio | P1 |
| AEO/SEO loop | João + Ana | Médio/Alto | Médio | P2 |
| Outbound/parcerias | Maria + João | Médio | Alto | P2 |

# Como isso muda a `ivs-loop-factory`

A skill que vamos criar não deve ser só uma cópia do Loops Creator. Ela precisa nascer com os 7 loops IVS como presets.

Estrutura recomendada:

```text
ivs-loop-factory/
  SKILL.md
  templates/
    loop-spec.md
    state.json
    trace.md
    stop-reason.md
  presets/
    clara-revenue-watchdog.md
    joao-content-loop.md
    seo-aeo-authority-loop.md
    partner-outbound-loop.md
    pedro-finance-spend-loop.md
    repo-skillification-loop.md
    continuation-handoff-loop.md
  scripts/
    create_ivs_loop.py
    validate_loop_trace.py
  examples/
    lightcopy-transcription/
    clara-jornada-preco/
    jarvis-voicebox-pilot/
```

# Regra IVS a embutir

Todo loop IVS precisa terminar com:

```text
status: DONE | DONE_WITH_CONCERNS | PARTIAL | BLOCKED | NEEDS_APPROVAL
stop_reason: success | plateau | blocked | budget_exhausted | human_gate
real_evidence: paths/logs/messageId/http status/metric/transcript
next_action: próxima ação concreta
```

# Recomendação final

Criar a `ivs-loop-factory` com 3 pilotos primeiro:

1. **Clara Revenue Watchdog** — maior impacto imediato em agendamentos.
2. **Repo + Skillification Loop** — melhora todos os agentes continuamente.
3. **Continuation Loop** — resolve perda de contexto e falso DONE em processos longos.

Depois expandir para João Content Loop e Pedro Finance Spend Loop.
