# QA diário Clara — conversão/agendamento — 2026-06-26 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou trechos sensíveis.

## Evidências sanitizadas
- Relatório current: últimas 6h, gerado em 2026-06-26 01:15 UTC, com 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins e 0 drops.
- Relatório histórico disponível: últimos 180 dias, gerado em 2026-06-24 10:23 UTC, com 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Sinais de agendamento no histórico: confirmações objetivas melhoram quando a mensagem contém nome, procedimento, dia/hora e opções fechadas de resposta: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
- Sinais de objeção/queda no histórico: em leads frios ou genéricos, oferta de agendamento/explicação de consulta logo na primeira resposta tende a gerar respostas de adiamento como “por enquanto não”.
- Entrada padronizada de anúncios: pedidos genéricos sobre o Instituto Vital Slim precisam de triagem por área de interesse antes da tentativa de agendamento.
- Ruído operacional: demandas administrativas aparecem misturadas a leads e devem sair do fluxo comercial para encaminhamento administrativo.
- Sinal de silêncio/observabilidade: o current permanece zerado, mantendo bloqueio de leitura recente; a QA de hoje não consegue inferir performance atual da Clara, apenas padrões históricos.

## Aprendizado operacional novo
O aprendizado incremental hoje vem do histórico atualizado: separar lead frio de lead com intenção clara. Para lead frio, a Clara deve primeiro direcionar por área de interesse; para lead com intenção ou agendamento já existente, deve usar confirmação fechada com opções padronizadas. Demandas administrativas devem ser desviadas do fluxo comercial.

## Melhorias práticas para Clara
1. **Triagem antes de vender para lead frio:** quando a entrada for genérica (“quero informações” ou equivalente), perguntar a área de interesse — emagrecimento, aplicações, tricologia ou nutrição — antes de oferecer consulta ou explicar detalhes.
2. **Confirmação fechada para reduzir silêncio:** em consulta/aplicação já encaminhada, confirmar nome, atendimento, dia e horário, pedindo resposta literal entre `Confirmo`, `Quero remarcar` ou `Não vou conseguir`.
3. **Desvio administrativo imediato:** mensagens sobre nota fiscal, boleto, prontuário, reenvio de link ou documentos devem sair do roteiro comercial e ser encaminhadas ao administrativo, sem insistir em agenda.

## Risco operacional
Há risco operacional que exige intervenção humana/técnica, mas não pausa da Clara: o relatório current segue zerado e impede QA recente confiável. Ação recomendada: validar captura WhatsApp, planilha, Z-API/bridge e cron. Sem ordem direta do Tiaro, Clara não deve ser pausada.

## Guardrails
Nenhuma melhoria autoriza diagnóstico, prescrição, promessa de resultado, pressão comercial agressiva ou atendimento clínico. O foco é reduzir atrito de agenda, melhorar triagem segura e proteger a operação de ruído administrativo.

## Classificação
- Aplicar amanhã: melhorias 1, 2 e 3 como hipótese operacional segura.
- Testar 3 dias: medir resposta de leads frios triados por área versus leads com oferta direta de agenda.
- Intervenção humana: manter validação técnica do pipeline current como pendência operacional ativa.
