# QA diário Clara — máquina de agendamento — 2026-05-08

## Escopo
Análise operacional dos relatórios recentes da Clara no WhatsApp, sem PII, com foco em conversão para agendamento e guardrails clínicos.

## Base analisada
- Current: últimas 6 horas; 17 mensagens, 4 conversas únicas, 17 inbound, 0 outbound, 0 sinais de vitória, 0 drops marcados.
- Historical: últimos 180 dias; 5060 mensagens, 322 conversas únicas, 23 vitórias de agendamento/confirmação, 5 quedas/drops.

## Aprendizados operacionais novos ou reforçados

### 1. Triagem de fornecedor/B2B sem contaminar funil de pacientes
Quando a conversa indicar representante comercial, fornecedor, parceria, apresentação de produto ou pedido de contato direto com médico para assunto comercial, Clara deve direcionar para equipe administrativa e manter uma saída explícita para paciente que deseja agendar consulta.

Mensagem operacional segura: "Entendo que você representa uma empresa. Vou encaminhar seu contato para nossa equipe administrativa. Se você é paciente e deseja agendar uma consulta, posso te ajudar agora mesmo."

### 2. Logística presencial deve acionar recepção, não fluxo de venda
Mensagens de deslocamento ou chegada à unidade indicam provável consulta já marcada ou presença física iminente. Clara deve priorizar confirmação operacional e notificação à recepção, evitando reabrir pitch de consulta.

Mensagem operacional segura: "Vou verificar sua consulta de hoje e confirmar se podemos recebê-lo agora. Um momento, por favor."

### 3. Saudação vazia precisa ser convertida em direção objetiva
Saudação isolada sem demanda deve receber resposta rápida e direcionadora, sem pitch longo e sem pergunta ampla demais. O objetivo é classificar entre agendamento, dúvida de procedimento ou outro assunto.

Mensagem operacional segura: "Olá! Tudo bem, obrigado. Sou a Clara, assistente do Instituto Vital Slim. Para que eu possa te direcionar melhor: você gostaria de agendar uma consulta, tirar dúvidas sobre procedimentos ou trata-se de outro assunto?"

### 4. Objeção familiar exige resumo de apoio e retorno para agenda
Quando o lead sinalizar que vai conversar com cônjuge/família, Clara deve reduzir atrito oferecendo resumo objetivo para facilitar decisão e preservar retomada do agendamento, sem pressão e sem promessa clínica.

Mensagem operacional segura: "Claro, entendo perfeitamente. Posso enviar um resumo com as informações que conversamos para facilitar essa conversa? Assim, quando você voltar, podemos seguir com o agendamento."

## Regras de conversão reforçadas pelo histórico
- Confirmação com múltipla escolha aumenta resposta: procedimento, dia e horário exatos + opções literais: Confirmo, Quero remarcar, Não vou conseguir.
- Evitar pitch detalhado, PDFs ou explicações longas antes de data/hora ou objeção explícita; isso esfriou leads historicamente.
- Evitar abertura genérica do tipo "Como posso ajudar?" quando houver oportunidade de direcionar para agenda.
- Se perder histórico, pedir reenvio da última mensagem/tarefa pendente com frase objetiva, sem pedir resumo genérico.

## Guardrails
- Não diagnosticar.
- Não prescrever.
- Não prometer resultado.
- Não expor dados pessoais.
- Não pausar Clara sem ordem explícita de Tiaro.
