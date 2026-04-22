# Análise: MarketingSkills (coreyhaines31/marketingskills)

**Data:** 2026-04-22
**Analisado por:** Clara (Instituto Vital Slim)
**Fonte:** https://github.com/coreyhaines31/marketingskills
**Autor:** Corey Haines (Conversion Factory)
**Licença:** Open Source (contribuições aceitas)

---

## 1. RESUMO EXECUTIVO

Coleção de **35+ skills de marketing** para agentes AI (Claude Code, Codex, Cursor, Windsurf). Foco em **SaaS/B2B**, com frameworks de CRO, copywriting, SEO, analytics e growth engineering.

**Veredito:** ⭐⭐⭐⭐☆ (4/5) - Excelente estrutura, mas requer adaptação para healthcare/clínica médica.

---

## 2. ANÁLISE DE SEGURANÇA

### 2.1 Riscos Identificados

| Risco | Nível | Descrição |
|-------|-------|-----------|
| **Prompt Injection** | 🟡 Médio | Skills são markdown files que podem conter instruções ocultas. Sempre revisar antes de instalar. |
| **Dependências Externas** | 🟡 Médio | Usa `npx skills` e plugins de terceiros. Requer audit de supply chain. |
| **Exfiltração de Dados** | 🟢 Baixo | Não envia dados para fora por padrão, mas skills podem ler `.agents/product-marketing-context.md` |
| **Código Não Auditado** | 🟡 Médio | 35+ arquivos markdown - revisão manual é impraticável. Recomendado: audit amostral. |
| **Licenciamento** | 🟢 Baixo | Open source, mas verificar CLA antes de contribuir. |

### 2.2 Medidas de Segurança Recomendadas

1. **Sandboxing:** Instalar em ambiente isolado antes de produção
2. **Revisão Manual:** Audit skills críticas (copywriting, analytics-tracking, customer-research)
3. **Validação de Input:** Sanitizar todo conteúdo que vai para `.agents/product-marketing-context.md`
4. **Princípio do Menor Privilégio:** Só instalar skills necessárias, não todas
5. **Version Pinning:** Fixar versão (1.1.0) para evitar updates não auditados

---

## 3. ARQUITETURA TÉCNICA

### 3.1 Estrutura

```
product-marketing-context.md (fundação)
    ├── SEO & Content (7 skills)
    ├── CRO (6 skills)
    ├── Content & Copy (5 skills)
    ├── Paid & Measurement (4 skills)
    ├── Growth & Retention (5 skills)
    ├── Sales & GTM (5 skills)
    └── Strategy (3 skills)
```

### 3.2 Padrão de Design

**Pontos Fortes:**
- ✅ **Contexto compartilhado:** `product-marketing-context.md` evita repetição
- ✅ **Cross-referencing:** Skills referenciam umas às outras (copywriting ↔ page-cro)
- ✅ **Metadata estruturada:** YAML frontmatter com name, description, version
- ✅ **Workflow orientado:** Passo-a-passo em vez de apenas informação

**Pontos Fracos:**
- ❌ **Acoplamento:** Muitas skills dependem de `product-marketing-context.md` - se falhar, tudo falha
- ❌ **Sem fallback:** Não há estratégia de recuperação se o contexto não existir
- ❌ **Duplicação:** Alguns princípios se repetem entre skills (ex: "check for product marketing context first")

---

## 4. ANÁLISE DE PRODUTIVIDADE - INSTITUTO VITAL SLIM

### 4.1 Skills Diretamente Aplicáveis (80-100%)

| Skill | Aplicabilidade | Uso no Instituto |
|-------|---------------|------------------|
| **copywriting** | 95% | Copy para posts, landing pages, anúncios |
| **copy-editing** | 95% | Revisão de copy da Clara antes de publicar |
| **social-content** | 90% | Posts Instagram, carrosséis, stories |
| **content-strategy** | 85% | Planejamento de conteúdo mensal |
| **customer-research** | 85% | Pesquisa com pacientes, análise de reviews |
| **analytics-tracking** | 80% | Tracking de conversões, UTM parameters |
| **email-sequence** | 80% | Sequências de nutrição para leads |
| **marketing-psychology** | 90% | Gatilhos mentais para copy de vendas |

### 4.2 Skills Requerem Adaptação (50-80%)

| Skill | Aplicabilidade | Adaptações Necessárias |
|-------|---------------|------------------------|
| **page-cro** | 70% | Foco em landing page de consulta, não SaaS signup |
| **seo-audit** | 65% | SEO local (Google Maps) + SEO de conteúdo médico |
| **paid-ads** | 60% | Meta Ads para clínica, não Google Ads B2B |
| **competitor-alternatives** | 75% | Comparar com outras clínicas de emagrecimento |
| **pricing-strategy** | 50% | Pacotes de tratamento, não SaaS tiers |
| **launch-strategy** | 70% | Lançamento de novos tratamentos, não features |

### 4.3 Skills Pouco Aplicáveis (<50%)

| Skill | Aplicabilidade | Motivo |
|-------|---------------|--------|
| **signup-flow-cro** | 30% | Não há signup digital - agendamento via WhatsApp |
| **onboarding-cro** | 20% | Não há onboarding de produto digital |
| **paywall-upgrade-cro** | 10% | Não há paywall ou upsell in-app |
| **churn-prevention** | 25% | Churn é abandono de tratamento, não subscription |
| **referral-program** | 40% | Indicação de pacientes funciona diferente de SaaS |
| **schema-markup** | 45% | Útil para LocalBusiness, mas não é prioridade |
| **aso-audit** | 0% | Não há app mobile |
| **revops** | 15% | Não há pipeline CRM complexo |

---

## 5. FRAMEWORKS ÚTEIS EXTRAÍDOS

### 5.1 Copywriting - Princípios Universais

```
1. Clarity Over Cleverness
2. Benefits Over Features
3. Specificity Over Vagueness
4. Customer Language Over Company Language
5. One Idea Per Section
```

**Aplicação no Instituto:**
- ❌ "Tratamento de emagrecimento completo"
- ✅ "Perca até 5kg no primeiro mês sem passar fome"

### 5.2 Customer Research - Voice of Customer

```
- Extrair linguagem verbatim de pacientes
- Analisar reviews Google Maps
- Identificar "jobs to be done" (por que buscam a clínica)
- Mapear objeções (preço, tempo, medo)
```

**Aplicação no Instituto:**
- Minerar reviews do Google para descobrir linguagem dos pacientes
- Usar objeções reais em copy de vendas da Clara

### 5.3 Content Strategy - Searchable vs Shareable

```
Searchable (captura demanda existente):
- "como emagrecer rápido em Salvador"
- "médico endocrinologista emagrecimento"

Shareable (cria demanda):
- Carrossel sobre glicina (feito hoje)
- Story sobre transformação de paciente
```

### 5.4 Analytics - Framework de Tracking

```
Object-Action naming: {element}_{action}
cta_whatsapp_clicked
form_agendamento_submitted
video_testemunho_played
```

---

## 6. GAPS IDENTIFICADOS (Oportunidades)

### 6.1 Skills que NÃO Existem e Deveríamos Criar

| Skill | Descrição | Prioridade |
|-------|-----------|------------|
| **whatsapp-marketing** | Nutrição de leads, follow-ups, recuperação | 🔴 Alta |
| **local-seo** | Google Maps, Google Business Profile | 🔴 Alta |
| **patient-testimonials** | Coleta, edição e publicação de depoimentos | 🟡 Média |
| **medical-content** | Compliance, disclaimers, referências científicas | 🔴 Alta |
| **appointment-cro** | Otimização de agendamento e confirmação | 🟡 Média |
| **treatment-launch** | Lançamento de novos protocolos/tratamentos | 🟡 Média |
| **clinic-reputation** | Gestão de reviews, reputação online | 🟡 Média |
| **whatsapp-audio** | Scripts de áudio, TTS, atendimento por voz | 🟢 Baixa |

### 6.2 Adaptações Necessárias

**Product Marketing Context → Patient Marketing Context:**
- Trocar "ICP" por "Perfil de Paciente Ideal"
- Trocar "Product" por "Tratamento/Protocolo"
- Trocar "Sign-up" por "Agendamento"
- Trocar "Churn" por "Abandono de Tratamento"
- Trocar "MRR" por "Receita Mensal Recorrente (pacotes)"

---

## 7. IMPACTO ESTIMADO NA PRODUTIVIDADE

### 7.1 Antes vs Depois (Instituto Vital Slim)

| Atividade | Antes (Manual) | Depois (com Skills) | Economia |
|-----------|---------------|---------------------|----------|
| Copy para 1 carrossel | 2-3h | 30min | **85%** |
| Research de concorrente | 3-4h | 45min | **80%** |
| Estratégia de conteúdo | 4-5h | 1h | **80%** |
| Setup de tracking | 2-3h | 30min | **85%** |
| Edição de copy existente | 1-2h | 15min | **90%** |
| Análise de reviews | 2-3h | 20min | **90%** |

### 7.2 ROI Projetado (mensal)

Assumindo 20 peças de conteúdo/mês:
- **Tempo economizado:** ~40h/mês
- **Custo de oportunidade:** R$ 3.000-5.000/mês (tempo da equipe)
- **Custo de implementação:** ~8h de setup inicial
- **Payback:** 1-2 semanas

---

## 8. RECOMENDAÇÕES

### 8.1 Instalação (Segura)

```bash
# 1. Fork do repositório (não instalar diretamente)
git clone https://github.com/coreyhaines31/marketingskills.git

# 2. Copiar só as skills relevantes
cp marketingskills/skills/copywriting/ ~/.openclaw/skills/
cp marketingskills/skills/copy-editing/ ~/.openclaw/skills/
cp marketingskills/skills/social-content/ ~/.openclaw/skills/
cp marketingskills/skills/customer-research/ ~/.openclaw/skills/
cp marketingskills/skills/content-strategy/ ~/.openclaw/skills/
cp marketingskills/skills/marketing-psychology/ ~/.openclaw/skills/

# 3. Adaptar product-marketing-context.md para healthcare
```

### 8.2 Skills Prioritárias (Instalar Primeiro)

1. **copywriting** - Impacto imediato em todo conteúdo
2. **customer-research** - Fundação para toda copy
3. **social-content** - Posts diários no Instagram
4. **content-strategy** - Planejamento mensal
5. **analytics-tracking** - Medir o que funciona

### 8.3 Skills para Adaptar/Criar

1. **whatsapp-marketing** - Não existe no repo, mas é 80% do nosso funil
2. **medical-content** - Compliance e referências científicas
3. **local-seo** - Google Maps é crucial para clínica física

### 8.4 Integração com Nosso Cérebro

- Adicionar referência em `cerebro/OPERATIONS_INDEX.md`
- Criar skill wrapper `marketing-skills` que adapta os frameworks
- Documentar adaptações em `cerebro/verdades-operacionais.md`

---

## 9. CONCLUSÃO

**MarketingSkills** é uma coleção **muito bem estruturada** com frameworks sólidos de marketing digital. Para o Instituto Vital Slim:

✅ **Adotar:** copywriting, customer-research, social-content, content-strategy
🔄 **Adaptar:** page-cro, seo-audit, paid-ads, pricing-strategy
❌ **Ignorar:** signup-flow-cro, onboarding-cro, paywall-upgrade-cro, aso-audit
🆕 **Criar:** whatsapp-marketing, local-seo, medical-content

**Próximo passo recomendado:** Forkar o repo, instalar as 5 skills prioritárias e criar `patient-marketing-context.md` adaptado para healthcare.

---

**Análise concluída em:** 2026-04-22 23:33 UTC
**Modelo usado:** Kimi K2.6
