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
