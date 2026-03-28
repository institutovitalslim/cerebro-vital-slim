# Lições Aprendidas — Empresa

> O que aprendemos com erros e acertos. Cada lição gera uma ação concreta.

---

## Março 2026

### Migração de plataforma exige checklist completo
- **Contexto:** Migração para Hotmart teve 3 dias de links quebrados
- **Lição:** Sempre ter checklist de pré-migração com: links, emails automáticos, pixel, checkout, área de membros
- **Ação:** Criado template de checklist para futuras migrações

### Follow-up de leads esfria rápido
- **Contexto:** 40% dos leads ficavam sem contato por 5+ dias
- **Lição:** Se não contactar em 48h, a taxa de conversão cai 70%
- **Ação:** Implementar cron diário de alerta de leads frios

### [2026-03-26] Gap de dados no CSV de vendas
- **Contexto:** Relatório entregue sem dados dos últimos dias por ausência no CSV
- **Lição:** Antes de entregar qualquer relatório de vendas/leads, verificar se o CSV tem dados recentes. Se o último registro tiver mais de 2 dias, avisar a equipe sobre possível gap — evita passar imagem de queda quando é só ausência de dado
- **Ação:** Verificação de atualidade dos dados incorporada ao fluxo de relatórios

### [2026-03-27] Relatórios HTML → sempre enviar como documento .html
- **Contexto:** Telegram não renderiza HTML inline; Cayo confirmou padrão na sessão de demonstração
- **Lição:** Sempre enviar arquivos `.html` como documento anexo via Telegram. Screenshot como preview é opcional, não obrigatório
- **Ação:** Padrão incorporado nas skills de relatório

---

_Atualizado: 28/03/2026_
