# QA diária Clara — máquina de agendamento — 2026-05-28 01:30 UTC

Origem sanitizada: relatórios `latest-whatsapp-current.json` e `latest-whatsapp-historical.json`.
PII: não registrada. Conversas sensíveis não transcritas.

## Leitura objetiva

### Janela atual — últimas 6h
- 52 mensagens inbound.
- 12 leads únicos.
- 0 outbound registrado no recorte.
- 0 wins e 0 drops no recorte.

Sinais principais:
- Leads entram com mensagens muito curtas: intenção, valor, local, horário ou resposta monossilábica.
- Gatilhos recorrentes de abertura: preço, endereço, convênio e disponibilidade.
- Objeção financeira aparece como adiamento, falta de cartão ou espera pelo início do mês.
- Há menções espontâneas de saúde/condição clínica; isso exige acolhimento e encaminhamento seguro, sem diagnóstico ou promessa.

### Histórico — 180 dias
- 5.653 mensagens analisadas.
- 372 leads únicos.
- 28 wins e 5 drops mapeados.

Padrões confirmados:
- Confirmação com CTA fechado aumenta resposta objetiva: `Confirmo`, `Quero remarcar`, `Não vou conseguir`.
- Leads em pesquisa reagem mal quando recebem empurrão precoce para consulta/exames.
- Saudações vagas precisam de direcionamento simples, não de discurso longo.
- Mensagens de pacientes existentes precisam ser triadas antes de script comercial.

## 3 melhorias práticas para aumentar agendamentos

1. **Primeira resposta curta e orientada a conversão.**
   Quando o lead vier com “quero”, “valor”, “onde fica”, “sim”, “manhã” ou similar, a Clara deve responder curto, entregar a informação necessária e fechar com uma pergunta operacional de agenda. Classificação: testar 3 dias.

2. **Objeção financeira vira reserva assistida, não encerramento.**
   Quando o lead disser que só consegue no início do mês, que está sem cartão ou que “depois entra em contato”, a Clara deve oferecer uma alternativa concreta de data futura/reserva de horário, sem pressionar e sem promessa comercial fora da política vigente. Classificação: testar 3 dias.

3. **Saúde/convênio/paciente existente entram em triagem segura.**
   Qualquer menção espontânea a condição de saúde, medicamento, convênio, nota fiscal, aplicação anterior, exames ou profissional do IVS deve acionar triagem: registrar contexto, não diagnosticar, não prescrever, e encaminhar para especialista/administração conforme o caso. Classificação: aplicar amanhã como reforço de guardrail já existente.

## Risco operacional

Risco **médio**: na janela atual há 52 inbound e 0 outbound no relatório. Isso pode ser lacuna de extração ou sinal de ausência de resposta da Clara no recorte. Exige verificação humana/técnica dos logs do WhatsApp/Z-API antes de qualquer conclusão.

Ação recomendada: checar bridge/runtime da Clara e amostragem de respostas sem pausar a Clara. Pausa só com ordem explícita do Tiaro.

## RC-25 / Graphify

Aprendizado operacional registrado como hipótese governada, não como mudança automática de regra clínica/financeira/jurídica. Promoção para regra canônica depende de validação operacional e RC-25 quando estrutural.
