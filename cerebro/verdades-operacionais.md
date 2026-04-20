# Verdades Operacionais

Este arquivo concentra fatos operacionais canônicos que **não podem ser esquecidos**.

## GitHub / Cérebro
- Repositório oficial do cérebro: `institutovitalslim/cerebro-vital-slim`
- URL remota correta: `https://github.com/institutovitalslim/cerebro-vital-slim.git`
- Quando Tiaro disser **"commit no cérebro"**, isso significa:
  1. atualizar os arquivos relevantes no workspace do cérebro;
  2. fazer `git commit`;
  3. fazer `git push` para o repositório oficial no GitHub.

## WhatsApp
- A comunicação operacional por WhatsApp deve usar a **bridge da Z-API**.
- Não assumir que um fluxo criado a partir de contexto Telegram consegue disparar WhatsApp automaticamente sem estar amarrado ao contexto/caminho correto.

## Quarkclinic
- Agenda padrão para novos agendamentos via API: **AGENDA OPENCLAW**
- `agendaId`: `445996589`
- `profissionalId`: `240623016` (Daniely Alves Freitas)
- `clinicaId`: `227138348` (Instituto Vital Slim)
- A agenda `240623539` pode listar horários livres, mas pode bloquear criação via endpoint com erro de agenda não permitir agendamentos online.
- Ao marcar consulta, sempre consultar `/horarios-livres` da agenda padrão primeiro.
- Quando o horário exato não existir, usar o início real do slot livre mais próximo e informar isso claramente.

## Omie
- Para cadastrar paciente no Omie a partir de um nome solto, usar o fluxo canônico da skill `skills/omie-cadastro-paciente/`.
- Fluxo obrigatório: buscar no Quarkclinic, confirmar a identidade com o usuário, checar duplicidade no Omie e só depois criar.
- `codigo_cliente_integracao` do cadastro vindo do Quarkclinic deve seguir o padrão `QC-<id do paciente>`.
- Não inferir cidade, estado, CEP ou complemento quando esses dados não vierem preenchidos no Quarkclinic; pedir complemento ao usuário ou manter vazio.
- Ao emitir proposta/OS no Omie com cobrança por boleto, não basta escrever isso em observação: é obrigatório preencher corretamente os campos estruturados de categoria, conta corrente, `Gerar boleto = Sim`, `Enviar também o boleto de cobrança = Sim`, tipo de pagamento `Boleto` e meio de pagamento `Boleto Bancário`.
- Quando o caso exigir recibo em vez de nota fiscal, isso deve coexistir com a configuração correta de boleto nas parcelas; uma coisa não substitui a outra.

## Time da clínica
- **Dra. Daniely Alves Freitas**
  - WhatsApp: `+55 71 99696-2059`
  - E-mail: `danyafreitas@hotmail.com`
- **Liane (enfermeira)**
  - WhatsApp: `+55 71 99157-4827`
  - E-mail: `enfermagem.vitalslim@gmail.com`

## Comercial / Leads
- Nunca passar preço antes de o paciente entender o valor do atendimento.
- Em leads, primeiro acolher, entender a necessidade, contextualizar o atendimento e explicar a proposta/avaliação; só depois entrar em preço.
- Quando Tiaro pedir para "chamar o conselho", usar a skill/metodologia canônica de conselho (`llm-council`) quando ela for a referência definida, e não improvisar com subagente genérico.

## Tweet-carrossel
- OpenClaw `v2026.4.11` possui sistema nativo de image providers.
- Para gerar imagens de carrossel, preferir provider Google com NanoBanana 2 (`google/gemini-3.1-flash-image-preview` / NanoBanana 2).
- Fallback permitido: OpenAI (`gpt-image-1`).
- Banco central de fotos reais da Dra. Daniely:
  - originais: `/root/.openclaw/workspace/fotos_dra/originais/`
  - avatares: `/root/.openclaw/workspace/fotos_dra/avatares/`
- Acervo disponível inclui looks e poses em blazer branco, vestido branco longo, blazer branco com blusa preta e saia preta, macacão vermelho e composições com Bio Meds, seringa e modelos corporais.
- Para TODA capa de carrossel, usar obrigatoriamente o script `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py`.
- Fluxo obrigatório da capa:
  1. selecionar uma foto REAL da Dra. no repositório central;
  2. se necessário, editar apenas o FUNDO com NanoBanana 2, preservando rosto e corpo;
  3. gerar a IMAGEM DO CÍRCULO via NanoBanana 2 com contexto do tema;
  4. montar a capa com `make_cover.py`.
- Comando padrão:
  `python3 scripts/make_cover.py --foto FOTO.png --circulo CIRCULO.png --headline "LINHA1|LINHA2" --destaques "PALAVRA1,PALAVRA2" --out capa.png`
- NUNCA gerar rosto da Dra. via IA.
- NUNCA gerar a capa inteira com texto via image tool.
- Se a troca de fundo distorcer a Dra., usar a foto original com fundo escuro.
- SEMPRE usar `make_cover.py` para manter consistência de layout.

## Regra de operação
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API ou time da clínica, consultar os arquivos canônicos correspondentes em `cerebro/`.
