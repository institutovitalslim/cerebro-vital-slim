# Skill: ana-google (Gemini — conta institutovitalslim@gmail.com)

Resumos científicos e gráficos via API Google Gemini (chave renovada, conta institutovitalslim).
A Ana usa esta skill para sintetizar pesquisas e gerar gráficos de dados de estudos.

## Comandos
- `python3 skills/ana-google/ana_google.py summarize <arquivo|->` — resumo científico estruturado (tema, achados, evidência, aplicação IVS, ressalvas).
- `python3 skills/ana-google/ana_google.py graph <arquivo|-> [saida.png]` — extrai dados numéricos e gera gráfico PNG (bar/line).
- `python3 skills/ana-google/ana_google.py check` — testa o acesso Gemini.

## Notas
- Chave resolvida de `/root/.openclaw/.env.runtime` / `.env` (GOOGLE_API_KEY/GEMINI_API_KEY) — conta institutovitalslim@gmail.com.
- Modelos: gemini-2.5-flash (padrão) → 2.5-pro → 2.0-flash.
- Se a API falhar, fallback = sessão logada no Chrome da VPS (institutovitalslim) via CDP. NotebookLM (sem API pública) usa essa rota de navegador.
