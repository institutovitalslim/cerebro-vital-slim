# Checklist Rápido — Escolha de Provider de Mídia IVS

> Consulta curta antes de gerar imagem, vídeo ou voz.
>
> Índice central relacionado:
> - `cerebro/areas/marketing/governanca-visual-ivs-index.md`

## 1. Antes de qualquer geração

Perguntar:
- isso é **protótipo** ou **peça final**?
- há **foto da Dra.**, **paciente** ou **conteúdo sensível**?
- o objetivo é **qualidade máxima**, **velocidade** ou **baixo custo**?
- isso vai para **publicação** ou é só teste interno?

---

## 2. Imagem

### Use **Z-Image-Turbo** se:
- é rascunho
- é conceito
- é mockup
- é teste rápido
- custo zero importa mais que acabamento final

### Use **Google / NanoBanana2** se:
- precisa de estética premium
- precisa de realismo melhor
- a imagem está perto da versão final
- a percepção de marca importa muito

### Use **OpenAI** se:
- precisa de output final consistente
- quer mais previsibilidade de produção
- a peça é final ou quase final

### Nunca usar **Z-Image-Turbo** se:
- tiver foto da Dra.
- tiver paciente
- tiver contexto médico sensível
- for arte final premium

---

## 3. Vídeo

### Use **Qwen / Wan** se:
- for reel produzido
- precisar de clip com movimento real
- entrar no pipeline oficial do IVS

### Regra obrigatória
- **1 cena = 1 clip = 1 fala = 1 legenda**

### Reprovar imediatamente se:
- a legenda estiver corrida no vídeo inteiro
- o vídeo final não estiver visível
- a sincronização estiver ruim

---

## 4. Voz

### Use **ElevenLabs** se:
- a locução for final
- o vídeo precisar soar premium
- a fala precisar sincronizar bem com as legendas

### Use **gTTS** só se:
- for contingência
- ElevenLabs estiver indisponível

---

## 5. Ferramenta nova / provider novo

Antes de adotar, responder:
1. resolve um problema real do IVS?
2. melhora qualidade, custo ou velocidade sem subir muito o risco?
3. é ferramenta pequena ou produto inteiro?
4. respeita compliance e marca?
5. reduz trabalho ou cria mais manutenção?

### Sinais de alerta
- monorepo enorme
- submódulos obrigatórios
- Electron sem necessidade
- branding “sem filtros / sem guardrails”
- promessa vaga de privacidade
- hype maior que utilidade real

---

## 6. Regra final

Não escolher provider por hype.
Escolher por:
- encaixe operacional
- compliance
- qualidade percebida
- previsibilidade
- simplicidade
