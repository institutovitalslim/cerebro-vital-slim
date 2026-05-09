# IVS Agent Operating Layer — Workflow Registry

Registry operacional dos workflows read-only e guardrailed da operação assistida IVS.

Workflows:
- `followup-seguro`: preflight e governança de follow-up Clara/Z-API.
- `preconsulta-safety`: segurança de submissões, drafts e markdowns da pré-consulta.
- `marketing-os`: continuidade operacional do João e entregáveis de marketing.
- `agent-layer-audit`: consolidação executiva Clara + Pré-consulta + João.

Regra central: monitores são read-only por padrão. Qualquer ação de estado exige autorização explícita quando houver risco operacional.
