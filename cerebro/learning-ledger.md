## 2026-04-22 - Skills de Marketing adaptadas do MarketingSkills (coreyhaines31)

### Análise de segurança
- Risco médio: prompt injection possível em markdown files de skills externas
- Risco médio: dependências externas (npx skills, plugins)
- Decisão: NÃO instalar diretamente do repo externo
- Decisão: Criar skills próprias baseadas nos conceitos, escritas do zero

### Skills criadas/adaptadas
1. **copywriting-vitalslim** — copywriting para healthcare (95% aplicável)
2. **customer-research-vitalslim** — pesquisa com pacientes, JTBD, voice of customer
3. **social-content-vitalslim** — conteúdo Instagram/WhatsApp, framework carrossel viral
4. **content-strategy-vitalslim** — planejamento de conteúdo, SEO local, calendário editorial
5. **whatsapp-marketing** (NOVA) — fluxos de conversação, follow-ups, reativação
6. **local-seo** (NOVA) — Google Business Profile, reviews, palavras-chave locais
7. **medical-content** (NOVA) — compliance CFM, disclaimers, referências científicas
8. **patient-marketing-context.md** — contexto compartilhado adaptado para healthcare

### Localização
Todas em `~/.openclaw/skills/` exceto `patient-marketing-context.md` em `cerebro/`

### Impacto estimado
- ~40h economizadas/mês em produção de conteúdo
- ROI: R$ 3.000-5.000/mês em tempo de equipe
- Payback: 1-2 semanas

### Próximo passo
Popular `cerebro/patient-marketing-context.md` com dados reais da clínica

---

## 2026-04-22 - Correções em carrosséis

### Problema: badge de verificação sobrepondo nome
- **Causa:** espaçamento insuficiente entre o nome e o badge no `make_tweet_slides.py`
- **Fix:** aumentado de `nb[2] + 6` para `nb[2] + 12`
- **Arquivo alterado:** `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py`

### Problema: caracteres Unicode renderizando como quadrados (tofu)
- **Causa:** fonte DejaVuSans não possui glyphs para alguns caracteres especiais usados nos slides
- **Fix:** adicionada função `sanitize_text()` para substituir caracteres problemáticos por alternativas seguras (•, →, ✓, ✗)
- **Arquivo alterado:** `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py`

### Slides afetados e corrigidos
- Slide 2 do carrossel GlyNAC (badge sobreposto)
- Slide 8 do carrossel GlyNAC (símbolo ☐ antes da referência)

### Lição
Sempre validar a renderização de caracteres especiais e o posicionamento de elementos visuais antes de entregar carrosséis finais.

---

## 2026-04-23 - Omie: serviço deve ser confirmado antes de emitir NFS-e

### Problema
A NFS-e do caso de Mario Gomes de Abreu Filho retornou com rejeição da prefeitura porque a OS foi criada com serviço incorreto para o caso.

### Aprendizado
- Em emissão de OS/NFS-e no Omie, nunca criar ou assumir serviço por conta própria.
- Sempre perguntar ao Tiaro qual serviço/cadastro de serviço do Omie deve ser usado.
- Serviço parecido ou descrição improvisada pode passar na criação da OS e falhar depois na autorização da NFS-e.

### Regras reforçadas
- Confirmar explicitamente o banco antes da emissão.
- Confirmar explicitamente o serviço exato antes da emissão.
- Não inventar novo serviço textual quando o correto é usar um cadastro específico já existente no Omie, como `PROGRAMA DE ACOMPANHAMENTO INTENSIVO`.
- Quando a emissão for com nota fiscal, habilitar sempre `Enviar o link da NFS-e gerada na prefeitura`.
- Em emissão com NFS-e, o serviço deve ser selecionado pela lista/cadastro de serviços do Omie, nunca digitado manualmente, porque o cadastro da lista puxa os dados fiscais corretos.
- Mapeamentos confirmados: `Tricologia` = `SRV00016`; `Programa de Acompanhamento Intensivo` = item da lista correspondente, com referência visual apontando `SRV00013`.
- Regra técnica validada por teste real: para a OS puxar a descrição fiscal completa do serviço cadastrado, `ServicosPrestados` precisa enviar o `nCodServico` do cadastro do serviço (`nCodServ`), e não apenas descrição/campos montados manualmente.
