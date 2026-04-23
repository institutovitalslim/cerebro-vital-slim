# Trigger de Videos para Clara - Instituto Vital Slim

## Como usar

Quando Clara estiver conversando com um lead, ela deve:

1. **Ler a ultima mensagem do lead**
2. **Verificar palavras-chave** na mensagem
3. **Decidir se envia video**
4. **Personalizar mensagem** com nome do lead
5. **Registrar envio** para nao reenviar

---

## Palavras-chave por video

### Video 1: Primeira Consulta
**Arquivo original:** `file_506---d9124a51-4880-4143-b536-866a2fbda5ab.mp4`
**Local:** `/root/.openclaw/media/inbound/`

**Palavras-chave (enviar quando o lead disser):**
- "como funciona", "o que voces fazem", "como e a consulta"
- "o que inclui", "como e o tratamento", "especialidade"
- "endocrino", "emagrecimento", "perder peso", "metabolismo", "hormonios"
- "primeira vez", "nunca fui", "quero conhecer", "quero saber mais"
- "e caro", "qual o valor", "quanto custa", "preco", "investimento"
- "diferenca", "melhor", "outras clinicas", "ja tentei"

**Mensagem padrao:**
```
Oi [NOME]! A Dra. Daniely faz uma consulta diferente porque olha para voce como um todo — energia, sono, metabolismo, hormonios. Nada de protocolo pronto. Cada paciente tem um plano unico.

Da uma olhada em como funciona:
[enviar video]

Me conta: qual seu maior objetivo hoje?
```

---

### Video 2: Bioimpedancia
**Arquivo original:** `file_505---64879356-cf76-4a10-95e2-7bcc31b80b6c.mp4`
**Local:** `/root/.openclaw/media/inbound/`

**Palavras-chave (enviar quando o lead disser):**
- "exame", "avaliacao", "bioimpedancia", "composicao corporal"
- "gordura", "massa magra", "massa muscular", "hidratacao"
- "peso", "balanca", "medir", "analise", "resultados"
- "gordura visceral", "metabolismo basal"
- "preciso fazer exame", "quais exames", "tenho exames"
- "oque levar", "como me preparar"

**Mensagem padrao:**
```
Oi [NOME]! Durante a consulta faremos um exame de bioimpedancia — uma tecnologia avancada que mede gordura visceral, massa muscular, hidratacao celular e muito mais. Voce recebe os resultados em tempo real no celular e acompanha sua evolucao.

Da uma olhada no exame:
[enviar video]

Tem alguma duvida sobre o exame?
```

**Mensagem quando ja agendou:**
```
Ola [NOME]! Sua consulta esta agendada. Vai ser um prazer te receber.

Durante a consulta faremos um exame de bioimpedancia — uma tecnologia avancada que mede gordura visceral, massa muscular, hidratacao celular e muito mais. Voce recebe os resultados em tempo real no celular e acompanha sua evolucao.

Da uma olhada no exame:
[enviar video]

Traga exames recentes se tiver. Ate la!
```

---

## Regras importantes

### NAO ENVIAR quando:
- Lead ja recebeu o mesmo video antes (verificar historico)
- Lead esta respondendo a uma pergunta direta (ex: "qual seu peso?")
- Lead marcou horario e ja recebeu video de bioimpedancia
- Lead disse "nao" ou "obrigado, vou pensar" (respeitar)

### SEMPRE fazer:
- Personalizar com nome do lead
- Adicionar texto antes e depois do video (nunca so o video)
- Fazer uma pergunta no final para manter conversa
- Registrar que enviou o video (para nao reenviar)

---

## Exemplos de conversas

### Exemplo 1 - Lead novo
**Lead:** "Oi, quero saber mais sobre o tratamento de voces"
**Clara:** Detectou "quero saber mais" + "tratamento" → ENVIAR video de Primeira Consulta

### Exemplo 2 - Lead com duvida de exame
**Lead:** "O exame de bioimpedancia mede o que exatamente?"
**Clara:** Detectou "bioimpedancia" + "mede" + "exame" → ENVIAR video de Bioimpedancia

### Exemplo 3 - Lead agendou
**Lead:** "Agendei para segunda, preciso levar algo?"
**Clara:** Detectou "agendei" + "levar" → ENVIAR video de Bioimpedancia (versao pre-consulta)

### Exemplo 4 - Lead acha caro
**Lead:** "E caro? Quanto custa a consulta?"
**Clara:** Detectou "caro" + "custa" → ENVIAR video de Primeira Consulta (mostra valor)

---

## Registro de envios

Manter em: `memory/2026-04-23-videos-enviados.md`

Formato:
```
## 2026-04-23
- [10:00] Maria Silva - Primeira Consulta - Enviado
- [10:30] Joao Santos - Bioimpedancia - Enviado
- [11:00] Ana Costa - Primeira Consulta - JA TINHA RECEBIDO (nao reenviado)
```
