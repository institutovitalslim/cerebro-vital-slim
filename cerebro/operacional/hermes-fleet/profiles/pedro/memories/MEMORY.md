# Memoria do Pedro - Contexto & Aprendizados
> Destilado de 757 turnos do topico 1980 (OpenClaw) em 2026-06-22.

# MEMÓRIA OPERACIONAL — PEDRO (Controller Financeiro IVS)

## 1. Quem é o Pedro e como o Tiaro quer que ele atue

- **Papel:** Controller financeiro do Instituto Vital Slim (IVS); reporta ao Tiaro (CEO). Maria também aparece como interlocutora operacional.
- **Tom/formato:** Respostas estruturadas em Markdown com blocos: **Resumo executivo**, **Números principais**, **Exceções**, **Decisão necessária**, **Próximo passo recomendado**. Direto, objetivo, sem floreio.
- **Postura de segurança (guardas):** Não executa escrita/alteração sensível no Omie sem **aprovação explícita** do Tiaro (conta, data, valor/critério, finalidade). Nunca apaga histórico — usa ajustes não destrutivos e rastreáveis.
- **Correção dada pelo Tiaro (importante):** Pedro **TEM acesso ao Omie** (API e browser). O Tiaro repreendeu Pedro mais de uma vez por dizer "não tenho acesso/conector". **Regra firmada: SEMPRE procurar/usar o próprio acesso antes de alegar indisponibilidade.**

## 2. Contexto financeiro/operacional recorrente

- **ERP:** Omie (API + interface web `app.omie.com.br`). Login via Google OAuth (`medicalemagrecimento@gmail.com`), com 2FA — Tiaro envia o código quando solicitado (precisa ser rápido).
- **Acesso browser:** Chrome/Chromium na VPS Hostinger (perfil OpenClaw, `--remote-debugging-port=18800`). **Regra: usar sempre o Chrome/Chromium já validado.** Quando a API falha, entrar pelo browser autenticado.
- **Sistema clínico:** QuarkClinic (origem de dados de pacientes para NF).
- **Contas bancárias e IDs Omie:**
  - Caixinha — 6737587708
  - Omie.CASH — 6737590387
  - Bradesco — 6737642153
  - Santander — 6737645884
  - Banco Inter — 6737869298
  - Cloudwalk IP LTDA — 6737869936
  - Santander CONTA MAX — 6842007012
- **Serviços Omie:** Consulta Médica `SRV00001`; Consulta Nutricional `SRV00002`; Bioimpedância `SRV00004`; Tricologia `SRV00016` (nCodServ 6831167233).
- **Atividades recorrentes:** conciliação bancária (OFX x Omie), ponto de corte/linha de corte, ajustes de saldo, emissão de NFS-e e boletos, faturamentos parcelados, download/organização de boletos no Drive, lembretes de pagamento.
- **Mapa de referência API Omie:** `/root/.openclaw/workspace/relatorios/mapa_varredura_omie_developer_2026-05-14.md` — **consulta obrigatória antes de qualquer ação no Omie.**
- **Limites API Omie:** 4 req/s, 240 req/min, 14.400 req/h. Paginação ≤500/página. Já houve bloqueios 429/erro 100 (hash `0f0fc74163da1a8fe53fb2f31075cba5`).

## 3. Preferências e regras dadas pelo Tiaro

**Regras de classificação contábil (conta Bradesco salvo indicado):**
- Entrada "RENTABINVEST FACILCRED" → categoria **Rendimentos de Aplicações**, favorecido **Bradesco**.
- Saída "TARIFA" ou "TAR" → categoria **Tarifas Bancárias**, beneficiário **BRADESCO**.
- Saída "ENCARGOS" → categoria **Juros sobre Empréstimos**, favorecido **Bradesco**.
- Saída "GASTOS CARTÃO DE CRÉDITO" (cobrança de cartão) → **transferência interna** para conta **Cartão Bradesco - Elo** (não despesa).
- Saída com descrição "TIARO FERNANDES NEVES" (**qualquer conta**) → categoria **Retirada de Sócio**.

**Regras de conciliação/transferência:**
- Toda transferência bancária interna → lançar **as duas pontas** (saída origem + entrada destino). Só considerar conciliado quando ambas existirem/conciliadas.
- Validar header pós-upload de OFX (risco já visto de Santander cair como Inter) — se não bater 100%, parar.

**Operacionais:**
- Pode acessar a interface via browser sempre que precisar; se API falhar, usar browser; se pedir 2FA, avisar imediatamente.
- Para escrita no Omie: aprovação formal ("Autorizo Pedro executar escrita Omie com este payload aprovado agora").
- NF: buscar dados do paciente no QuarkClinic; pedir confirmação se cadastro incompleto.

## 4. Aprendizados/decisões importantes

- **Banco Inter — ponto de corte 01/01/2026:** saldo inicial zerado; ajuste complementar de **-R$ 8.030,58** (31/12/2025, ID 6838179860, cat 2.05.98); depois ajuste positivo **+R$ 4.098,57** (01/01/2026, ID 6838287565, cat 1.04.96) para bater com OFX. Saldo final validado: **-R$ 4.936,11**.
- **Limitação API Omie:** não aceita gravar campo de conciliação (`dDtConc`) via `AlterarLancCC`. Conciliação formal precisa ser feita pela **interface web** ou importação OFX interna.
- **Conciliação 4 contas (Inter/Bradesco/Santander/Cloudwalk):** 50 transferências internas seguras mapeadas (R$ 305.095,33). Planilha: `relatorios/conciliacao_transferencias_internas_2026-01-01_a_2026-05-11.csv`.
- **Auditoria de pares:** 101 pares, 97 OK, **4 exceções pendentes de conciliação visual** (cartão Bradesco→Elo 20/03 R$5.273,68; 20/04 R$75,76; 24/04 R$6.055,94; Santander→Bradesco 24/04 R$8.100,00).
- **Conciliação Santander:** OFX importado e header validado (Santander, ag 0933, conta 13005102-5). 55 transferências internas OK. Restam ~214 movimentos OFX sem match no Omie + 4 lançamentos sem `dDtConc` + 2 grupos ambíguos (03/03 e 16/03, R$3.000 cada). **Não finalizado** (browser/CDP caiu).
- Variação OFX = 1 lançamento banco vs 2 no Omie em 07/01 (890) e 20/02 (2.700) — sem impacto de saldo.
- **NF Jucimar da Silva Moura:** cliente cadastrado no Omie (código **6855647359**). Endereço completado manualmente (Rua Florice da S Pinto s/n, Itinga, Lauro de Freitas/BA, CEP 42.738-510). Conta escolhida: **6 = Cloudwalk IP LTDA** (6737869936).

## 5. TAREFAS ABERTAS / Pendências

1. **Conciliação Santander — finalizar:** retomar tela "Lançamentos Importados" no Omie, conciliar matches seguros, resolver ~214 OFX sem match, 4 lançamentos sem `dDtConc`, 2 grupos ambíguos (R$3.000). Auditar até fechar.
2. **4 exceções de conciliação visual** (cartão Bradesco→Elo e Santander→Bradesco) — marcar conciliado pela interface até atingir 101/101.
3. **Saldo inicial Bradesco 01/01/2026 → corrigir para R$ 244,87** (solicitado, não confirmado como executado).
4. **NFS-e Jucimar — emitir as 3 notas** (Consulta Médica R$392,20; Bioimpedância R$80,66; Consulta Nutricional R$211,63; total R$684,49), na conta **6 (Cloudwalk)**. Autorização de escrita já dada; faltou concluir após informar `nCodCC`.
5. **Pós-emissão Jucimar:** investigar na documentação/API do QuarkClinic por que o **endereço vem incompleto** e propor correção.
6. **NF Marize — tricologia, Pix Santander, R$2.500, hoje:** ficou **bloqueada por 429/erro 100** do Omie. Retomar quando liberar (serviço SRV00016).
7. **Faturamento Silvana Modesto:** R$33.500 em 6 boletos Bradesco, venc. dia 25 (25/06 a 25/11/2026); 1ª R$5.583,35, demais R$5.583,33. Emitir recibo e **salvar boletos na pasta de boletos dos pacientes**. (Tiaro cobrou execução — verificar se concluído.)
8. **Lembrete (recorrente/pontual):** 24/06 às 08:00 — pagar boleto **PORTOSEG S/A R$3.609,16** (venc. 24/06/2026, pagador Daniely Alves Freitas). Conferir beneficiário/CNPJ antes de pagar. (Lembrete da Silvana p/ Liane em 16/06 08:50 — já no passado.)