# HomeMatch Club — Arquitetura Técnica
## Troca de Hospedagem com Matching Bidirecional

---

## Lógica Central: Matching Bidirecional

### Regra de Ouro
```
Casa A (Cidade X) quer ir para Cidade Y
Casa B (Cidade Y) quer ir para Cidade X
DATAS COMPATÍVEIS
→ MATCH POTENCIAL 💚
```

### Algoritmo de Compatibilidade
```typescript
function calcularCompatibilidade(casaA: Casa, casaB: Casa): Score {
  let score = 0;
  
  // 1. Compatibilidade de localização (PESO 50%)
  if (casaA.localizacao === casaB.destinoDesejado && 
      casaB.localizacao === casaA.destinoDesejado) {
    score += 50; // DESTINO PERFEITO
  }
  
  // 2. Compatibilidade de datas (PESO 30%)
  const intersecaoDatas = intersectarDatas(casaA.datasDisponiveis, casaB.datasDisponiveis);
  if (intersecaoDatas.dias >= 3) score += 30;
  else if (intersecaoDatas.dias >= 1) score += 15;
  
  // 3. Compatibilidade de regras (PESO 20%)
  if (regrasCompativeis(casaA.regras, casaB.regras)) score += 20;
  
  return score; // 0-100
}
```

### Ranking no Feed
- Score 80-100: "💚 Troca Perfeita" — aparece primeiro
- Score 50-79: "⭐ Match Potencial" — aparece segundo
- Score < 50: Não aparece no feed principal (apenas em busca)

---

## Estrutura de Dados

### Membro
```typescript
interface Membro {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  foto: string;
  idade: number;
  profissao?: string;
  bio?: string;
  
  // Verificação
  verificado: boolean;
  docVerificado: boolean;
  casaVerificada: boolean;
  
  // Gamificação
  nivel: 'bronze' | 'prata' | 'ouro' | 'diamante' | 'elite';
  pontos: number;
  trocasConcluidas: number;
  avaliacaoMedia: number; // 1-5 estrelas
  
  // Preferências
  destinosInteresse: string[]; // cidades
  datasDisponiveis: DateRange[];
  
  // Relações
  casaId: string;
  likesDados: string[]; // ids de casas
  matches: string[]; // ids de matches
}
```

### Casa
```typescript
interface Casa {
  id: string;
  membroId: string;
  
  // Localização
  cidade: string;
  estado: string;
  pais: string;
  coordenadas?: { lat: number; lng: number };
  
  // Fotos
  fotos: string[];
  fotoDestaque: string;
  
  // Detalhes
  titulo: string;
  descricao: string;
  tipo: 'casa' | 'apartamento' | 'chalé' | 'loft' | 'vila';
  quartos: number;
  banheiros: number;
  vagas: number;
  area?: number;
  
  // Comodidades
  comodidades: string[]; // WiFi, Piscina, ArCondicionado, etc.
  
  // Regras
  regras: {
    aceitaPets: boolean;
    aceitaCriancas: boolean;
    permiteFumar: boolean;
    limiteHospedes: number;
    checkIn: string;
    checkOut: string;
    outrasRegras?: string;
  };
  
  // Disponibilidade
  datasDisponiveis: DateRange[];
  datasIndisponiveis: DateRange[]; // já reservadas/em troca
  
  // Status
  status: 'disponivel' | 'em_troca' | 'indisponivel';
}
```

### Match
```typescript
interface Match {
  id: string;
  membroAId: string;
  membroBId: string;
  casaAId: string;
  casaBId: string;
  
  // Status
  status: 'match' | 'conversando' | 'proposta_enviada' | 'confirmado' | 'em_andamento' | 'concluido' | 'cancelado';
  
  // Datas combinadas
  dataInicio: Date;
  dataFim: Date;
  
  // Proposta
  proposta?: {
    propostoPor: string;
    dataInicio: Date;
    dataFim: Date;
    notas: string;
    aceitoPorOutro: boolean;
  };
  
  // Chat
  mensagens: Mensagem[];
  
  // Timeline
  criadoEm: Date;
  confirmadoEm?: Date;
  concluidoEm?: Date;
}
```

### Mensagem
```typescript
interface Mensagem {
  id: string;
  matchId: string;
  remetenteId: string;
  tipo: 'texto' | 'proposta' | 'sistema';
  conteudo: string;
  timestamp: Date;
  lida: boolean;
}
```

---

## Fluxo de Dados

### Cadastro → Feed
```
Membro cadastra casa → Define destinos de interesse → Define datas disponíveis
→ Algoritmo calcula compatibilidade com todas as casas cadastradas
→ Feed é ordenado por score de compatibilidade
```

### Like → Match
```
Membro A dá like na Casa B
→ Sistema verifica se Membro B já deu like na Casa A
→ SE SIM: Cria Match, abre chat
→ SE NÃO: Registra like, notifica Membro B ("Alguém curtiu sua casa!")
```

### Chat → Proposta → Confirmação
```
Membros conversam no chat
→ Membro A envia proposta formal (datas, notas)
→ Membro B aceita/recusa/contrapropõe
→ Quando ambos aceitam: status = "confirmado"
→ Casas ficam "em_troca" nas datas
→ Notificações de check-in no dia
```

---

## Monetização (Freemium)

### Free
- 5 likes/dia
- 1 destino de interesse
- Chat básico
- Feed padrão

### Plus (R$ 29/mês)
- Likes ilimitados
- 5 destinos de interesse
- Super Match (notifica antes do match)
- Prioridade no feed
- Filtros avançados

### Elite (R$ 79/mês)
- Tudo do Plus
- Destinos ilimitados
- Ver quem curtiu sua casa
- Badge Elite
- Suporte prioritário
- Acesso antecipado

### À la carte
- Boost (24h destaque): R$ 19
- Super Match avulso: R$ 9
- Verificação Expressa: R$ 49

---

## Gamificação

### Pontos
| Ação | Pontos |
|------|--------|
| Cadastrar casa | +50 |
| Completar perfil | +30 |
| Like dado | +1 |
| Match | +10 |
| Troca concluída | +100 |
| Boa avaliação (4★+) | +20 |
| Indicar amigo (que entra) | +25 |

### Níveis
| Nível | Pontos | Benefício Visual |
|-------|--------|------------------|
| Bronze | 0-200 | Badge bronze |
| Prata | 200-500 | Badge prata + frame avatar |
| Ouro | 500-1000 | Badge ouro + destaque no feed |
| Diamante | 1000+ | Badge diamante + prioridade máxima |
| Elite | 5+ trocas + 4.8★ | Coroa dourada + acesso exclusivo |

### Streaks
- Membro Ativo: 7 dias logados → badge especial
- Viajante Frequente: 3+ trocas/ano → privilégios
- Anfitrião Top: 100% avaliações positivas em 5 trocas → destaque permanente

---

## Tech Stack Recomendada

### Frontend
- Next.js 15 + App Router (static export)
- TypeScript
- Tailwind CSS
- Framer Motion (animações de swipe/match)
- React Query (cache de dados)

### Backend/DB
- Supabase (PostgreSQL + Auth + Realtime)
- Edge Functions para matching
- Storage para fotos

### Infra
- HostGator (estático) ou VPS
- Cloudflare (CDN + SSL)
- Imgur/AWS S3 (armazenamento de imagens)

---

## Próximos Passos de Implementação

1. **MVP Core** (2 semanas)
   - Cadastro/login
   - Cadastro de casa + destinos
   - Feed com cards swipe
   - Like/match básico
   - Chat simples

2. **Matching Inteligente** (1 semana)
   - Algoritmo de compatibilidade
   - Ranking no feed
   - Filtros

3. **Gamificação** (1 semana)
   - Pontos e níveis
   - Badges visuais
   - Leaderboard

4. **Monetização** (1 semana)
   - Planos Plus/Elite
   - Super Match, Boost
   - Stripe/PagSeguro

5. **Polimento** (1 semana)
   - Animações de match
   - Push notifications
   - Offline support
   - Performance
