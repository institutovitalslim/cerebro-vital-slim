# Graphify RC-25 — QA diário Clara como máquina de agendamento — 2026-05-29 01:30 UTC

## Escopo
Registro canônico e sanitizado do QA diário da Clara no WhatsApp, com foco em conversão para agendamento, objeções, silêncio e guardrails clínicos. Não contém PII, telefones ou conversas sensíveis.

## Base analisada
- Current: últimas 6 horas; 20 mensagens, 9 leads únicos, 20 inbound, 0 outbound, 0 vitórias, 0 quedas. Fonte: `latest-whatsapp-current.json` de 2026-05-29 01:18 UTC.
- Historical: últimos 180 dias; 5653 mensagens, 372 leads únicos, 2741 inbound, 2912 outbound, 28 vitórias, 5 quedas. Fonte: `latest-whatsapp-historical.json` de 2026-05-25.

## Sinais operacionais
- Agendamento/confirmação: histórico reforça que confirmação estruturada com serviço, data, hora e três respostas literais aumenta confirmação: *Confirmo*, *Quero remarcar*, *Não vou conseguir*.
- Objeção/pesquisa: leads que chegam apenas pesquisando esfriam quando recebem pitch ou pedido de exame antes de contexto mínimo; a pergunta inicial deve descobrir objetivo principal antes de propor próximo passo.
- Silêncio/telemetria: o recorte atual mostra 20 inbound e 0 outbound. Se a fonte estiver completa, há risco de silêncio operacional e deve haver checagem humana de Z-API/runtime; se o relatório estiver capturando apenas inbound, é falha de telemetria a corrigir, não motivo para pausar Clara.
- Fora de escopo: apareceu busca de emprego/candidatura. Este fluxo não deve entrar no funil de paciente nem gerar pitch de tratamento.
- Serviços avulsos: apareceram perguntas sobre consulta com nutricionista e bioimpedância/InBody. Bioimpedância avulsa já tem regra operacional canônica no cérebro; valor de consulta nutricional avulsa não foi confirmado como regra canônica neste QA.
- Medicação controlada: apareceu menção informal a fórmula com substâncias controladas/psicoativas. Clara não deve discutir dosagem, combinação, disponibilidade ou prescrição no WhatsApp.

## Aprendizados operacionais novos ou reforçados

### 1. Candidatura/emprego deve sair do funil de agendamento
Quando a mensagem indicar emprego, vaga, oportunidade de trabalho, currículo, faxina, babá, cuidador(a) ou serviços gerais, Clara deve responder com acolhimento curto, informar que o canal é para pacientes/serviços IVS e direcionar para a rota administrativa/RH aprovada. Não inventar e-mail se não houver contato canônico. Classificação: aplicar amanhã após confirmar rota de RH/administrativo.

### 2. Pergunta de serviço avulso precisa de resposta curta + ponte segura para consulta/programa
Quando o lead perguntar preço de bioimpedância ou serviço isolado, Clara deve responder com o valor apenas se ele estiver no cérebro canônico. Para bioimpedância avulsa, usar a regra vigente. Para consulta nutricional avulsa, não inventar preço; acionar recepção/administração ou oferecer a avaliação completa se fizer sentido. Sempre fechar com uma pergunta objetiva de agenda: “Quer que eu veja os próximos horários?” Classificação: aplicar amanhã para bioimpedância; propor RC-25/decisão para tabela de serviços avulsos faltante.

### 3. Menção a medicamento controlado exige bloqueio clínico e conversão para avaliação
Quando o lead mencionar fórmula, dose, orlistat, fluoxetina ou outra medicação controlada/psicoativa, Clara não deve orientar dosagem nem confirmar prescrição. Resposta segura: “Essa definição precisa ser avaliada individualmente pela equipe. Posso te ajudar a agendar uma avaliação para analisarem seu caso com segurança?” Classificação: aplicar amanhã.

## 3 melhorias práticas para aumentar agendamentos sem violar guardrails
1. Implantar respostas de triagem para fora de escopo e paciente existente, evitando que Clara gaste turno com conversa que não agenda e preservando a rota humana correta.
2. Padronizar fechamento com pergunta objetiva após resposta de preço/serviço: valor canônico curto, uma frase de contexto e convite direto para ver horários.
3. Criar alerta operacional para janelas com inbound sem outbound: checar se é silêncio real da Clara ou limitação da planilha antes de qualquer intervenção, sem pausar a Clara sem ordem explícita de Tiaro.

## Risco operacional
Risco moderado a verificar: o relatório atual mostra 20 mensagens inbound, 9 leads e 0 outbound no período. Ação recomendada: validação humana leve dos logs Z-API/runtime para confirmar se Clara respondeu fora da planilha. Não há base para pausar Clara automaticamente.

## Guardrails
- Não diagnosticar, não prescrever, não interpretar exames e não prometer resultado.
- Não expor PII, telefones ou conversas sensíveis.
- Não pausar Clara sem ordem explícita de Tiaro.
- Preço só deve ser dito quando estiver confirmado em regra canônica vigente.
