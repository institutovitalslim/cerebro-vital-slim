# Graph Report - 2026-05-22  (2026-05-22)

## Corpus Check
- 1 files · ~464 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 46 nodes · 48 edges · 11 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]

## God Nodes (most connected - your core abstractions)
1. `x_twitter` - 9 edges
2. `ClaraQADiarioConversao20260522` - 7 edges
3. `instagram_manha` - 4 edges
4. `instagram_tarde` - 4 edges
5. `revisao` - 4 edges
6. `whatsapp-current` - 4 edges
7. `whatsapp-historical` - 4 edges
8. `youtube` - 4 edges
9. `If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof 5 days ago and stil` - 2 edges
10. `Join Let’s Talk Service for a breakdown of the new “Set Appointment” feature and how it can help position your business as the FIRST choice servicer while improving the customer ex` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Clara WhatsApp` ----> `instagram_manha`  [EXTRACTED]
   → raw/latest-instagram_manha.json  _Bridges community 0 → community 2_
- `Clara WhatsApp` ----> `revisao`  [EXTRACTED]
   → raw/latest-revisao.json  _Bridges community 0 → community 3_
- `Clara WhatsApp` ----> `x_twitter`  [EXTRACTED]
   → raw/latest-x_twitter.json  _Bridges community 0 → community 4_
- `Clara WhatsApp` ----> `youtube`  [EXTRACTED]
   → raw/latest-youtube.json  _Bridges community 0 → community 5_
- `x_twitter` ----> `If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof 5 days ago and stil`  [EXTRACTED]
  raw/latest-x_twitter.json → raw/latest-x_twitter.json  _Bridges community 4 → community 6_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.31
Nodes (9): Agendamento premium de pacientes/leads, Clara WhatsApp, Conselho Growth, padrões de conversa reais para melhorar agendamento da Clara sem expor PII, WhatsApp IVS via planilha de conversas, latest-evidence-gate, whatsapp-current, whatsapp-historical (+1 more)

### Community 1 - "Community 1"
Cohesion: 0.25
Nodes (2): ClaraQADiarioConversao20260522, Graphify seed for Clara daily conversion QA 2026-05-22 01:30 UTC.

### Community 2 - "Community 2"
Cohesion: 0.29
Nodes (7): 1 insight + 1 pergunta curta de abertura + 1 frase proibida, 1 resposta ruim + 1 resposta Clara premium + 1 pergunta de avanço, Instagram, instagram_manha, instagram_tarde, SPIN, negociação, social selling ou clínica premium, vendas consultivas, WhatsApp, atendimento premium

### Community 3 - "Community 3"
Cohesion: 0.5
Nodes (4): classificar aplicar amanhã / descartar / testar 3 dias / propor memória, Revisão interna, revisao, aprendizados do dia

### Community 4 - "Community 4"
Cohesion: 0.5
Nodes (4): 1 frase curta + 1 ângulo de objeção + 1 cuidado contra agressividade, X/Twitter, x_twitter, posts de alto engajamento sobre persuasão, objeções, atendimento, negócios locais ou experiência do cliente

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (4): ideia central + aplicação WhatsApp + script antes/depois + métrica + risco, YouTube, youtube, tactical empathy customer experience premium service

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (2): If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof, If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof 5 days ago and stil

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (2): I am hiring freshers for the Customer Experience team at Shoffr. 

Our cars and our drivers are the face of Shoffr, but the CX team is the voice - the voice tha, I am hiring freshers for the Customer Experience team at Shoffr. 

Our cars and our drivers are the face of Shoffr, but the CX team is the voice - the voice that holds our guest's 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): Join Let’s Talk Service for a breakdown of the new “Set Appointment” feature and how it can help position your business as the FIRST choice servicer while impro, Join Let’s Talk Service for a breakdown of the new “Set Appointment” feature and how it can help position your business as the FIRST choice servicer while improving the customer ex

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (2): Captain Obvious Specialist in chat 👋

Hey team — just wanted to confirm:

Is this still the preferred customer experience workflow for guests after a disappoint, Captain Obvious Specialist in chat 👋

Hey team — just wanted to confirm:

Is this still the preferred customer experience workflow for guests after a disappointing booking?

Asking

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (2): Complicated booking systems slow businesses down. 🚫

With BookingDyno, you can simplify bookings, reduce manual work, and create a smoother customer experience., Complicated booking systems slow businesses down. 🚫

With BookingDyno, you can simplify bookings, reduce manual work, and create a smoother customer experience.

Less stress. Faste

## Knowledge Gaps
- **2 isolated node(s):** `Graphify seed for Clara daily conversion QA 2026-05-22 01:30 UTC.`, `latest-evidence-gate`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 1`** (8 nodes): `qa_diario_clara_20260522_graph_nodes.py`, `ClaraQADiarioConversao20260522`, `.evidencia_zero_outbound()`, `.guardrail_operacional()`, `.melhoria_abertura_vaga()`, `.melhoria_espera_sem_previsao()`, `.melhoria_sla_primeira_resposta()`, `Graphify seed for Clara daily conversion QA 2026-05-22 01:30 UTC.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (2 nodes): `If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof`, `If you are booking a hotel with MakeMyTrip, please think twice. The hotel experience was terrible, but the customer support was even worse. I shared video proof 5 days ago and stil`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (2 nodes): `I am hiring freshers for the Customer Experience team at Shoffr. 

Our cars and our drivers are the face of Shoffr, but the CX team is the voice - the voice tha`, `I am hiring freshers for the Customer Experience team at Shoffr. 

Our cars and our drivers are the face of Shoffr, but the CX team is the voice - the voice that holds our guest's `
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (2 nodes): `Join Let’s Talk Service for a breakdown of the new “Set Appointment” feature and how it can help position your business as the FIRST choice servicer while impro`, `Join Let’s Talk Service for a breakdown of the new “Set Appointment” feature and how it can help position your business as the FIRST choice servicer while improving the customer ex`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (2 nodes): `Captain Obvious Specialist in chat 👋

Hey team — just wanted to confirm:

Is this still the preferred customer experience workflow for guests after a disappoint`, `Captain Obvious Specialist in chat 👋

Hey team — just wanted to confirm:

Is this still the preferred customer experience workflow for guests after a disappointing booking?

Asking`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (2 nodes): `Complicated booking systems slow businesses down. 🚫

With BookingDyno, you can simplify bookings, reduce manual work, and create a smoother customer experience.`, `Complicated booking systems slow businesses down. 🚫

With BookingDyno, you can simplify bookings, reduce manual work, and create a smoother customer experience.

Less stress. Faste`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x_twitter` connect `Community 4` to `Community 0`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.389) - this node is a cross-community bridge._
- **Why does `revisao` connect `Community 3` to `Community 0`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `youtube` connect `Community 5` to `Community 0`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **What connects `Graphify seed for Clara daily conversion QA 2026-05-22 01:30 UTC.`, `latest-evidence-gate` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._