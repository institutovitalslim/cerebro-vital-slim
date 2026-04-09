# MEMORY.md - Long-Term Memory

_Curated knowledge and context. Updated as I learn._

---

## Skills Criadas

### omie-boletos (2026-04-07)
Skill para baixar boletos de faturamentos do Omie ERP e organizar por paciente.

- **Localização:** `/root/.openclaw/workspace/skills/omie-boletos/`
- **Script:** `scripts/omie_boletos.py`

**Uso:**
```bash
# Listar boletos de uma data
python3 scripts/omie_boletos.py --data DD/MM/AAAA --listar

# Baixar para Google Drive
python3 scripts/omie_boletos.py --data DD/MM/AAAA --drive

# Baixar localmente
python3 scripts/omie_boletos.py --data DD/MM/AAAA --local

# Período específico
python3 scripts/omie_boletos.py --de DD/MM/AAAA --ate DD/MM/AAAA --drive
```

**Regras importantes:**
- Sempre verificar pasta existente antes de criar (nunca duplicar)
- Usar `filtrar_por_emissao_de/ate` (NÃO `filtrar_por_data_de/ate`)
- Pular cancelados e parcelas sem boleto gerado
- Rate limit: 0.4s entre chamadas
- Destino local: `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Boletos de Programa de Acompanhamento`
- Destino Drive: pasta **Pacientes** no Drive da clínica

**Credenciais:**
- Omie: `/root/.openclaw/secure/omie_api.env` (APP_KEY + APP_SECRET)
- Drive: `gog` com conta `medicalemagrecimento@gmail.com`
- `GOG_KEYRING_PASSWORD` via 1Password (item `gog-keyring-pass`)

---

## Skills Criadas

### deep-research-protocol (2026-04-07)
Skill para pesquisa profunda com múltiplas fontes.

- **Localização:** `/root/.openclaw/workspace/skills/deep-research/`
- **Output padrão:** HTML salvo em `/root/.openclaw/workspace/research/`

**Fontes de pesquisa (ordem):**
1. `web_search` (Brave)
2. `web_fetch`
3. Perplexity
4. Knowledge Base (memória)
5. PubMed/Scholar (para conteúdo médico)

**Níveis:**
- **Quick scan:** 5-10 min, 3-5 URLs
- **Standard:** 15-30 min, 8-12 URLs
- **Deep dive:** 30-60 min, 15-20+ URLs (spawnar sub-agent)

**Formato:** HTML com CSS inline, auto-contido, cores da marca (`#d4a84b` dourado).

---

## Skills Criadas

### omie-linha-corte (2026-04-07)
Skill para realizar linha de corte (ponto de corte financeiro) em contas correntes do Omie.

- **Localização:** `/root/.openclaw/workspace/skills/omie-linha-corte/`

**O que faz:**
- Zera o saldo de uma conta corrente no Omie
- Define novo ponto de partida para controle financeiro
- Cria lançamento de ajuste 1 dia antes da data de corte

**Categorias de ajuste:**
- Saldo positivo → `2.05.98` (AJUSTE DE SALDO - Despesa)
- Saldo negativo → `1.04.96` (AJUSTE DE SALDO - Receita)

**Campos corretos da API:**
- `saldo_inicial` e `saldo_data` (NÃO `nSaldoInicial` ou `dDtSaldoInicial`)
- `AlterarContaCorrente` requer: `nCodCC`, `saldo_inicial`, `saldo_data`, `descricao`, `tipo_conta_corrente`, `codigo_banco`

**Execução já realizada:**
- 2026-04-07: Caixinha (6737587708) — saldo R$40 zerado, corte em 01/01/2026, lançamento 6825963504

**Regra de segurança:** SEMPRE confirmar com o usuário antes de executar

---

## Clara / Vendas

### Aprendizados de vendas incorporados à Clara (2026-04-09)
Foram analisados dois perfis de Instagram para aprender técnicas de vendas adaptáveis à Clara Concierge do Instituto Vital Slim:

- **Yuri Barbosa (`@yuribarbosaoficial`)**
  - Aprendizados principais: condução intencional, valor antes de preço, rapport breve e contextual, objeção tratada com clareza, follow-up mais elegante.
  - O que não importar: pressão, manipulação emocional, urgência artificial, linguagem agressiva de closer.

- **Oestevão Souza (`@oestevaosouza`)**
  - Análise feita por triangulação pragmática por limitação pública do Instagram.
  - Aprendizados principais: direção comercial, diagnóstico curto, foco em resultado/processo, microcompromissos claros, postura consultiva.

**Mudança aplicada:** prompt da Clara na bridge foi atualizado para incorporar esses princípios com tom premium e seguro para contexto de saúde.

## Índice

| Data | Evento |
|------|--------|
| 2026-04-07 | Skill `omie-boletos` criada para baixar boletos do Omie ERP |
| 2026-04-07 | Skill `deep-research-protocol` instalada para pesquisa profunda multi-fonte |
| 2026-04-07 | Skill `omie-linha-corte` criada para linha de corte em contas correntes do Omie |
| 2026-04-09 | Prompt da Clara refinado com aprendizados de vendas dos perfis de Yuri Barbosa e Oestevão Souza |
