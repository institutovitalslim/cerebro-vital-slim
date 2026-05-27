# RC-25 / Graphify — Manutenção diária 01:00 — Clara zero envios e health ponta a ponta

Data: 2026-05-27 01:00 UTC
Responsável: Maria, Gerente Geral IVS
Rotina: `cerebro/manutencao/ROTINA-DIARIA-0100.md`

## Consolidações revisadas

1. Logs `clara-whatsapp-learning` de 2026-05-26 mostram recorrência crítica: várias janelas com mensagens recebidas e **0 mensagens enviadas**.
2. Sinais comerciais recorrentes observados nas janelas: pergunta direta de valor/consulta, pergunta de agendamento, abertura vaga, lead em concorrente, objeção financeira, retorno futuro, janela de horário flexível e relato emocional/clínico denso.
3. As ações sugeridas pelos learnings não devem ser promovidas literalmente para runtime porque parte delas conflita com RC-38/RC-39/RC-40: origem/demanda é pista, abertura genérica pede descoberta mínima, preço exige contexto mínimo, e agenda não deve atropelar o entendimento real.
4. A consolidação estrutural permitida nesta rotina é de governança, painel, índice, ambiguidade e memória operacional; não houve contato com lead/paciente, envio de WhatsApp nem pausa da Clara.
5. Health ponta a ponta precisa diferenciar: serviço local indisponível, webhook sem processo, action_gate bloqueando, Z-API falhando, Clara pausada por ordem explícita, ou learning apenas read-only sem envio real.

## Decisão RC-25

- Promover o achado para painel/backlog e itens ambíguos como monitoramento HIGH/YELLOW.
- Promover linguagem recorrente para `INDEX-PEDIDOS-RECORRENTES.md` como auditoria de “0 enviadas”.
- Não alterar runtime/prompt da Clara nesta rotina.
- Não pausar Clara por iniciativa da Maria.

## Evidência sanitizada

- 2026-05-26: janelas analisadas com 8, 6, 43, 59, 55, 39, 23 e 21 mensagens; todas registraram `Enviadas: 0`.
- Admin local `http://127.0.0.1:8787/admin/status` não respondeu durante a manutenção; serviço local com nome `clara-zapi-bridge.service` não encontrado no host consultado. Isso é achado técnico local e não prova, sozinho, queda definitiva de produção.
