# -*- coding: utf-8 -*-
"""
virality_predictor.py — GATE de viralização do Content Engine OS (render_worker).

Toda criacao (reel/video) do Content Engine OS DEVE passar por aqui ANTES da aprovacao
de publicacao pelo usuario do sistema. Usa o modelo `brain_activity` ("Virality Predictor")
do Higgsfield via CLI: predicao neuro-atencional por segundo (global_scores_by_frame, 0-1).

Saida: {ok, scores[], hook_score, avg, peak, peak_s, weak_seconds[], retention_delta, index_0_100,
        verdict, advice[], raw_json_path}. Limite do modelo: video <= 16s (usa os primeiros 16s).

uso CLI: python3 virality_predictor.py <video.mp4> [out_dir]
uso lib: from virality_predictor import predict_virality
"""
from __future__ import annotations
import os, sys, json, subprocess, re


def _trim16(video: str, workdir: str) -> str:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip() or "0")
    if dur <= 16.0:
        return video
    out = os.path.join(workdir, "_viral16.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-t", "16",
                    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", out], check=True)
    return out


def _find_scores(obj):
    """acha global_scores_by_frame em qualquer nivel do JSON."""
    if isinstance(obj, dict):
        if "global_scores_by_frame" in obj and isinstance(obj["global_scores_by_frame"], list):
            return obj["global_scores_by_frame"]
        for v in obj.values():
            r = _find_scores(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_scores(v)
            if r:
                return r
    return None


def predict_virality(video: str, out_dir: str | None = None, creative_id: str | None = None, context: dict | None = None) -> dict:
    out_dir = out_dir or os.path.dirname(os.path.abspath(video))
    creative_id = creative_id or os.path.basename(os.path.dirname(os.path.abspath(video))) or "creative"
    os.makedirs(out_dir, exist_ok=True)
    clip = _trim16(video, out_dir)
    raw = None
    for _ in range(4):  # 502 e transitorios sao comuns
        p = subprocess.run(["higgsfield", "generate", "create", "brain_activity", "--video", clip,
                            "--wait", "--wait-timeout", "9m", "--json"], capture_output=True, text=True, timeout=650)
        txt = p.stdout
        m = re.search(r"(\[.*\]|\{.*\})", txt, re.S)
        if m:
            try:
                raw = json.loads(m.group(1))
                if _find_scores(raw):
                    break
            except Exception:
                pass
        if "502" not in (txt + p.stderr) and "error code" not in (txt + p.stderr):
            # erro nao-transitorio
            if raw is None:
                continue
    scores = _find_scores(raw) if raw else None
    if not scores:
        return {"ok": False, "error": "sem global_scores_by_frame", "raw": (raw or {})}

    raw_path = os.path.join(out_dir, "virality_raw.json")
    json.dump(raw, open(raw_path, "w"), ensure_ascii=False)

    n = len(scores)
    avg = sum(scores) / n
    peak = max(scores); peak_s = scores.index(peak)
    hook = sum(scores[:3]) / min(3, n)
    retention_delta = (sum(scores[-3:]) / min(3, n)) - hook
    weak = [i for i, s in enumerate(scores) if s < avg * 0.95]
    # indice relativo 0-100 (0.45 ~ topo forte de atencao neuro p/ social vertical)
    index = max(0, min(100, round((avg / 0.45) * 100)))
    if index >= 75:
        verdict = "alto"
    elif index >= 55:
        verdict = "medio"
    else:
        verdict = "baixo"

    advice = []
    if hook < avg:
        advice.append(f"Hook fraco: atencao media nos 3s iniciais ({hook:.2f}) abaixo da media ({avg:.2f}). Reforce o gancho (rosto da Dra + frase de impacto).")
    if 1 in weak or 2 in weak:
        advice.append("Queda de atencao no 2o-3o segundo: encurte a introducao / entre no problema mais rapido.")
    if retention_delta < -0.02:
        advice.append(f"Retencao cai no final ({retention_delta:+.2f}): fortaleca o trecho final/CTA (corte mais rapido, payoff visual).")
    if weak:
        advice.append("Segundos com menor atencao (revisar essas cenas/transicoes): " + ", ".join(f"{i}s" for i in weak) + ".")
    if not advice:
        advice.append("Curva de atencao estavel; teste variacoes de hook p/ subir o pico.")

    result = {"ok": True, "scores": [round(s, 3) for s in scores], "n_seconds": n,
              "hook_score": round(hook, 3), "avg": round(avg, 3), "peak": round(peak, 3), "peak_s": peak_s,
              "retention_delta": round(retention_delta, 3), "weak_seconds": weak,
              "index_0_100": index, "verdict": verdict, "advice": advice, "raw_json_path": raw_path}
    # alimenta a biblioteca de boas práticas (loop de aprendizado) — não-fatal
    try:
        from virality_library import record
        record(creative_id, result, context=context)
    except Exception as e:
        print("virality_library.record falhou (nao-fatal):", str(e)[:120])
    return result


if __name__ == "__main__":
    r = predict_virality(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(r, ensure_ascii=False, indent=2))
