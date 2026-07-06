# Análise IVS — Loops Creator Kit

**Fonte pública analisada:** `https://loops-creator-kit-site.vercel.app/`  
**Data:** 2026-07-05  
**Responsável:** Maria — Gerente Geral IVS  
**Modo:** read-only, sem login, sem bypass, token/query string não preservado nos artefatos.

## 1. O que foi coletado

O site entrega um kit gratuito da Single Grain / Eric Siu para transformar prompts únicos em **loops operacionais**.

Arquivos extraídos da página pública:

| Arquivo | Linhas | Função |
|---|---:|---|
| `skills/loops-creator.md` | 1206 | Skill principal para desenhar, operar e revisar loops fechados de agentes |
| `templates/loop-spec.md` | 52 | Template de especificação de loop |
| `templates/state.json` | 18 | Estado mínimo de execução |
| `templates/trace.md` | 32 | Trace de iterações |

Cópias locais sanitizadas:

```text
/root/.hermes/maria-workspace/loops_creator_kit_analysis/skills/loops-creator.md
/root/.hermes/maria-workspace/loops_creator_kit_analysis/templates/loop-spec.md
/root/.hermes/maria-workspace/loops_creator_kit_analysis/templates/state.json
/root/.hermes/maria-workspace/loops_creator_kit_analysis/templates/trace.md
```

## 2. Ideia central

A distinção principal é excelente para o IVS:

```text
Prompt/comando único = responde uma vez.
Loop = observa estado, age, avalia, decide e repete até uma condição de parada.
```

A fórmula canônica do kit:

```text
goal -> plan -> act -> observe -> evaluate -> decide -> improve or stop
```

Isso conversa diretamente com o que já aplicamos no IVS como **NEXUS-IVS + Evidence Gate**.

## 3. Pontos fortes

1. **Separação clara entre one-shot e loop real**  
   Evita agente dizendo que “rodou loop” quando só respondeu uma vez.

2. **Eval antes da iteração**  
   O kit força a definir critério de avaliação antes de começar a melhorar.

3. **Stop conditions explícitas**  
   Sucesso, falha, orçamento, plateau, risco e handoff humano.

4. **Trace obrigatório**  
   Cada iteração registra ação, observação real, score/resultado e decisão.

5. **Human gates muito alinhados ao IVS**  
   Bloqueia envio, publicação, gastos, alteração de dados, contato com cliente/prospect e claims sem prova.

6. **Portabilidade**  
   O material é Markdown + templates simples. Dá para usar em Hermes, Codex, Claude Code e OpenClaw.

## 4. Pontos que precisam adaptação IVS

| Tema | Risco se copiar bruto | Adaptação IVS necessária |
|---|---|---|
| Autonomia | Pode incentivar loops autônomos demais | Reforçar aprovação para WhatsApp, paciente, publicação, financeiro e Omie |
| Marketing | Rubricas genéricas | Acrescentar compliance médico, claim safety e prova científica/operacional |
| Leads/outbound | O kit cita lead sourcing e emails | No IVS, contato externo nunca é automático; só draft interno |
| Saúde | Não contempla CFM/ética médica | Ana/Maria precisam gatear claims e conteúdo clínico |
| Produção | Pode virar scheduler sem governança | Começar como loop manual/cron no-agent antes de automação real |

## 5. Encaixe com arquitetura atual IVS

O kit não substitui o **NEXUS-IVS**. Ele complementa.

### NEXUS-IVS atual

```text
Intake -> Roteamento -> Execução -> Evidence Gate -> Reality Check -> Registro -> Aprendizado
```

### Loops Creator adiciona

```text
Estado explícito + score por iteração + plateau + trace + stop reason
```

### Síntese recomendada

```text
NEXUS-IVS = sistema operacional multiagente.
Loops Creator = motor de iteração para tarefas repetíveis dentro do NEXUS.
```

## 6. Loops IVS que valem criar primeiro

### 6.1 Clara — Atendimento antes do preço

**Objetivo:** reduzir reincidência da Clara falando valor antes da jornada.

Loop:

```text
1. Coletar conversas elegíveis do período.
2. Classificar se houve: descoberta -> jornada -> encaixe -> valor.
3. Marcar violações.
4. Gerar patch de instrução/runtime se a falha repetir.
5. Reavaliar amostra após correção.
6. Parar quando 0 violações críticas em N conversas ou quando faltar log.
```

Eval:

- Valor só depois da jornada e do encaixe.
- Uma pergunta por vez.
- Sem medicalizar.
- Sem PII no relatório.

Human gate:

- Enviar mensagem real à lead.
- Pausar Clara.
- Alterar regra canônica.

### 6.2 João — Reels/Ads Creative Evidence Loop

**Objetivo:** gerar melhores conceitos de Reels sem inventar claim clínico.

Loop:

```text
1. Definir público, dor, promessa segura e prova permitida.
2. Gerar 20 hooks.
3. Pontuar thumb-stop, clareza, novidade, fit IVS e claim safety.
4. Expandir top 5 em roteiros.
5. Validar compliance e produção.
6. Entregar 3-5 roteiros testáveis com score e risco.
```

Eval:

- Hook forte.
- Claim suportado.
- CTA claro.
- Linguagem premium.
- Sem promessa de resultado.

Human gate:

- Publicar.
- Usar imagem/depoimento de paciente.
- Mudar oferta.

### 6.3 Maria — Incident / Cron Recovery Loop

**Objetivo:** reduzir falso “concluído” em crons e processos longos.

Loop:

```text
1. Ler output real do cron/processo.
2. Classificar: success, transient failure, auth failure, timeout, missing evidence.
3. Corrigir se reversível.
4. Reexecutar/validar.
5. Atualizar status DONE/PARTIAL/BLOCKED.
6. Parar quando houver evidência ou bloqueio real documentado.
```

Eval:

- Log real lido.
- Causa provável indicada.
- Reexecução ou bloqueio claro.
- Não chamar de concluído sem artefato.

### 6.4 Light Copy / Cursos — Transcription Evidence Loop

**Objetivo:** só promover aprendizado com transcrição validada.

Loop:

```text
1. Ler worklist.
2. Identificar aulas sem .txt validado.
3. Se mídia acessível, baixar/transcrever sem burlar DRM.
4. Validar tamanho e conteúdo do .txt.
5. Atualizar manifesto.
6. Parar em sessão expirada, ausência de mídia, ou 100% transcrito.
```

Eval:

- `.txt` existe.
- Tamanho compatível.
- Conteúdo legível.
- Status `PARTIAL` se faltar aula.

### 6.5 Jarvis — Router / Builder / Verifier Loop

**Objetivo:** impedir Jarvis de resolver no lugar errado sem roteamento.

Loop:

```text
1. Classificar domínio da demanda.
2. Decidir se responde, roteia ou delega.
3. Executar apenas se couber no escopo.
4. Verificar evidência.
5. Retornar com dono, status e próximo passo.
```

Eval:

- Escopo correto.
- Não usurpou João/Clara/Pedro/Ana.
- Evidence Gate aplicado.

## 7. Decisão recomendada

**Recomendação:** adaptar, não instalar bruto.

Criar uma skill IVS-first chamada, por exemplo:

```text
ivs-loop-factory
```

Ela deve conter:

```text
SKILL.md
references/loops-creator-source-analysis.md
references/templates/loop-spec.md
references/templates/state.json
references/templates/trace.md
scripts/create_ivs_loop.py
scripts/validate_ivs_loop.py
examples/clara-jornada-preco/
examples/joao-reels-creative-loop/
examples/maria-cron-recovery-loop/
examples/lightcopy-transcription-loop/
```

## 8. Critérios de implantação

### Aplicar agora

- Usar a lógica nos próximos loops manuais da Maria.
- Exigir `trace.md` para qualquer processo iterativo longo.
- Exigir `stop_reason` em relatórios de processo.

### Testar por 3 dias

- Clara jornada/preço.
- Maria cron/processo longo.
- João Reels creative loop.

### Só canonizar depois

- Se os loops reduzirem falso DONE.
- Se os traces forem úteis e não virarem burocracia.
- Se os agentes conseguirem usar sem travar operação.

## 9. Veredito

```text
ALTO VALOR — adaptar para IVS como motor de loops dentro do NEXUS-IVS.
```

Não é uma skill “de conteúdo”; é uma skill de **governança operacional e melhoria contínua**.

A melhor aplicação imediata é elevar o padrão de todos os agentes de:

```text
fazer tarefa -> dizer concluído
```

para:

```text
estado -> ação -> evidência -> avaliação -> próxima decisão -> stop reason
```

## 10. Pendências / limites da análise

- O site não tinha `robots.txt`, `sitemap.xml` ou `llms.txt` disponível; retornaram 404.
- Conteúdo coletado somente da página pública HTML.
- Não houve login, bypass, stealth ou uso de token em artefato.
- Não instalei a skill em produção; gerei análise e cópia local sanitizada.
