# AUDITORIA: Generative-Media-Skills (SamurAIGPT)
**Repositório:** https://github.com/SamurAIGPT/Generative-Media-Skills
**Data:** 2026-04-26
**Solicitante:** Tiaro F. Neves
**Auditor:** Clara (VPS)

---

## 1. O QUE É

Biblioteca de skills para agents AI (Claude Code, Cursor, Gemini CLI) que permite geração multimídia (imagem, vídeo, áudio, lip sync) via API paga **muapi.ai**.

### Capacidades anunciadas:
- 100+ modelos (Flux, Midjourney v7, Kling 3.0, Veo3, Nano Banana, Wan 2.2, etc.)
- Text-to-image, image-to-video, text-to-video, lip sync
- MCP server com 19 tools
- Upload de arquivos locais para CDN
- Upscale, background removal, face swap

---

## 2. ANÁLISE DE SEGURANÇA

### 2.1 Dependências Externas
| Tipo | Item | Risco |
|------|------|-------|
| CLI | `muapi-cli` (npm/pip) | **MÉDIO** — pacote externo não auditado |
| API | muapi.ai (API key) | **MÉDIO** — serviço pago, custo imprevisível |
| CDN | Upload de arquivos para muapi | **ALTO** — dados da clínica em servidor externo |
| Skills installer | `npx skills add` | **MÉDIO** — execução remota de scripts |

### 2.2 Execução de Código
- **Scripts bash** que delegam para `muapi` CLI → NÃO há eval()/exec() direto no repositório
- **MCP server** expõe 19 tools com JSON Schema → Interface bem estruturada
- **Sem código Python/JavaScript** que execute comandos de sistema arbitrários
- **Risco baixo** de injection em runtime (usa CLI interno, não shell raw)

### 2.3 Dados Sensíveis
| Cenário | Risco | Nota |
|---------|-------|------|
| Upload de foto da Dra. para geração | **ALTO** | Violação potencial de compliance CFM |
| Upload de imagens de pacientes | **CRÍTICO** | Violação LGPD e ética médica |
| API key em plain text | **MÉDIO** | Armazenada em `~/.config/muapi` |
| Logs de prompts | **MÉDIO** | Enviados para servidor externo |

### 2.4 Conteúdo "Uncensored"
- A muapi.ai é o mesmo backend do **Open-Generative-AI** (Anil Matcha)
- **Sem filtros de conteúdo** — pode gerar NSFW, violência, deepfakes
- Para uso médico/comercial: **sem garantia de compliance**

### 2.5 Supply Chain
- Repositório: `SamurAIGPT/Generative-Media-Skills` — 1.2k stars
- Mantenedor: SamurAIGPT (desenvolvedor conhecido, mas externo)
- CLI: `muapi-cli` — npm package publicado
- **Não é malware**, mas é **software não auditado** por nós

---

## 3. COMPARATIVO COM STACK ATUAL

| Capacidade | Temos já? | Via | Risco atual |
|------------|-----------|-----|-------------|
| Geração de imagem | ✅ SIM | OpenClaw nativo (OpenAI, Google) | BAIXO |
| Nano Banana | ✅ SIM | OpenClaw nativo (Google) | BAIXO |
| Geração de vídeo | ✅ SIM | OpenClaw nativo (Wan 2.2) | BAIXO |
| Geração de música | ✅ SIM | OpenClaw nativo (music_generate) | BAIXO |
| Text-to-speech | ✅ SIM | ElevenLabs (própria conta) | BAIXO |
| Lip sync | ❌ NÃO | — | — |
| Face swap | ❌ NÃO | — | — |
| Upscale | ⚠️ LIMITADO | image_generate | BAIXO |
| Background removal | ❌ NÃO | — | — |

**Conclusão:** A skill acrescenta **lip sync, face swap e background removal** — capacidades que não temos. Mas essas capacidades são **irrelevantes para o Instituto Vital Slim** (médico, clínica de emagrecimento).

---

## 4. CUSTO

| Modelo | Custo aproximado (muapi.ai) |
|--------|---------------------------|
| Flux Dev | $0.003/imagem |
| Kling Pro | $0.10/vídeo 5s |
| Midjourney v7 | $0.05/imagem |
| Veo3 | $0.20/vídeo 5s |

- **Sem orçamento definido** → risco de gasto imprevisível
- **Sem rate limiting** no script → pode gerar custo alto acidentalmente

---

## 5. REPUTAÇÃO DO PROJETO

| Métrica | Valor |
|---------|-------|
| Stars | ~1.2k |
| Forks | ~150 |
| Último commit | Abril 2026 (ativo) |
| Issues | Moderado |
| Mantenedor | SamurAIGPT — desenvolvedor legítimo (criador de vários projetos open-source AI) |
| Licença | MIT |

**Veredicto:** Projeto legítimo, mas **não essencial** para nossa operação.

---

## 6. RECOMENDAÇÃO FINAL

### ❌ NÃO INSTALAR

**Justificativa:**
1. **Não acrescenta valor operacional** — todas as capacidades relevantes já temos via OpenClaw nativo
2. **Risco de compliance** — upload de materiais médicos/fotos da Dra. para CDN externo sem controle
3. **Custo imprevisível** — API paga, sem orçamento definido
4. **Dependência extra** — mais um ponto de falha na stack
5. **Capacidades "uncensored"** — sem filtros de conteúdo, inadequado para uso médico

### Quando reconsiderar:
- Se precisarmos de **lip sync** para vídeos da Dra. (avatar virtual)
- Se precisarmos de **face swap** controlado para campanhas específicas
- Se quisermos um **upscale mais barato** que o atual
- Após **auditar** o muapi-cli e ter orçamento definido

---

## 7. ALTERNATIVAS SEGURAS

| Necessidade | Solução atual | Risco |
|-------------|---------------|-------|
| Geração de imagem | OpenClaw nativo (OpenAI/Google) | BAIXO |
| Geração de vídeo | OpenClaw nativo (Wan 2.2) | BAIXO |
| Geração de áudio | ElevenLabs (própria conta) | BAIXO |
| Background removal | Photoshop manual ou Remove.bg (paga) | BAIXO |
| Upscale | image_generate com size maior | BAIXO |

---

**Veredicto final:** Skill legítima, mas **desnecessária e potencialmente arriscada** para nosso contexto médico. Não recomendo instalação.

**Auditor:** Clara
**Data:** 2026-04-26