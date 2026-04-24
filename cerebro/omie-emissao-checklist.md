# Checklist de Pré-Voo — Emissão no Omie

**Use este checklist antes de TODA emissão de OS, proposta, boleto ou NFS-e no Omie.**

---

## ☑️ CHECKLIST OBRIGATÓRIO

### 1. Verificação do Modelo LLM
- [ ] Modelo atual é `openai-codex/gpt-5.5` ou `openai-codex/gpt-5.4`?
- [ ] Se estiver em `kimi-k2.6` ou outro, **trocar antes de prosseguir**
- [ ] Motivo: Kimi trava em tool-use longo → stopReason=toolUse com payloads=0

### 2. Identificação do Paciente
- [ ] Paciente localizado no QuarkClinic?
- [ ] Nome confirmado com o usuário?
- [ ] Se nome for ambíguo, pedir CPF ou identificador único
- [ ] Paciente já cadastrado no Omie? Se não, cadastrar primeiro.

### 3. Serviço / Descrição
- [ ] Serviço selecionado da **lista cadastrada** do Omie?
- [ ] **NUNCA** digitar descrição manualmente
- [ ] Mapeamento confirmado:
  - `Tricologia` → `SRV00016` → `nCodServ: 6831167233`
  - `Programa de Acompanhamento Intensivo` → `SRV00013` → `nCodServ: 6737863763`
  - Outro serviço → consultar `cerebro/omie-servicos.md`
- [ ] Se houver dúvida, **perguntar ao Tiaro** qual serviço exato usar

### 4. Banco / Conta Corrente
- [ ] Banco/conta corrente confirmado com o Tiaro?
- [ ] **NUNCA** assumir o banco do caso anterior
- [ ] Se boleto: conta correta configurada?

### 5. Configuração Financeira (se houver cobrança)
- [ ] `Gerar boleto = Sim` (se aplicável)
- [ ] `Enviar também o boleto de cobrança = Sim` (se aplicável)
- [ ] Tipo de pagamento/documento = `Boleto` (se aplicável)
- [ ] Meio de pagamento = `Boleto Bancário` (se aplicável)
- [ ] Se for cartão: tipo/meio configurados corretamente?
- [ ] Se exigir recibo em vez de nota fiscal: observação registrada

### 6. Nota Fiscal (se aplicável)
- [ ] `Enviar o link da NFS-e gerada na prefeitura` = **habilitado**
- [ ] Serviço da lista cadastrada (para puxar descrição fiscal correta)
- [ ] Valor, quantidade e unidade conferidos?

### 7. Validação Final
- [ ] Revisar todos os campos antes de clicar "Criar OS" / "Faturar"
- [ ] Valor total está correto?
- [ ] Paciente, serviço e banco conferidos?

---

## 🔄 APÓS EMISSÃO

### Faturamento com NFS-e
- [ ] `FaturarOS` retornou sucesso?
- [ ] **Aguardar** retorno da prefeitura (pode levar minutos)
- [ ] Se `ConsultarOS` mostrar `cFaturada = "N"`, não panicar — estado transitório normal
- [ ] Verificar novamente em 5-10 minutos
- [ ] Confirmar NFS-e autorizada antes de declarar concluído

### Entrega de Boletos
- [ ] Baixar todos os PDFs dos boletos
- [ ] Enviar PDFs no tópico do Telegram **no mesmo fluxo**
- [ ] Não esperar pedido adicional do usuário

---

## 🚨 SE DER ERRO

### NFS-e Rejeitada
1. **NÃO** reaproveitar a mesma suposição de serviço
2. Confirmar serviço exato com o Tiaro
3. Se OS anterior estiver cancelada/inconsistente → criar **nova OS espelho**
4. Não tentar forçar reaproveitamento cego

### OS não aparece como faturada
1. Verificar se `FaturarOS` retornou sucesso
2. Se sim → aguardar retorno da prefeitura (assíncrono)
3. Se após 30 min ainda não aparecer → investigar

---

## 📋 RESUMO VISUAL

```
[  ] Modelo correto (GPT-5.5/5.4)
[  ] Paciente identificado e confirmado
[  ] Serviço da lista (nunca manual)
[  ] Banco confirmado com Tiaro
[  ] Financeiro configurado
[  ] NFS-e com link habilitado
[  ] Revisar tudo → CRIAR OS
[  ] Faturar → aguardar prefeitura
[  ] Baixar boletos → enviar no Telegram
```

---

**Referências cruzadas:**
- `cerebro/omie.md` — regra de roteamento de modelo
- `cerebro/omie-servicos.md` — lista de serviços cadastrados
- `cerebro/verdades-operacionais.md` — regras de banco e serviço
- `skills/omie-cadastro-paciente/SKILL.md` — fluxo de cadastro
