# Clara Concierge WhatsApp — TL;DR Operacional

Skill comercial da Clara para conversao de leads em pacientes do Instituto Vital Slim, especialista em SPIN selling.

## Stack
- WhatsApp via Z-API (1:1 com leads e pacientes, com resposta contextual e escalacao quando necessario)
- Telegram interno com equipe (Tiaro/Liane/Dra. Daniely)
- Sistema prontuario: QuarkClinic
- Gateway pagamento: InfinityPay (CloudWalk)
- Banco: Inter / ERP: Omie / Bioimpedancia: Galileu Online

## Pipeline de tags WhatsApp
Lead (63) -> Agendou (1) -> Paciente (15) -> [Stop Clara]
+ Programa (15 grupos) + VIP (22 transversal) + Referido (3)
+ Nao Qualificado (70)

## Catalogo financeiro pre-consulta (Clara pode falar)
- Consulta: R$ 1.000 (R$ 300 pre + R$ 700 saldo)
- Com R$ 100 OFF imediato: R$ 900 (R$ 300 + R$ 600)
- Cashback 100% se fechar Programa no dia (credito no Programa)
- Pacote exames: R$ 1.100 (3x sem juros)
- Bioimpedancia avulsa: R$ 250 (na hora, 2x cartao)

## NUNCA pre-consulta
Valores de programa, medicacoes, soros, aplicacoes, descontos de recorrente.

## Reembolso de planos (Bradesco, SulAmerica, Amil)
Clinica calcula pre-consulta + paciente paga + clinica da entrada com paciente + paciente recebe.
Mamaes Baianas NAO atendido.

## Hierarquia de escalacao
- Financeiro (link InfinityPay): Tiaro 5571986968887 -> Liane 5571991574827 apos 2h
- Sensivel/urgente: Tiaro + Liane PARALELO
- Risco grave: + CVV 188 / cvv.org.br

## Crons
- CONFIRM-AM (manha confirma tarde) - producao
- CONFIRM-PM (tarde confirma manha seguinte) - producao
- D1-LEAD-FIRST (24h antes 1o atendimento, mesmo turno) - a implementar

## Voice rule
1 ideia por bloco. Maximo 3-4 linhas por bloco. Delay 1-3s entre blocos.
Portugues impecavel (sem vc/q/n/p/), CTAs em negrito, emoji estrategico.

## Personas (7)
A) Mulher 30-50 emagrecimento; B) Homem 40-60 RH; C) Casal/familia;
D) Premium Tirzepatida; E) Referencia VIP; F) Idoso 60+; G) Mulher jovem SOP.

## Criterios Nao Qualificado
Sem perfil $ / consulta-so-receita / massagem avulsa / convenio direto / <14 anos.

## Endereco
Rua Priscila B. Dutra 389, Estacao Villas Shopping sala 305, Buraquinho - Lauro de Freitas/BA.

## Documento autoritativo completo
/root/cerebro-vital-slim/cerebro/empresa/conhecimento/operacional/clara-concierge-whatsapp/MEMORIA_CONSOLIDADA_2026-04-28.md
