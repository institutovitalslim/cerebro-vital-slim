# SPEC-CEOS-SOCIAL-SELLING-001: Produção por formato + BI social + busca ativa governada

## Goal
Separar a produção do Content Engine OS por formato e criar um módulo de Social Selling para transformar sinais públicos de interação no Instagram em oportunidades de conversa manual, segura e contextual.

## Agentes `ivs-data-dev-os` ativados
- Product Analyst IVS: dor = produção genérica/confusa e falta de módulo de captação ativa.
- Solution Architect IVS: Produção separada em Carrosséis, Estáticos, Reels e Stories; Social Selling em módulo próprio.
- Data Architect IVS: tabelas para métricas de perfil, publicação e interatores.
- Security/LGPD Guard IVS: handles/interações são dados de lead; sem automação, sem bulk, sem diagnóstico e sem promessa.
- Builder IVS: rotas API, páginas UI e smoke.
- QA/Bench Engineer IVS: build, compile, smoke e validação pública.
- Release Engineer IVS: restart dos containers.
- Executive Narrator IVS: reporte final com evidências.

## Produção
A seção Produção deve expor entradas separadas:
- `/producao/carrosseis`
- `/producao/estaticos`
- `/producao/reels`
- `/stories-engine`

O hub `/criar` vira seletor de formato.

## BI social
A seção BI deve mostrar, quando houver ingestão RapidAPI:
- seguidores;
- visitas ao perfil;
- cliques em WhatsApp;
- curtidas, comentários, salvamentos, compartilhamentos;
- follows atribuídos;
- pessoas/interatores mapeados;
- candidatos para abordagem manual.

## Social Selling
O módulo `/social-selling` deve responder:
1. quem interagiu com publicações públicas;
2. qual tipo de sinal deu;
3. em qual estágio de consciência está;
4. qual score de fit;
5. qual abertura manual sugerida;
6. quais guardrails bloqueiam abuso.

## Governança
- Não enviar DM automaticamente.
- Não fazer disparo em massa.
- Não diagnosticar.
- Não prometer resultado.
- Não oferecer preço sem contexto.
- Qualquer mensagem real exige ação humana e aprovação operacional.
- Ingestão via RapidAPI deve ser read-only e idempotente.

## Próxima fase
Criar job diário RapidAPI para popular:
- `instagram_profile_daily_metrics`
- `instagram_publication_daily_metrics`
- `social_selling_interactors`

Classificação inicial sugerida:
- comentário = maior intenção;
- salvamento/compartilhamento = interesse forte;
- follow/profile_click/whatsapp_click = intenção de relação;
- like isolado = sinal fraco.
