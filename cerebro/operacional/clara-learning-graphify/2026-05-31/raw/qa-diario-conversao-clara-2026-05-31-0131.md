# QA diário de conversão da Clara — 2026-05-31 01:31 UTC

## Escopo
Revisão objetiva da Clara como máquina de agendamento, usando os relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json`. Documento sanitizado: não inclui PII, telefones nem transcrição sensível.

## Evidências agregadas

### Janela atual — últimas 6h
- Mensagens analisadas: 21.
- Conversas/leads únicos: 6.
- Entradas recebidas: 21.
- Saídas/enviadas registradas: 0.
- Sinais de agendamento/vitória: 0.
- Sinais de queda/objeção: 0.

### Histórico — últimos 180 dias
- Mensagens analisadas: 5.653.
- Conversas/leads únicos: 372.
- Entradas recebidas: 2.741.
- Saídas/enviadas: 2.912.
- Sinais de agendamento/vitória: 28.
- Sinais de queda/objeção: 5.

## Sinais observados
- Agendamento: nenhum sinal novo na janela atual; histórico mostra vitórias quando confirmação é estruturada e com CTA fechado.
- Objeção: na janela atual não houve queda marcada, mas o padrão recorrente de preço/parcelamento permanece relevante no histórico e nos aprendizados recentes.
- Silêncio/risco de continuidade: há 21 mensagens recebidas e 0 enviadas nas últimas 6h. O endpoint local `/admin/status` respondeu `paused=false`, portanto o risco não é pausa formal, e sim falha/latência/ponte de envio, captura incompleta de outbound ou bloqueio por overrides/fila.

## 3 melhorias práticas para aumentar agendamentos sem violar guardrails clínicos

1. **Responder primeiro a dor emocional, depois conduzir para objetivo e próxima etapa.**
   - Quando o lead vier com baixa autoestima, cansaço ou frustração, a Clara deve validar a dor em uma frase curta e em seguida fazer pergunta objetiva de triagem comercial.
   - Guardrail: não diagnosticar, não prometer resultado e não prescrever.

2. **Tratar histórico de dietas/academia sem culpar o lead.**
   - Reposicionar tentativa frustrada como falta de acompanhamento adequado, abrindo caminho para consulta/avaliação sem usar linguagem de promessa.
   - Objetivo de conversão: reduzir vergonha e aumentar disposição para aceitar avaliação.

3. **Antecipar forma de pagamento sem inventar condição.**
   - Quando chegar em investimento/valor, apresentar que existem condições e parcelamento disponíveis, mas sem declarar número de parcelas ou valor específico se a regra vigente não estiver confirmada.
   - Objetivo de conversão: evitar drop por preço antes de explorar agenda/avaliação.

## Classificação do aprendizado
- Status: **testar 3 dias**.
- Não promover automaticamente para regra canônica ou alteração de runtime.
- Métrica de aceite: aumento de conversas com próximo passo explícito de agenda/avaliação e queda do volume de conversas sem resposta registrada.

## Risco operacional e intervenção humana
- Risco: **SIM, exige checagem humana/técnica**, porque a janela atual mostra múltiplas mensagens recebidas e zero enviadas, mesmo com Clara não pausada no status local.
- Intervenção recomendada: validar ponte WhatsApp/Z-API, worker de envio, planilha de captura de outbound e overrides ativos antes do início do expediente. Não pausar Clara sem ordem explícita do Tiaro.
