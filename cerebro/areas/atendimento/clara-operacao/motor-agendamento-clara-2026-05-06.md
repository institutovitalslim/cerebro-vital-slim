# Clara — Motor de Agendamento de Pacientes (2026-05-06)

## Decisão operacional
Tiaro autorizou autonomia total para transformar Clara em uma máquina de agendamento de pacientes, mantendo ética médica e tom premium.

## Melhorias aplicadas

1. **Janela ativa de lead**
   - Lead conhecido continua atendido pela Clara dentro de janela ativa operacional.
   - Corrige perda de continuidade em conversas de múltiplas mensagens.
   - Mantém bloqueio quando há takeover humano/manual.

2. **Bloqueio real de paciente QuarkClinic**
   - Se QuarkClinic detectar paciente existente, Clara fica em silêncio conforme RC-12.
   - Evita Clara atuar onde a equipe humana deve cuidar.

3. **Contexto operacional do lead no prompt**
   - Clara recebe contagem segura de interações e dados operacionais não sensíveis.
   - Não menciona isso ao lead.

4. **Registro de resposta enviada**
   - Estado local passa a registrar último envio e estender janela ativa.
   - Serve para continuidade e auditoria.

5. **Patch de prompt — Máquina de Agendamento**
   - Proibido encerrar passivamente.
   - Toda resposta deve acolher, avançar, reduzir atrito ou propor próximo passo.
   - Preferir oferta de horários/turnos concretos.
   - Objeção tratada como pedido de segurança, não rejeição.
   - Preço permitido volta para contexto e agendamento.

## Guardrails preservados
- Clara não diagnostica.
- Clara não prescreve.
- Clara não promete resultado.
- Clara não atende paciente já realizado no QuarkClinic.
- Clara não sobrepõe humano em manual takeover.
- Clara não divulga valores de programa antes da consulta.

## Próximo padrão esperado
Clara deve conduzir toda conversa para um destes desfechos:
- avaliação agendada;
- pré-reserva/horário em andamento;
- objeção real identificada;
- follow-up com data;
- handoff humano quando obrigatório.

## QA recorrente adicionada

Cron criado:
- Nome: `Clara Agendamento — QA diário de conversão`
- ID: `13141b04-2bdc-44da-9967-350328c33911`
- Agenda: `30 22 * * *`, TZ `America/Bahia`
- Objetivo: revisar diariamente sinais de agendamento, objeção e silêncio, sem expor PII, e propor melhorias práticas para Clara.

## Acompanhamento próximo — decisão Tiaro (2026-05-06)

Tiaro determinou: Maria deve acompanhar a evolução da Clara de perto, fazendo tudo que for necessário para que ela se torne uma máquina de agendamento de pacientes.

### Cadência operacional criada

1. **Health check matinal**
   - Nome: `Clara Guardrail Health — manhã`
   - ID: `ce9ea71e-ec78-496e-ab73-4fe2d00319a2`
   - Agenda: `50 7 * * *`, TZ `America/Bahia`
   - Objetivo: validar bridge ativo, Clara não pausada, overrides e falhas de crons antes do expediente.

2. **Pulse 2/2h em horário comercial**
   - Nome: `Maria Pulse — Clara máquina de agendamento 2/2h`
   - ID: `535f3616-8621-483d-a895-6f1d57d81222`
   - Agenda: `55 8-22/2 * * *`, TZ `America/Bahia`
   - Objetivo: acompanhar saúde, volume recente, qualidade de sinal, riscos e ação tática a cada ciclo.

3. **QA diário de conversão**
   - Nome: `Clara Agendamento — QA diário de conversão`
   - ID: `13141b04-2bdc-44da-9967-350328c33911`
   - Agenda: `30 22 * * *`, TZ `America/Bahia`
   - Objetivo: revisar sinais de agendamento, objeção e silêncio e promover melhoria via Graphify/RC-25 quando estrutural.

4. **Revisão estratégica semanal**
   - Nome: `Clara Strategy Review — semanal agendamento`
   - ID: `79822d71-e7f8-410c-bbfe-0a3021eb09fd`
   - Agenda: `0 7 * * 1`, TZ `America/Bahia`
   - Objetivo: identificar gargalos, desenhar testes A/B, ajustar playbook/prompt e consolidar aprendizados no cérebro.

### Regras de acompanhamento
- Maria não pausa Clara sem ordem explícita de Tiaro.
- Maria não expõe PII em relatórios.
- Toda mudança estrutural deve ir para cérebro via Graphify/RC-25 e GitHub com commit+push.
- O objetivo operacional da Clara é agendamento qualificado, preservando guardrails clínicos.

## Regra canônica adicionada — prazo mínimo de agendamento

Tiaro definiu que Clara nunca deve oferecer agendamento para o mesmo dia ou para o dia seguinte, para dar tempo da equipe humana executar os aspectos operacionais. A oferta mínima é D+2 ou data posterior. Esta regra prevalece sobre qualquer técnica de fechamento.

## Regra canônica adicionada — aviso Tiaro + Liane após agendamento

Tiaro definiu que sempre que Clara agendar, confirmar reserva, pré-reserva ou avançar para pagamento/link de pré-consulta, Tiaro e Liane devem ser informados por WhatsApp. A regra foi adicionada ao prompt e ao runtime operacional para notificação interna automática quando o padrão de agendamento for detectado.
