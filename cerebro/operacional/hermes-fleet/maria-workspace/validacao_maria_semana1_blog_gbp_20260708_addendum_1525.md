# Validação Maria — addendum Semana 1 Blog IVS / GBP
Data: 2026-07-08 15:25 BRT
Responsável: Maria Gerente
Correlação: semana1-blog-gbp-publicacao-final-20260708

## Evidências analisadas
- João: `/opt/ivs/blog-scientific-authority/data/visibility_30d_20260630/semana1_pecas_finais_joao_20260702/resposta_final_maria_iam-20260708-152130-8edfb3bfa8b2.md`
- João: `/opt/ivs/blog-scientific-authority/data/visibility_30d_20260630/semana1_pecas_finais_joao_20260702/evidencia_final_out001_out004_pacote_revisado_20260708_151753.md`
- Jarvis: `/root/.hermes/profiles/jarvis/workspace/gbp_julho_2026_execucao_20260708.md`

## Decisão por item — João

### OUT-001 — Google Business Profile
Status Maria: `BLOCKED_TECNICO_ACEITO` para execução pelo João nesta rodada.

Evidência aceita: runtime do João sem CLI/canal/credencial operacional de GBP (`gws`, `google-business-profile`, `gbp` ausentes; envs `GOOGLE_BUSINESS/GBP/GMB` ausentes). Não há URL/print/status porque não houve acesso real de publicação.

Próximo passo: destravar canal oficial/credencial/ferramenta ou execução humana; depois registrar URL pública, print/status ou log/API real.

### OUT-004 — Facebook Page IVS
Status Maria: `BLOCKED_TECNICO_ACEITO` para execução pelo João nesta rodada.

Evidência aceita: runtime do João sem CLI/canal/credencial operacional Facebook/Meta (`facebook-cli`, `meta`, `social-scheduler`, `buffer` ausentes; envs `FACEBOOK/META` ausentes). Além disso, Tiaro definiu que Facebook/Instagram devem entrar pelo Content OS com aprovação final antes de publicar.

Próximo passo: cadastrar/processar no Content OS quando houver brief/canal operacional e manter gate de aprovação do Tiaro; após publicação, registrar URL/print/status.

### OUT-005 — Instagram Bio/Highlights/Reels/Stories
Status Maria: `APROVADO_PARA_CONTENT_OS_TIARO`.

Validação: pacote revisado agora contém roteiros falados, textos em tela/slides, legendas, links/UTMs e disclaimer educativo. Linguagem está em tom educativo, sem promessa de resultado, sem diagnóstico/prescrição e sem antes/depois/depoimento.

Gate: aprovado apenas para seguir ao Content OS e aprovação final do Tiaro. Não autoriza publicação direta nem contato externo.

### OUT-016 — Academias premium
Status Maria: `PARCIAL_APROVADO_COM_BLOCKER_DE_LISTA`.

Validação: copy/canal/responsável/UTM estão adequados para validação interna. Lista nominal parcial recebida: Power Fit Academia; Acadêmia de mulheres. Ainda falta lista-base completa/aprovada ou canal de pesquisa oficial antes de qualquer outreach.

Gate: nenhum contato externo autorizado.

### OUT-017 — Pilates/fisioterapia
Status Maria: `BLOCKED_LISTA`.

Validação: copy/canal/responsável/UTM estão adequados para validação interna, mas lista nominal segue bloqueada por 0 resultados úteis/timeout nas fontes usadas por João.

Próximo passo: Tiaro/Maria liberar lista-base aprovada ou canal oficial de pesquisa. Nenhum contato externo autorizado.

### OUT-018 — Nutricionistas parceiras
Status Maria: `BLOCKED_LISTA`.

Validação: copy/canal/responsável/UTM estão adequados para validação interna, mas lista nominal segue bloqueada por 0 resultados úteis/ausência de base aprovada.

Próximo passo: Tiaro/Maria liberar lista-base aprovada ou canal oficial de pesquisa. Nenhum contato externo autorizado.

## Decisão por item — Jarvis GBP
Status Maria: `BLOCKED_AUTH_GBP_ACEITO` para os 7 posts.

Evidência aceita: `business.google.com/locations` segue em tela de login; conta autenticada disponível não é a rota GBP/local posts esperada; runtime sem variáveis `GBP/MYBUSINESS/GMB`; `gog-ivs` sem comando GBP/local posts. Itens 1 a 7 permanecem sem URL pública/status externo por falta de acesso real ao painel/API.

Próximo passo: liberar sessão autenticada do Google Business Profile na conta/localização correta ou rota/API governada validada. Depois Jarvis publica/programa os 7 itens e devolve URL/print/status por item.

## Guardrail final
- Nada publicado por Maria.
- Nenhum contato externo feito.
- ACK não conclui; somente evidência externa final ou blocker objetivo com próximo passo.
