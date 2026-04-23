# Apps Script `zapi-webhook` — investigação de latência

> Aberto em 2026-04-23 pelo Claude remoto após Tiaro reportar que a Clara não estava respondendo pacientes novos no WhatsApp. Hipótese inicial confirmada como falsa (Clara voltou a responder normal), **mas a latência detectada é real e fica como risco latente**.

## Endpoint
- URL canônica: `https://script.google.com/macros/s/AKfycbxmLLmzLtjnmQwBNxPTaCwNEBtbcez3qvz78C5X2dxV1w5CK4R6j-Ky-1CXtvfU-3Hy7Q/exec`
- Identifica-se como `{"ok":true,"service":"zapi-webhook","mode":"health"}` — é o **mesmo endpoint** que recebe webhook da Z-API (POST) e responde queries de histórico (GET com `phone=`).
- Documentado em `cerebro/CLAUDE.md` seção "Rotina obrigatória — Consulta ao histórico de conversas".

## Medições (2026-04-23, 23:30 BRT, do sandbox GitHub via HTTPS)

| Request | HTTP | Latência |
|---------|------|----------|
| GET `/exec` (sem params, modo health) | 200 | **17,8 s** |
| GET `/exec` retry (sem cold start) | 200 | **17,4 s** |
| GET `/exec?phone=...` (lookup típico) | 200 | 6,7 s |
| GET `/exec?mode=history&phone=...` | 200 | 8,6 s |
| GET `/exec?mode=lookup&phone=...` | 200 | 7,4 s |
| GET `/exec?mode=messages&phone=...` | 200 | 2,4 s |

**Esperado**: `/health` < 2 s, lookup < 3 s.
**Observado**: 5–10× mais lento.

## Por que isso é risco

- **Z-API tem timeout de webhook tipicamente 5–15 s**. Se o endpoint demora 17 s pra responder até `/health`, o webhook POST de mensagem nova pode timeoutar antes do Apps Script processar — **mensagem do paciente é perdida silenciosamente** (Z-API pode tentar retry, mas se a quota do Apps Script estiver baixa, vai falhar de novo).
- A regra do `cerebro/CLAUDE.md` manda Clara **parar e notificar Tiaro** quando não consegue consultar histórico. Se o lookup de phone ficar timing-out, Clara pode entrar em modo "silêncio defensivo" pra leads novos — exatamente o sintoma que Tiaro reportou hoje (mesmo que a causa imediata tenha sido outra).

## Próximos passos (precisa de Tiaro com acesso ao Apps Script)

1. Abrir `script.google.com` → projeto `zapi-webhook` (ou nome que estiver) → **Executions** das últimas 24 h
2. Procurar:
   - Erros recorrentes (em vermelho)
   - Execuções que demoram > 30 s
   - Mensagens de quota: `Service invoked too many times`, `Exceeded maximum execution time`
3. Verificar **quotas** do Apps Script (`Apps Script Dashboard → Quotas`):
   - Free tier: 6 h/dia de runtime, 20.000 chamadas/dia, 90 min/dia de URL fetch
   - Conta Workspace: 6 h/dia, 100.000 chamadas/dia, 6 h/dia de URL fetch
4. Se quota próxima do limite: investigar o que tá consumindo (provavelmente loop de retry de webhook ou leitura excessiva da planilha)
5. Se sem quota mas ainda lento: revisar código do script — leitura de planilha grande sem paginação, chamadas sequenciais que poderiam ser batch, etc.

## Mitigação imediata possível
- **Mover o webhook Z-API direto pro VPS** (`localhost:8787` da bridge da Z-API), tirar o Apps Script do caminho crítico de entrega. Apps Script fica só pro logging/histórico, async.
- Isso elimina o ponto de falha mais sensível. Hoje o Apps Script é simultaneamente webhook entrega e fonte de histórico — quando ele engasga, todo o fluxo trava.

## Status
- ⏳ **Não diagnosticado a fundo** — depende de Tiaro abrir o painel do Apps Script
- ✅ Latência confirmada (medida externamente, não suposição)
- ✅ Risco documentado para próximo agente que tocar nesse fluxo

_Aberto em 2026-04-23 por Claude (sandbox GitHub) na branch `claude/connect-openclaw-brain-JNF6Q` (mergeada via PR #1)._
