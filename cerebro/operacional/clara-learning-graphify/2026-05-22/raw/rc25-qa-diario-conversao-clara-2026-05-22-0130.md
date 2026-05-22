# RC-25 — QA diário de conversão Clara — 2026-05-22 01:30 UTC

Status: aprendizado operacional registrado via Graphify/RC-25.
Origem: relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` da rotina Clara Learning.
Escopo: máquina de agendamento Clara WhatsApp. Sem PII, sem telefones, sem transcrição sensível.

## Evidências sem PII

- Janela atual: 6 mensagens inbound, 2 leads únicos, 0 mensagens outbound, 0 vitórias, 0 quedas classificadas.
- Sinal operacional crítico: ausência total de resposta da Clara na janela atual.
- Sinais de conversão observados no histórico: confirmações funcionam melhor com três opções curtas e estruturadas; textos explicativos longos antes do agendamento aumentam drop; perguntas abertas em lead frio geram rejeição; imprevistos precisam de remarcação concreta.
- Sinal de objeção/silêncio atual: lead mencionou falta de previsão/ordem de chegada e intenção de desmarcar; outro caso iniciou com mensagem vaga e não recebeu condução.

## Decisão operacional

Classificação: aplicar amanhã + intervenção humana operacional.

Não é mudança clínica, financeira ou jurídica. Não autoriza diagnóstico, prescrição, promessa de resultado nem contato por Maria com lead/paciente. Não autoriza pausa da Clara.

## Aprendizados práticos para Clara

1. SLA de primeira resposta: toda mensagem inbound nova precisa resposta inicial objetiva em até 5 minutos, mesmo quando a abertura for vaga.
2. Abertura vaga deve virar pergunta fechada de intenção: agendar, remarcar ou tirar dúvida; evitar “como posso ajudar?” genérico em lead frio.
3. Objeção de espera/sem previsão deve acionar recuperação imediata: oferecer checar horário de atendimento ou remarcar com duas janelas concretas.

## Risco operacional

Risco amarelo/alto: 0 outbound em 6 inbound sugere falha de execução, integração, roteamento, pausa, rate limit ou bloqueio operacional. Requer verificação humana do runtime/logs da Clara antes do próximo horário comercial.

Próxima ação recomendada: responsável técnico/admin verificar se Clara está ativa, se a ponte WhatsApp/Z-API está entregando mensagens e se existe fila acumulada sem resposta. Não pausar Clara sem ordem explícita do Tiaro.
