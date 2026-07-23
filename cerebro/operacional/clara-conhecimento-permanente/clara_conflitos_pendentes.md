# Conflitos/decisões da Clara — pendentes
> Política de preço/abordagem fixada (consulta R$1.000, desconto autorizado R$100->R$900, pré R$300 abatida, cashback; SPIN selling; Programa não pré-consulta; 35%/recorrente só humano). Aprendizado só de LEAD. O cron acrescenta aqui só conflitos NOVOS reais.


## [2026-06-22] conflitos/decisoes
### Endereço incompleto/divergente — confirmar dado oficial
- Hoje a Clara enviou o endereço sem o CEP e mencionou "ao lado da CPX" (não "Estação Villas Shopping" como no conhecimento). O endereço autoritativo é Rua Priscila B. Dutra, 389, Estação Villas Shopping, sala 305, Buraquinho, Lauro de Freitas-BA, CEP 42709-200. Tiaro confirmar referência correta ("CPX" vs "Estação Villas Shopping") para padronizar.


## [2026-07-11] conflitos/decisoes
### Conduta do HUMANO que NÃO é replicável pela Clara — pedir decisão do Tiaro
- O humano informou proativamente valores de PROGRAMA/tratamento (ampola Tirzepatida 10x R$650, comparação R$12.802 na farmácia, implantes para endometriose, equipe 24/7) ANTES/independente de consulta. Isso conflita frontalmente com RC-01 (proibido divulgar valor de Programa/acompanhamento pré-consulta) para a Clara. Confirmar: a Clara deve continuar BLOQUEADA de citar qualquer valor/dose de tratamento, escalando para humano — mesmo tendo esse 'padrão-ouro' humano na thread? (Recomendo manter bloqueio da Clara e NÃO promover esses valores como aprendizado dela.)
- O humano também ofereceu "se eu conseguir um desconto e aumentar parcelamento" — se isso extrapola o desconto autorizado (R$100/R$900, reserva R$300, 2x), é território RC-07 (só humano). Confirmar limite de negociação que a Clara pode oferecer sozinha.
- Apareceu uma linha de produto NOVA na thread do humano: "Experiência Supramaximus" (agendamento com biquíni/roupa de academia, sem jejum). A Clara não tem base para conduzir isso. Confirmar se deve ignorar/escalar ao detectar menção a Supramaximus.


## [2026-07-11] conflitos/decisoes
### Reutilização de nome de outro lead (possível violação RC-34) — decisão Tiaro
- A Clara(auto) chamou leads de 'Tamile' sem essa lead ter fornecido o nome (nome parece vazado de outra ficha/thread). Precisa correção determinística no runtime: bloquear uso de nome que não foi digitado pelo próprio lead na thread atual.

### Conteúdo do HUMANO com valores de PROGRAMA/tirzepatida — NÃO aprender, apenas registrar
- O HUMANO citou valores de ampola de Tirzepatida (10x R$650), comparação com farmácia (R$12.802,68), progressão de dose e detalhes de Programa/implantes de endometriose. Isso é conduta clínica/valor de Programa que a Clara NÃO pode reproduzir (RC-01). Registrado só para não atribuir à Clara nem promover como padrão de captação.


## [2026-07-12] conflitos/decisoes
### Possível conflito para decisão do Tiaro — HUMANO cotou preços de TRATAMENTO/medicação pré-consulta
- O HUMANO(takeover) informou valores detalhados de medicação/tratamento antes da consulta: 'ampola 10x R$650', comparação com Mounjaro de farmácia (R$1.422,52 x9 = R$12.802,68), 'Programa de Acompanhamento inclui implantes'. Isso é conduta de humano autorizado (RC-07), mas contraria a política que proíbe a CLARA de divulgar valor de Programa/tratamento pré-consulta (RC-01).
- **Decisão necessária:** confirmar que esses valores de tratamento/ampola/programa permanecem EXCLUSIVOS do humano e que a Clara jamais deve reproduzi-los, mesmo tendo-os 'visto' na thread. Sem isso, há risco de a Clara aprender e vazar cotação de tratamento (violação RC-01).


## [2026-07-20] conflitos/decisoes
### RESOLVIDO — Convênio
Tiaro decidiu em 20/07: resposta exata obrigatória.
Regra aplicada: Clara deve responder exatamente “Por termos um atendimento completamente exclusivo e limitado a uma quantidade máxima de pacientes por turno, com foco total no seu acolhimento e na entrega de seus resultados, não atendemos convênio”.


## [2026-07-21] conflitos/decisoes
### RESOLVIDO — 'Lotérica Estrada do Coco / bolões da Caixa' não foi vazamento da Clara
- Decisão/correção do Tiaro: não foi vazamento de persona da Clara. Era mensagem automática de resposta do WhatsApp comercial daquele lead.
- Regra aplicada: antes de classificar mensagem estranha como vazamento/bug da Clara, verificar direção e origem no webhook (`from_me`, `from_api`, `sender_name`, instância e telefone). Se for inbound/auto-resposta do lead, tratar como contexto do lead/empresa dele, não como saída da Clara.


## [2026-07-22] conflitos/decisoes
### RESOLVIDO — Clara pode falar o valor da pré-consulta/reserva R$300
- Decisão do Tiaro: a Clara pode falar o valor da pré-consulta.
- Regra aplicada: pré-consulta/reserva de **R$300**, no cartão em até **2x sem juros**, é informação autorizada e deve ser posicionada como valor **abatido do total da consulta**, não como taxa extra. Ex.: consulta R$1.000 = R$300 reserva + R$700 saldo; com desconto de fechamento, consulta R$900 = R$300 reserva + R$600 saldo.
- Limite mantido: Clara continua proibida de divulgar valor de Programa, medicações, injetáveis, implantes ou tratamento antes da consulta.
