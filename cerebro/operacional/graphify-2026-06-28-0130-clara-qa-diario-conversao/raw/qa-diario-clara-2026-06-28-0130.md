# QA diário Clara — conversão/agendamento — 2026-06-28 01:30 UTC

## Escopo
Análise sanitizada dos relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json` para avaliar a Clara como máquina de agendamento, sem expor PII, telefones ou conversas sensíveis.

## Fontes consultadas
- `latest-whatsapp-current.json`: WhatsApp IVS via planilha de conversas, modo current, últimas 6h, gerado em 2026-06-28 01:15 UTC.
- `latest-whatsapp-historical.json`: WhatsApp IVS via planilha de conversas, modo historical, últimos 180 dias, gerado em 2026-06-24 10:23 UTC.
- GBrain/arquivo canônico consultado antes da resposta: registros anteriores de QA diário Clara e resolver canônico do cérebro.

## Evidências sanitizadas
- Relatório current: 0 mensagens, 0 leads únicos, 0 inbound, 0 outbound, 0 wins e 0 drops nas últimas 6h.
- Relatório historical: 6187 mensagens, 443 leads únicos, 3275 inbound, 2912 outbound, 30 sinais de vitória/agendamento e 5 sinais de queda/objeção.
- Taxa histórica simples de wins sobre leads únicos: aproximadamente 6,8% (30/443), leitura apenas direcional porque os dados misturam contextos comerciais e administrativos.

## Sinais de agendamento
- Confirmação estruturada com nome, procedimento, dia/hora e opções fechadas tende a gerar resposta objetiva de confirmação.
- A agenda funciona melhor quando Clara reduz ambiguidade e conduz para uma escolha operacional clara, em vez de prolongar conversa sem próximo passo.
- Leads com intenção mínima precisam de encaminhamento rápido para área/interesse antes de qualquer detalhamento longo.

## Sinais de objeção ou queda
- Lead frio que pede informação genérica tende a rejeitar quando recebe venda direta, oferta de explicação de consulta ou convite prematuro para marcar.
- Perguntas abertas do tipo “como posso ajudar?” em entrada genérica de anúncio deixam o lead com esforço alto e podem aumentar recusa.
- Demandas administrativas misturadas ao fluxo comercial não devem receber cadência de venda; precisam de triagem e encaminhamento administrativo.

## Sinais de silêncio / observabilidade
- O current veio zerado novamente. Como já houve recorrência desse padrão em QAs anteriores, a ausência de mensagens nas últimas 6h não deve ser interpretada sozinha como ausência real de demanda.
- A leitura mais segura é: sem evidência recente de conversa; manter análise apoiada no histórico e tratar o pipeline current como ponto de atenção técnico.

## Melhorias práticas para aumentar agendamentos sem violar guardrails clínicos
1. **Entrada genérica de anúncio = triagem por área antes de venda.** Para mensagens genéricas de interesse no Instituto, Clara deve responder com áreas objetivas — emagrecimento, aplicações, tricologia ou nutrição — e pedir a escolha do lead antes de explicar consulta ou ofertar agenda.
2. **Confirmação padronizada com opções literais.** Em confirmações de consulta/procedimento, manter bloco único com atendimento, data, horário e três respostas possíveis: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
3. **Desvio administrativo imediato.** Se aparecer pedido de nota fiscal, prontuário, boleto, link ou documento, Clara deve interromper fluxo comercial e encaminhar para administrativo, evitando ruído de venda e preservando experiência premium.

## Risco operacional
Há risco operacional moderado que exige validação humana/técnica, mas não pausa da Clara: o relatório current segue zerado e limita a QA de performance recente. Ação recomendada: validar captura da planilha/WhatsApp, Z-API/bridge e cron do `whatsapp-current`.

Não há evidência, nesta QA, de risco clínico/compliance que exija intervenção humana imediata em conversa específica. Sem ordem expressa do Tiaro, Clara não deve ser pausada.

## Aprendizado operacional novo registrado
- Lead frio/genérico de anúncio deve ser qualificado por área de interesse antes de receber venda direta ou convite de agenda.
- Demandas administrativas dentro do canal da Clara devem ser detectadas por palavras-chave e encaminhadas, não tratadas como lead comercial.
- A sequência recorrente de `current` zerado permanece como risco de observabilidade e deve ser acompanhada até validação técnica.

## Classificação do aprendizado
- **Aplicar amanhã:** melhorias 1, 2 e 3 como ajuste seguro de linguagem/roteamento.
- **Testar 3 dias:** medir resposta de leads genéricos quando a primeira mensagem é triagem por área versus explicação/convite direto.
- **Intervenção humana:** validação técnica do pipeline current se o zero persistir.
