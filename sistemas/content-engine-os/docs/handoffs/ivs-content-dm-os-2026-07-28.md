# Handoff para Claude Main — IVS Content DM OS

**Data:** 2026-07-28

**Origem:** Maria, Gerente Geral IVS

**Destino:** Claude Main, responsável atual pelo Content Engine OS

**Status:** novo módulo em desenvolvimento, sem integração produtiva e sem credenciais Meta

## 1. Decisão do Tiaro

Tiaro autorizou clonar integralmente e evoluir o OpenReply para criar o sistema próprio de respostas a comentários e DMs do IVS dentro do ecossistema Content OS.

A implementação está sendo feita em **repositório independente** para respeitar o `BUILD_LOCK.md` do Content Engine OS e evitar concorrência de escrita no código sob responsabilidade do Claude Main.

## 2. Repositório e origem

- Repositório local isolado: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os`
- Upstream preservado: `https://github.com/diwenne/openreply.git`
- Branch de evolução IVS: `ivs/main`
- Baseline clonado: 100 commits e 157 arquivos rastreados
- Design aprovado: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os/docs/superpowers/specs/2026-07-28-ivs-content-dm-os-design.md`

O repositório privado IVS e a URL definitiva serão adicionados a este documento quando a primeira fase passar por testes, build e auditoria.

## 3. Papel no ecossistema

O **IVS Content DM OS** fecha o ciclo entre conteúdo publicado e intenção recebida:

```text
conteúdo do Content OS
  → publicação/reel
  → comentário com palavra-chave
  → DM automática pela API oficial da Meta
  → link rastreado
  → lead útil
  → agendamento
  → aprendizado de performance volta ao Content OS
```

Não substitui a Clara. O Instagram permanece sob domínio de Marketing; Clara só entra quando o usuário voluntariamente migra para o WhatsApp.

## 4. Capacidades planejadas

### Fase 1 — Fundação segura

- clone integral e preservação do upstream;
- correção de CI, testes e build;
- atualização de dependências críticas;
- autenticação, tenant isolation e health seguro;
- retenção LGPD e expurgo auditável;
- contrato de integração Content OS v1 em dry-run.

### Fase 2 — Comment-to-DM

- campanhas ligadas a posts/Reels;
- palavras-chave exatas ou parciais;
- DM automática e resposta pública opcional;
- tracked links e atribuição;
- rate limit, retries, deduplicação e logs por reason code.

### Fase 3 — Inbox e handoff

- leitura e resposta de DMs dentro da janela permitida pela Meta;
- templates aprovados;
- classificação de intenção;
- handoff humano;
- trilha de auditoria e kill switch por conta/campanha.

### Fase 4 — Performance no Content OS

- métricas por peça de conteúdo;
- ranking de hook, CTA, palavra-chave e formato;
- aprendizado para BI e Sprint Semanal;
- foco em lead útil/agendamento, não apenas CTR.

## 5. Contrato recomendado para o Claude Main

### Identificadores canônicos

Toda campanha criada a partir do Content OS deve transportar:

- `tenant_id`
- `content_id`
- `campaign_id`
- `origin_tag`
- `schema_version = "content-dm-os/v1"`

### Content OS → Content DM OS

Contrato pretendido:

```http
POST /api/integrations/content-os/v1/campaigns
Authorization: Bearer <service-token>
Idempotency-Key: <uuid>
Content-Type: application/json
```

Payload mínimo:

```json
{
  "schema_version": "content-dm-os/v1",
  "tenant_id": "ivs",
  "content_id": "<id interno do Content OS>",
  "campaign_id": "<id estável>",
  "origin_tag": "reel|post|story",
  "mode": "dry_run",
  "keywords": ["GUIA"],
  "dm_template": "<template aprovado>",
  "destination_url": "https://<dominio-institucional>/..."
}
```

**Default obrigatório:** `mode=dry_run`. Ativação real exige credencial Meta, permissão e gate operacional.

### Content DM OS → Content OS

Eventos agregados e sanitizados:

- `comment_matched`
- `dm_queued`
- `dm_sent`
- `dm_failed`
- `tracked_link_clicked`
- `handoff_requested`

Envelope recomendado:

```json
{
  "schema_version": "content-dm-os/v1",
  "event_id": "<uuid>",
  "event_type": "dm_sent",
  "occurred_at": "<ISO-8601 UTC>",
  "tenant_id": "ivs",
  "content_id": "<id interno>",
  "campaign_id": "<id estável>",
  "metrics": {
    "count": 1
  }
}
```

Não transportar ao Content OS:

- texto integral de comentários ou DMs;
- Instagram user ID, username ou avatar;
- telefone, e-mail ou qualquer PII;
- access tokens ou refresh tokens;
- dados clínicos.

### Segurança do contrato

- HTTPS obrigatório;
- assinatura HMAC ou service token dedicado;
- idempotência por `event_id`/`Idempotency-Key`;
- allowlist entre serviços;
- timeout curto, retry com backoff e fila morta;
- falha da integração nunca pode provocar DM duplicada;
- segredos apenas no cofre/ambiente, nunca no repositório.

## 6. Alterações esperadas no Content Engine OS

Quando o Claude Main decidir incluir o módulo, a abordagem recomendada é:

1. Criar uma seção **DM & Conversão** no painel, sem incorporar o runtime do worker ao monólito.
2. Persistir apenas IDs e métricas agregadas do Content DM OS.
3. Adicionar ao modelo de conteúdo os campos opcionais:
   - `dm_campaign_id`
   - `dm_keyword`
   - `dm_cta_variant`
   - `dm_destination_url`
   - `dm_campaign_status`
4. Exibir no detalhe da peça:
   - comentários compatíveis;
   - DMs enfileiradas/enviadas/falhas;
   - cliques;
   - leads úteis;
   - agendamentos atribuídos.
5. Não permitir publicação ou envio direto sem o gate humano já existente no Content OS.
6. Tratar o Content DM OS como serviço dependente, com estado `healthy | degraded | offline`.

## 7. Baseline técnico encontrado

No clone original, antes das correções:

- `npm ci`: concluído;
- testes: **88/95 passam e 7 falham**;
- causa inicial das sete falhas: mock de `prisma.dmLog.create` ausente/desatualizado na suíte do worker;
- lint: verde;
- typecheck inicial: depende de `prisma generate` e apresenta erros quando o client ainda não foi gerado;
- auditoria completa: **17 vulnerabilidades**, sendo 2 críticas, 9 altas, 4 moderadas e 2 baixas.

Portanto, o código ainda não deve ser conectado à conta oficial nem publicado em produção.

## 8. Guardrails soberanos

- Sem conexão da conta oficial do Instagram nesta fase.
- Sem envio real de DM ou comentário.
- Sem alteração do Content Engine OS por Maria/João enquanto o `BUILD_LOCK.md` estiver ativo.
- Sem escrita em WhatsApp/Z-API, QuarkClinic, Omie ou dados clínicos.
- Sem PII em eventos de integração.
- O Claude Main mantém autoridade sobre arquitetura e código do Content Engine OS.

## 9. Próxima ação do Claude Main

Ao retomar o Content Engine OS:

1. Ler este handoff.
2. Reservar no modelo de domínio os IDs e métricas descritos na seção 6.
3. Definir o endpoint interno que receberá eventos sanitizados.
4. Manter a interface em estado `coming soon` ou feature flag até o Content DM OS passar pelos gates.
5. Registrar qualquer divergência de contrato em novo documento de decisão, sem editar diretamente o runtime do Content DM OS.

## 10. Evidências

- Novo clone: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os`
- Design aprovado: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os/docs/superpowers/specs/2026-07-28-ivs-content-dm-os-design.md`
- Análise executiva: `/root/.hermes/maria-workspace/relatorios/openreply-repo-analysis-2026-07-28.html`
- Este handoff: `docs/handoffs/ivs-content-dm-os-2026-07-28.md`
