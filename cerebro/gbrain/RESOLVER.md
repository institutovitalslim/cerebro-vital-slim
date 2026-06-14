# GBrain IVS — Resolver Canônico do Cérebro

Use este resolver antes de criar, mover ou promover conhecimento no cérebro.

## Ordem de decisão

1. **Regra permanente, governança, segurança, compliance ou mudança estrutural**
   - Arquivar em `cerebro/areas/governanca/` ou `cerebro/areas/_governanca/`.
   - Registrar via `cerebro/operacional/graphify-YYYY-MM-DD-*/`.

2. **Operação clínica/agenda/processo interno**
   - Arquivar em `cerebro/areas/operacoes/`.
   - Se envolver apresentação de paciente, usar os guias canônicos em `cerebro/areas/operacoes/`.

3. **Atendimento, Clara, WhatsApp, leads, fluxo comercial de paciente**
   - Arquivar em `cerebro/areas/atendimento/`.
   - Nunca acionar paciente diretamente fora do domínio da Clara.

4. **Marketing, João, Reels, anúncios, criativos, relatórios de tráfego**
   - Arquivar em `cerebro/areas/marketing/`.
   - Tópico Reels/Marketing continua domínio do João.

5. **Financeiro, Omie, boletos, conciliação, contratos operacionais**
   - Arquivar em `cerebro/areas/financeiro/`.
   - Ações financeiras complexas exigem alinhamento com Tiaro.

6. **Tecnologia, automações, agentes, skills, OpenClaw, integrações**
   - Arquivar em `cerebro/areas/tecnologia/`.
   - Runtime e credenciais não entram no cérebro; apenas mapas e playbooks sem segredo.

7. **Conhecimento institucional, histórico, marca, contexto da empresa**
   - Arquivar em `cerebro/empresa/`.

8. **Memória específica de agente**
   - Arquivar em `cerebro/agentes/<agente>/` e referenciar em `cerebro/gbrain/agents/memory-bridge.md`.

9. **Registro bruto de mudança ou implantação**
   - Arquivar em `cerebro/operacional/graphify-YYYY-MM-DD-<slug>/raw/`.

10. **Se não encaixar**
   - Criar rascunho em `cerebro/operacional/inbox-gbrain/` com status `pendente-classificacao` e abrir RC-25 para decidir.

## Regra de retrieval para agentes
Antes de responder sobre qualquer item não trivial, o agente deve:
1. consultar memória local curta;
2. consultar GBrain sidecar se houver risco de regra/processo/histórico desatualizado;
3. abrir a página canônica quando o GBrain apontar slug;
4. responder citando o caminho do cérebro quando a decisão depender de fonte canônica.

## Regra de escrita
- GBrain pode sugerir e indexar.
- A escrita canônica no cérebro continua por Graphify/RC-25.
- Nenhum agente deve deixar GBrain sobrescrever arquivos canônicos sem autorização explícita.
