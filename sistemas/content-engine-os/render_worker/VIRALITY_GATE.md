# GATE OBRIGATORIO DE VIRALIZACAO — Content Engine OS

Regra do Tiaro (2026-06-25): **TODA criacao do Content Engine OS (reel/video) DEVE passar pelo
Virality Predictor ANTES da aprovacao de publicacao pelo usuario do sistema.**

## Ferramenta
- Modelo Higgsfield **`brain_activity`** (Virality Predictor), via CLI. Saida: `global_scores_by_frame`
  (atencao/engajamento neuro previsto por segundo, 0-1) + mapa 3D de atencao.
- **Limite: video <= 16s** (o gate usa os primeiros 16s — hook + retencao inicial, que definem viralizacao).

## Modulo
`render_worker/virality_predictor.py` -> `predict_virality(video) -> {index_0_100, verdict, hook_score,
avg, peak, peak_s, weak_seconds[], retention_delta, advice[], scores[], raw_json_path}`. Retry em 502.

## Fluxo obrigatorio (apos render, antes de aprovar)
1. Render finaliza -> roda `predict_virality` -> grava `virality_raw.json` + metricas no registro da criacao.
2. A tela de aprovacao do usuario MOSTRA: indice 0-100, curva por segundo, hook_score, segundos fracos e os `advice`.
3. Usuario aprova/reprova **vendo** a predicao. (Compliance continua vencendo compliance vs viralizacao.)

## Onde plugar
- `render_daemon.py` / pipeline de reel: chamar no fim do render e anexar ao status (ex.: 'aguardando_aprovacao' so com virality presente).
- API de aprovacao: bloquear publish sem registro de virality.

Validado em reel_dra_v12 (indice 75, hook fraco 0.30, pico 0.385 @10s).
