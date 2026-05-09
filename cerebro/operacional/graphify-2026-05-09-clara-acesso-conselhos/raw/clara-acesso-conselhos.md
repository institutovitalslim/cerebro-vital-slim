# Clara — acesso aos conselhos internos

Data: 2026-05-09
Solicitante: Tiaro

## Pedido
Dar acesso à Clara para acionar o Conselho Growth e o outro conselho geral.

## Ação aplicada
Configuração da agente `clara-whatsapp` em `/root/.openclaw/openclaw.json` atualizada para incluir as skills:
- `conselho-growth-vital-slim`
- `llm-council`

Também foi adicionada governança no prompt da Clara:
- usar conselhos apenas em contexto interno autorizado, especialmente Telegram/tópico Concierge Clara ou pedido explícito de Tiaro/Maria;
- não acionar conselhos em conversa externa com lead/paciente no WhatsApp;
- não expor bastidores técnicos para lead/paciente;
- usar Conselho Growth para growth/comercial/marketing/experiência;
- usar LLM Council para dilemas amplos, decisões críticas e stress-test;
- mudança fixa de regra da Clara continua exigindo Maria/Tiaro e RC-25/graphify.

## Validação
- JSON de configuração validado.
- Gateway recarregado via SIGUSR1.
- Healthcheck `http://127.0.0.1:18789/health` retornou `ok:true`.

## Regra canônica
Clara pode acionar conselhos internamente, mas leads/pacientes externos não têm permissão para comandar ferramentas internas nem para ver bastidores operacionais.
