# HomeMatch Club — Prototipagem UX
## Troca de Hospedagem Premium (Tinder-style)

---

## Conceito Central

**NÃO é imobiliária. É troca de hospedagem entre membros de um clube exclusivo.**

Você entra, cadastra sua casa com fotos e disponibilidade, diz onde quer ir, e o app te mostra cards de imóveis de outros membros. Swipe pro match, conversa, troca confirmada.

---

## Fluxo do Usuário

### 1. Onboarding (3 passos rápidos)
- **Passo 1:** Dados básicos, verificação de identidade
- **Passo 2:** Cadastrar minha casa (fotos, descrição, regras)
- **Passo 3:** Escolher destinos de interesse + datas disponíveis

### 2. Feed Principal — Swipe Cards
Tela principal é **UM CARD POR VEZ**, ocupando a tela inteira.

**Card mostra:**
- Foto grande da casa (galeria swipeable)
- Localização (cidade, país)
- Período disponível
- Quantos quartos/banheiros
- Destaques (piscina, vista, praia, etc.)
- Foto do proprietário + nome (confiança)
- Badge de reputação (estrelas, nível)

**Ações no card:**
- ❌ Swipe esquerda / botão X — "Não interessa"
- 💚 Swipe direita / botão coração — "Quero trocar"
- ℹ️ Swipe pra cima / botão info — "Ver detalhes completos"

### 3. Detalhes Completos (tela full)
Quando o usuário desliza pra cima ou toca em detalhes:
- Galeria completa de fotos
- Descrição da casa
- Regras da casa
- Reputação do proprietário (reviews passadas)
- Compatibilidade de datas
- Botão "Propor Troca" (equivale ao Super Like — notifica direto)

### 4. Match!
Quando ambos deram like:
- **Tela de match animada** (igual Tinder — fogos, confetes, celebração)
- Mostra a casa dos dois lado a lado
- Botão "Iniciar Conversa" (abre chat automaticamente)

### 5. Chat
Chat integrado, sem sair do app:
- Mensagens de texto
- Compartilhar datas disponíveis
- Enviar proposta formal (botão "Propor datas" que gera um card de proposta)
- Acordo mútuo = troca confirmada

### 6. Confirmação da Troca
- Tela de resumo: minha casa ↔ casa do outro
- Datas combinadas
- Checklist de regras aceitas
- Confirmação mútua

### 7. Durante a Hospedagem
- Botão de emergência / suporte
- Check-in virtual
- Notificações ("Boa estadia! Lembrete das regras")

### 8. Após a Troca
- Avaliação mútua (higiene, respeito, comunicação, experiência)
- Review público (anônimo para reputação)
- Pontos de gamificação

---

## Gamificação

### Sistema de Pontos (Club Points)
- Cadastrar casa: +50 pts
- Completar perfil: +30 pts
- Cada like dado: +1 pt
- Cada match: +10 pts
- Troca concluída: +100 pts
- Receber boa avaliação: +20 pts
- Indicar amigo que entra: +25 pts

### Níveis (Badges Visuais)
- 🥉 Membro Bronze (0-200 pts)
- 🥈 Membro Prata (200-500 pts)
- 🥇 Membro Ouro (500-1000 pts)
- 💎 Membro Diamante (1000+ pts)
- 👑 Host Elite (5+ trocas + 4.8★ média)

### Streaks
- "Membro Ativo" — logou 7 dias seguidos → badge especial
- "Viajante Frequente" — 3+ trocas no ano → privilégios
- "Anfitrião Top" — 100% de avaliações positivas em 5 trocas

### Recompensas Visuais
- Frames exclusivos no avatar
- Coroa/borda dourada no card da casa
- Destaque no feed (imóveis de membros Elite aparecem primeiro)
- Acesso antecipado a novos destinos

### Leaderboard (opcional)
- Ranking de membros mais ativos
- Ranking de destinos mais trocados
- Ranking de melhores anfitriões

---

## Estrutura de Dados (Simplificada)

### Membro
```
- id
- nome, foto, idade, profissão (opcional)
- verificação (identidade, propriedade)
- nível/badge
- pontos totais
- casa (referência)
- destinos de interesse[]
- likes dados[]
- likes recebidos[]
- matches[]
- avaliação média (1-5 estrelas)
```

### Casa
```
- id
- proprietário (referência)
- fotos[]
- título (ex: "Casa de praia com vista")
- descrição
- cidade, país
- tipo (casa, apto, chalé, etc.)
- quartos, banheiros, vagas
- regras
- comodidades[]
- datas disponíveis[]
- status (disponível, em troca, indisponível)
```

### Match
```
- id
- membro A, membro B
- casa A, casa B
- status (match, conversando, proposta, confirmado, concluído)
- proposta de datas
- chats[]
```

---

## Telas Principais (Wireframes)

### Tela 1: Splash / Login
- Logo HomeMatch Club
- "Troca de hospedagem entre pessoas certas"
- Entrar com email/Google/Apple

### Tela 2: Onboarding — Minha Casa
- Upload de fotos
- Descrição em vídeo (opcional, tipo TikTok Reels)
- O que oferece (WiFi, piscina, cozinha equipada)
- Regras importantes

### Tela 3: Onboarding — Destinos
- Buscar cidades/países
- Selecionar "Quero ir aqui"
- Escolher datas de disponibilidade (calendário)

### Tela 4: Feed Principal (TINDER-STYLE)
- Card grande ocupando 80% da tela
- Foto da casa (swipe pra ver mais)
- Info resumida
- 3 botões: ❌ | ℹ️ | 💚
- Barra inferior com: Feed | Matches | Mensagens | Perfil

### Tela 5: Detalhes (Swipe pra cima no card)
- Galeria de fotos full screen
- Descrição completa
- Regras da casa
- Perfil do proprietário (foto, nome, avaliações)
- Botão "Propor Troca" (destaque)

### Tela 6: Tela de Match
- Animação de celebração
- Casas dos dois lado a lado
- "Vocês combinam! Agora conversem para alinhar os detalhes."
- Botão "Abrir Chat" (grande, verde)

### Tela 7: Chat
- Interface tipo WhatsApp/Telegram
- Bolhas de mensagem
- Botão "Enviar Proposta" → abre modal com datas
- Quando ambos confirmam → troca confirmada

### Tela 8: Perfil
- Foto, nome, nível/badge
- Minha casa (miniatura, clica pra editar)
- Pontuação e progresso pro próximo nível
- Histórico de trocas
- Configurações

### Tela 9: Matches
- Lista de matches (foto da pessoa + casa)
- Status de cada um (novo match, conversando, proposta enviada, confirmado)
- Badge de notificação quando tem mensagem nova

---

## Diferença Chave vs. Tinder

| Aspecto | Tinder | HomeMatch Club |
|---------|--------|----------------|
| Card principal | Foto da pessoa | Foto da CASA |
| Match | Pessoa ↔ Pessoa | Casa A ↔ Casa B |
| Chat por | Interesse romântico | Troca de hospedagem |
| Info extra | Bio, idade, distância | Regras da casa, datas, comodidades |
| Pós-match | Marcar encontro | Confirmar datas e regras |
| Gamificação | Super Like, Boost | Pontos, níveis, badges |

---

## Próximos Passos

1. **[COMPLETO]** Documento de prototipagem UX
2. Gerar protótipos visuais (mockups) das telas principais
3. Validação do Tiaro
4. Construção MVP com fluxo completo
