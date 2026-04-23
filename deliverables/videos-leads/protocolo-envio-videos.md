# Protocolo de Envio de Videos - Instituto Vital Slim

## Videos disponiveis

| Video | Arquivo | Momento de Envio |
|-------|---------|------------------|
| Exame de Bioimpedancia | `bioimpedancia/exame-bioimpedancia.mp4` | Apos agendamento da 1a consulta, antes do exame |
| Primeira Consulta | `primeira-consulta/primeira-consulta-vsl.mp4` | Quando o lead entra em contato e pergunta como funciona |

---

## FLUXO 1 - Lead novo entra em contato

**Gatilho:** Lead manda "Oi, quero saber mais" ou pergunta como funciona a consulta

**Acao:**
1. Responder com texto explicando brevemente a abordagem holistica
2. Enviar video: `primeira-consulta-vsl.mp4`
3. Perguntar: "Qual seu maior objetivo hoje?"

**Exemplo de mensagem:**
> Oi! A Dra. Daniely faz uma consulta diferente porque olha para voce como um todo — energia, sono, metabolismo, hormonios. Nada de protocolo pronto. Cada paciente tem um plano unico.
> 
> Da uma olhada em como funciona:
> [enviar video]
> 
> Me conta: qual seu maior objetivo hoje?

---

## FLUXO 2 - Lead ja agendou a primeira consulta

**Gatilho:** Paciente confirma agendamento da 1a consulta

**Acao:**
1. Enviar mensagem de boas-vindas com orientacoes
2. Enviar video: `exame-bioimpedancia.mp4`
3. Explicar que o exame sera feito na consulta e os beneficios

**Exemplo de mensagem:**
> Ola! Sua consulta esta agendada. Vai ser um prazer te receber.
> 
> Durante a consulta faremos um exame de bioimpedancia — uma tecnologia avancada que mede gordura visceral, massa muscular, hidratacao celular e muito mais. Voce recebe os resultados em tempo real no celular e acompanha sua evolucao.
> 
> Da uma olhada no exame:
> [enviar video]
> 
> Traga exames recentes se tiver. Ate la!

---

## FLUXO 3 - Lead pergunta especificamente sobre exames/avaliacao

**Gatilho:** "O que voces avaliam?" / "Como e o exame?" / "Tem bioimpedancia?"

**Acao:**
1. Responder diretamente
2. Enviar video: `exame-bioimpedancia.mp4`

---

## FLUXO 4 - Lead com objecao de preco ou duvida sobre valor

**Gatilho:** "E caro?" / "O que inclui?" / "Por que o valor?"

**Acao:**
1. NAO enviar video de preco (nao existe)
2. Enviar video: `primeira-consulta-vsl.mp4` (mostra valor/diferencial)
3. Reforcar personalizacao e tecnologia

---

## Onde estao os arquivos

```
/root/cerebro-vital-slim/deliverables/videos-leads/
├── bioimpedancia/
│   ├── exame-bioimpedancia.mp4
│   └── thumbnail.jpg
├── primeira-consulta/
│   ├── primeira-consulta-vsl.mp4
│   └── thumbnail.jpg
└── protocolo-envio-videos.md  (este arquivo)
```

---

## Regras de ouro

1. **NUNCA enviar video sem texto** — sempre acompanhar com mensagem contextual
2. **Um video por vez** — nao bombardear o paciente
3. **Personalizar** — usar o nome do paciente quando possivel
4. **Perguntar algo depois** — sempre deixar uma pergunta para manter conversa
5. **Nao enviar para quem ja viu** — se o paciente ja recebeu, nao reenviar

---

## Registro de envios

Manter log em: `memory/2026-04-23-videos-enviados.md`

Formato:
```
- [DATA] [NOME_PACIENTE] [VIDEO_ENVIADO] [FLUXO] [RESULTADO]
```
