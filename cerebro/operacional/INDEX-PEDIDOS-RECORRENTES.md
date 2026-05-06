# Índice de Pedidos Recorrentes

## 1. "faz um reel disso"
- significa: transformar referência, insight, vídeo, print ou ideia em ativo de reel do IVS
- porta de entrada: `cerebro/areas/marketing/skills/criacao-reels/SKILL.md`
- apoio obrigatório: `cerebro/areas/marketing/governanca-visual-ivs-index.md`
- output esperado: hooks, roteiro, adaptação IVS, quebra de objeção e reaproveitamento

## 2. "segue com as melhorias"
- significa: continuar a reorganização já iniciada no bloco ativo
- porta de entrada: `cerebro/empresa/_governanca/README.md` e `cerebro/areas/_governanca/README.md`
- output esperado: correção estrutural + relatório HTML + envio no Telegram

## 3. "analisa isso" / "olha esse reel"
- significa: ler a peça, classificar, adaptar para IVS e gerar desdobramentos
- porta de entrada: `cerebro/areas/marketing/skills/criacao-reels/SKILL.md`
- apoio: repertório de engenharia reversa + governança visual

## 4. "o que está pendente?"
- significa: listar backlog real da frente ativa
- porta de entrada: `cerebro/empresa/projetos/` e relatórios HTML recentes
- output esperado: pendências priorizadas e próximas ações

## Regra
Este índice deve crescer conforme surgirem pedidos recorrentes reais do Tiaro.


## 5. "faz essa apresentação" / "ajusta essa apresentação"
- significa: gerar ou editar apresentação HTML mantendo padrão aprovado
- porta de entrada: `skills/geracao-apresentacao-paciente/SKILL.md`
- regra crítica: edição mínima quando o pedido for ajuste pontual
- output esperado: arquivo HTML pronto + envio/link automático

## 6. "analisa esse perfil/reel/post do Instagram"
- significa: ler peça e extrair mecanismo útil para IVS
- porta de entrada: `cerebro/areas/marketing/skills/criacao-reels/SKILL.md`
- regra crítica: começar pela rota canônica validada da RapidAPI para Instagram
- output esperado: leitura da peça + adaptação IVS + hooks/roteiro/desdobramentos

## 7. "faz o vídeo" / "gera esse reel em vídeo"
- significa: transformar roteiro/aprovação em entrega audiovisual completa
- porta de entrada: `cerebro/areas/marketing/skills/criacao-video-ivs/SKILL.md`
- regras críticas: ElevenLabs como padrão de voz, Qwen como padrão de vídeo, avatar mestre obrigatório, 1 cena = 1 clip = 1 fala = 1 legenda
- output esperado: vídeo visível, voz crível e legenda sincronizada

## 8. "como responder essa lead?" / "me ajuda nessa objeção"
- significa: gerar resposta de atendimento/vendas com direção consultiva e remoção de trava
- porta de entrada: `cerebro/areas/atendimento/` e `cerebro/leads-argumentos-venda-ligacoes.md`
- apoio: checklist e scripts da Clara
- output esperado: resposta prática, curta, natural e orientada a avanço


## 9. "gera os boletos" / "baixa os boletos" / "olha os boletos do Omie"
- significa: operar o fluxo canônico de boletos Omie sem redescoberta
- porta de entrada: `cerebro/empresa/conhecimento/operacional/boletos-omie-processo.md`
- output esperado: execução correta, destino correto e troubleshooting rápido

## 10. "consulta o histórico" / "puxa o histórico dessa paciente"
- significa: consultar histórico na planilha/camada operacional já validada
- porta de entrada: skill de histórico de conversas e script `consultar_historico.py`
- output esperado: contexto consolidado da paciente para continuidade de atendimento

## 11. "atualiza isso na memória da Clara" / "isso não pode ser esquecido"
- significa: promover aprendizado recorrente para camada recuperável
- porta de entrada: `cerebro/operacional/` + memória do dia + arquivo operacional correspondente
- output esperado: memória registrada, porta única atualizada e chance menor de repetição do erro

## 12. "me mostra o que ficou pendente" / "o que ficou aberto?"
- significa: resgatar backlog que pode ter se perdido entre tópicos e erros
- porta de entrada: `cerebro/empresa/projetos/pendencias.md`, relatórios HTML recentes e memória recente
- output esperado: lista objetiva de pendências reais, sem esconder item esquecido

## 13. "avalia essa ferramenta" / "olha essa skill/repo/MCP" / "isso serve para o IVS?"
- significa: avaliar tecnologia externa, skill, repositório, MCP ou ferramenta antes de homologar uso na operação IVS
- porta de entrada: `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-FONTES-E-FERRAMENTAS.md` quando envolver marketing/web; `cerebro/empresa/skills/GOVERNANCA-SKILLS.md` quando envolver skill oficial; painel único quando gerar pendência
- regras críticas: separar teste em sandbox de adoção canônica; não expor nem reutilizar tokens recebidos por link; registrar riscos, requisitos, encaixe operacional e próximo teste mínimo
- output esperado: veredito prático, status de homologação, riscos, próximos passos e, se aprovado apenas para teste, piloto controlado

## 14. "usa/chama um subagente" / "precisa criar agentes?"
- significa: decidir se João resolve sozinho ou aciona uma especialidade sob demanda, sem criar agente fixo desnecessário
- porta de entrada: `cerebro/areas/marketing/agentes/agente-reels-intel/JOAO-SUBAGENTES-SOB-DEMANDA.md`
- regra crítica: fluxo padrão `Tiaro → João → subagente sob demanda → João → Tiaro`; subagente não fala direto com Tiaro salvo autorização explícita
- output esperado: briefing controlado ao subagente, validação do João e resposta final consolidada

## 15. "passa pelo Conselho Growth" / "o conselho foi cirúrgico"
- significa: submeter peça, apresentação, copy ou fluxo comercial a uma leitura estratégica de conversão premium antes de implementação
- porta de entrada: skill/agente `conselho-growth-vital-slim` quando disponível + fonte operacional do material analisado
- regra crítica: conselho gera direção, riscos e critérios de aceite; implementação/canonização só ocorre após validação e, se estrutural, RC-25/Graphify
- output esperado: diagnóstico objetivo, alavancas de conversão, cortes/adaptações, objeções, SPIN/CTA e briefing executável

## 16. "gera uma apresentação detalhada em HTML para o Claude Code" / "manda para o Claude desenvolver"
- significa: transformar decisão estratégica em especificação HTML/CSS/JS detalhada para implementação por ferramenta/coder externo
- porta de entrada: `skills/geracao-apresentacao-paciente/SKILL.md` + arquivos do paciente/material-base aprovados
- regras críticas: preservar dados clínicos/exames/questionário como base argumentativa para a médica; não prometer resultado; separar copy médica, layout, componentes e critérios de aceite
- output esperado: HTML/spec pronto para desenvolvimento, com instruções cirúrgicas, checklist e pontos de validação

## 17. "enxuga essa apresentação" / "está prolixa"
- significa: reduzir redundância sem perder tese clínica, condução médica nem percepção premium
- porta de entrada: `skills/geracao-apresentacao-paciente/SKILL.md`
- regra crítica: cortar antes de adicionar; manter perguntas SPIN e alavancas clínicas em frases úteis para consulta
- output esperado: cortes por seção, nova arquitetura enxuta e instrução objetiva para a próxima versão
