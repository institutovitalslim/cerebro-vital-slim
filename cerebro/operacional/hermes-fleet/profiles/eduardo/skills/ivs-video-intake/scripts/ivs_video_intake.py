#!/usr/bin/env python3
"""IVS Video Intake — local-first video analysis scaffold.

Purpose: produce a governed intake package for Reels/ads/bugs/aulas without
sending media to external LLMs by default. It extracts metadata, representative
frames, optional transcript sidecar, audio fallback, JSON and HTML report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

REPORT_ROOT = Path("/root/.openclaw/reports/ivs-video-intake")
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
SECRET_QUERY_KEYS = {"mcp_token", "token", "access_token", "api_key", "key", "sig", "signature", "session", "sid"}
OBJECTIVE_DEFAULTS = {
    "reels": {"max_frames": 48, "resolution": 720, "label": "Reels/Conteúdo curto"},
    "ads": {"max_frames": 60, "resolution": 720, "label": "Criativo pago"},
    "bug": {"max_frames": 42, "resolution": 900, "label": "Bug/gravação de tela"},
    "aula": {"max_frames": 80, "resolution": 640, "label": "Aula/treinamento"},
    "treinamento": {"max_frames": 80, "resolution": 640, "label": "Treinamento interno"},
    "geral": {"max_frames": 50, "resolution": 720, "label": "Análise geral"},
}


def run(cmd: list[str], *, timeout: int = 300, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=capture, timeout=timeout)


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Dependência ausente: {name}. Instale antes de rodar a skill.")
    return path


def is_url(source: str) -> bool:
    p = urlparse(source)
    return p.scheme in {"http", "https"} and bool(p.netloc)


def sanitize_source(source: str) -> str:
    if not is_url(source):
        return source
    p = urlparse(source)
    safe_q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in SECRET_QUERY_KEYS]
    return urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(safe_q), ""))


def slugify(value: str, max_len: int = 80) -> str:
    value = re.sub(r"https?://", "", value, flags=re.I)
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (value or "video")[:max_len]


def parse_time(value: str | None) -> float | None:
    if not value:
        return None
    parts = str(value).strip().split(":")
    try:
        if len(parts) == 1:
            return float(parts[0])
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    except ValueError:
        pass
    raise SystemExit(f"Tempo inválido: {value!r}. Use SS, MM:SS ou HH:MM:SS.")


def fmt_time(seconds: float | int | None) -> str:
    if seconds is None:
        return "--:--"
    total = max(0, int(round(float(seconds))))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def download_if_needed(source: str, work: Path, no_download: bool = False) -> tuple[Path, dict, Path | None]:
    if not is_url(source):
        p = Path(source).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"Arquivo não encontrado: {p}")
        return p, {"source_type": "local", "title": p.name}, None
    if no_download:
        raise SystemExit("Fonte é URL, mas --no-download foi usado.")
    require_binary("yt-dlp")
    out_dir = work / "download"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(out_dir / "media.%(ext)s")
    cmd = [
        "yt-dlp", "-N", "4",
        "-f", "bv*[height<=1080]+ba/b[height<=1080]/bv+ba/b",
        "--merge-output-format", "mp4",
        "--write-info-json",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "pt,pt-BR,en,en-US,en-orig",
        "--sub-format", "vtt", "--convert-subs", "vtt",
        "--no-playlist", "-o", output_template, "--", source,
    ]
    cp = run(cmd, timeout=900, capture=True)
    videos = [p for p in out_dir.glob("media.*") if p.suffix.lower() in VIDEO_EXTS]
    if not videos:
        raise SystemExit(f"yt-dlp não gerou vídeo. exit={cp.returncode}\n{cp.stderr[-1000:]}")
    info = {"source_type": "url", "yt_dlp_exit": cp.returncode}
    info_file = out_dir / "media.info.json"
    if info_file.exists():
        try:
            raw = json.loads(info_file.read_text(encoding="utf-8"))
            info.update({k: raw.get(k) for k in ["title", "uploader", "duration", "webpage_url", "extractor_key"]})
        except Exception as exc:
            info["info_json_error"] = repr(exc)
    subs = sorted(out_dir.glob("media*.vtt"))
    subtitle = subs[0] if subs else None
    return videos[0], info, subtitle


def ffprobe(video: Path) -> dict:
    require_binary("ffprobe")
    cp = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(video)], timeout=120)
    if cp.returncode != 0:
        raise SystemExit(f"ffprobe falhou: {cp.stderr}")
    data = json.loads(cp.stdout or "{}")
    streams = data.get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format") or {}
    return {
        "duration_seconds": float(fmt.get("duration") or v.get("duration") or 0),
        "width": v.get("width"), "height": v.get("height"), "video_codec": v.get("codec_name"),
        "has_audio": bool(a), "audio_codec": (a or {}).get("codec_name"),
        "size_bytes": int(fmt.get("size") or 0), "format_name": fmt.get("format_name"),
    }


def choose_fps(duration: float, max_frames: int, focused: bool) -> tuple[float, int]:
    if duration <= 0:
        return 1.0, 1
    if focused:
        target = min(max_frames, max(10, int(min(2.0 * duration, max_frames))))
    elif duration <= 30:
        target = min(max_frames, max(18, int(duration)))
    elif duration <= 60:
        target = min(max_frames, 40)
    elif duration <= 180:
        target = min(max_frames, 55)
    elif duration <= 600:
        target = min(max_frames, 70)
    else:
        target = max_frames
    fps = min(2.0, max(0.05, target / duration))
    return fps, target


def extract_frames(video: Path, frames_dir: Path, *, fps: float, resolution: int, max_frames: int, start: float | None, end: float | None) -> list[dict]:
    require_binary("ffmpeg")
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame_*.jpg"):
        old.unlink()
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"]
    cmd += ["-i", str(video), "-vf", f"fps={fps},scale={resolution}:-2", "-frames:v", str(max_frames), "-q:v", "4", str(frames_dir / "frame_%04d.jpg")]
    cp = run(cmd, timeout=600)
    if cp.returncode != 0:
        raise SystemExit(f"ffmpeg frames falhou: {cp.stderr}")
    offset = start or 0.0
    out = []
    for i, p in enumerate(sorted(frames_dir.glob("frame_*.jpg"))):
        out.append({"index": i, "timestamp_seconds": round(offset + (i / fps), 2), "path": str(p)})
    return out


def extract_audio(video: Path, out: Path) -> str | None:
    require_binary("ffmpeg")
    cp = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(out)], timeout=600)
    return str(out) if cp.returncode == 0 and out.exists() and out.stat().st_size else None


def parse_transcript(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Lightweight VTT/SRT parser: captures timestamp lines and subsequent text.
    ts = re.compile(r"(?:(\d{2}):(\d{2}):(\d{2})[,.](\d{3})|(\d{2}):(\d{2})[,.](\d{3}))\s+-->\s+(?:(\d{2}):(\d{2}):(\d{2})[,.](\d{3})|(\d{2}):(\d{2})[,.](\d{3}))")
    tag = re.compile(r"<[^>]+>")
    lines = text.splitlines(); out = []; i = 0
    def to_sec(groups, start_idx):
        if groups[start_idx] is not None:
            return int(groups[start_idx])*3600 + int(groups[start_idx+1])*60 + int(groups[start_idx+2]) + int(groups[start_idx+3])/1000
        return int(groups[start_idx+4])*60 + int(groups[start_idx+5]) + int(groups[start_idx+6])/1000
    while i < len(lines):
        m = ts.search(lines[i])
        if not m:
            i += 1; continue
        g = m.groups(); start = to_sec(g, 0); end = to_sec(g, 7)
        i += 1; buf = []
        while i < len(lines) and lines[i].strip():
            cleaned = tag.sub("", lines[i]).strip()
            if cleaned and not cleaned.isdigit():
                buf.append(cleaned)
            i += 1
        if buf:
            out.append({"start": round(start,2), "end": round(end,2), "text": " ".join(buf)})
        i += 1
    return out


def write_reports(out_dir: Path, data: dict, transcript: list[dict], frames: list[dict]) -> tuple[Path, Path]:
    json_path = out_dir / "intake.json"
    html_path = out_dir / "relatorio.html"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    objective = data["objective"]
    meta = data["metadata"]
    frame_rows = []
    rel_prefix = ""
    for f in frames:
        p = Path(f["path"])
        try:
            src = os.path.relpath(p, html_path.parent)
        except Exception:
            src = str(p)
        frame_rows.append(f"<figure><img src='{html.escape(src)}'><figcaption>{f['index']:02d} · {fmt_time(f['timestamp_seconds'])}</figcaption></figure>")
    transcript_html = "".join(f"<p><b>{fmt_time(s['start'])}</b> {html.escape(s['text'])}</p>" for s in transcript[:80]) or "<p class='muted'>Sem transcrição automática disponível neste intake. Use o áudio extraído ou sidecar .vtt/.srt para etapa de análise textual.</p>"
    score_items = [
        "Hook visual nos 3 primeiros segundos", "Primeira frase/tensão clara", "Texto na tela legível", "Mecanismo de conversão identificado",
        "Objeção central mapeada", "Prova/autoridade sem promessa indevida", "CTA claro", "Risco Meta/CFM revisado", "Próximo corte/variação definido"
    ]
    checks = "".join(f"<li><input type='checkbox'> {html.escape(x)}</li>" for x in score_items)
    html_doc = f"""<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>IVS Video Intake</title><style>body{{font-family:Inter,Arial,sans-serif;background:#07111f;color:#e5e7eb;margin:0;padding:28px}}.wrap{{max-width:1180px;margin:auto}}.card{{background:#0f172a;border:1px solid #334155;border-radius:18px;padding:20px;margin:16px 0}}.muted{{color:#94a3b8}}code{{background:#020617;padding:2px 6px;border-radius:5px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}figure{{margin:0;background:#020617;border:1px solid #1e293b;border-radius:12px;overflow:hidden}}img{{width:100%;display:block}}figcaption{{font-size:12px;color:#cbd5e1;padding:7px}}li{{margin:6px 0}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #334155;padding:8px;text-align:left}}</style></head><body><div class='wrap'>
<h1>IVS Video Intake</h1><p class='muted'>Pacote local-first para análise governada de vídeo.</p>
<section class='card'><h2>Resumo</h2><table><tr><th>Fonte</th><td><code>{html.escape(data['source_sanitized'])}</code></td></tr><tr><th>Objetivo</th><td>{html.escape(objective)}</td></tr><tr><th>Duração</th><td>{fmt_time(meta.get('duration_seconds'))} ({meta.get('duration_seconds',0):.1f}s)</td></tr><tr><th>Resolução</th><td>{meta.get('width')}x{meta.get('height')}</td></tr><tr><th>Áudio</th><td>{'sim' if meta.get('has_audio') else 'não'}</td></tr><tr><th>Frames</th><td>{len(frames)}</td></tr></table></section>
<section class='card'><h2>Checklist de análise IVS</h2><ul>{checks}</ul></section>
<section class='card'><h2>Frames extraídos</h2><div class='grid'>{''.join(frame_rows)}</div></section>
<section class='card'><h2>Transcrição / falas</h2>{transcript_html}</section>
<section class='card'><h2>Campos para João/Maria preencher</h2><ul><li><b>Hook real:</b></li><li><b>Mecanismo vencedor:</b></li><li><b>Objeção quebrada:</b></li><li><b>Prova usada:</b></li><li><b>Risco compliance:</b></li><li><b>Variações recomendadas:</b></li></ul></section>
</div></body></html>"""
    html_path.write_text(html_doc, encoding="utf-8")
    return json_path, html_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Cria intake IVS de vídeo: metadados, frames, transcript sidecar, áudio e relatório HTML/JSON.")
    ap.add_argument("source", help="URL pública suportada por yt-dlp ou caminho local de vídeo")
    ap.add_argument("--objective", choices=sorted(OBJECTIVE_DEFAULTS), default="reels")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--resolution", type=int, default=None)
    ap.add_argument("--transcript-file", default=None, help="Arquivo .vtt/.srt opcional")
    ap.add_argument("--no-download", action="store_true")
    args = ap.parse_args()

    start = parse_time(args.start); end = parse_time(args.end)
    if start is not None and end is not None and end <= start:
        raise SystemExit("--end precisa ser maior que --start")
    defaults = OBJECTIVE_DEFAULTS[args.objective]
    max_frames = min(args.max_frames or defaults["max_frames"], 100)
    resolution = args.resolution or defaults["resolution"]
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = sanitize_source(args.source)
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else REPORT_ROOT / f"{ts}-{slugify(safe)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / "work"; work.mkdir(exist_ok=True)

    video, download_info, subtitle = download_if_needed(args.source, work, args.no_download)
    meta = ffprobe(video)
    eff_start = start or 0.0
    eff_end = end or meta.get("duration_seconds") or 0.0
    eff_duration = max(0.0, eff_end - eff_start)
    fps, target = choose_fps(eff_duration or meta.get("duration_seconds") or 1, max_frames, bool(start or end))
    frames = extract_frames(video, out_dir / "frames", fps=fps, resolution=resolution, max_frames=max_frames, start=start, end=end)
    audio_path = extract_audio(video, out_dir / "audio_16k.wav") if meta.get("has_audio") else None
    transcript_path = Path(args.transcript_file).expanduser().resolve() if args.transcript_file else subtitle
    transcript = parse_transcript(transcript_path)

    data = {
        "ok": True, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_sanitized": safe, "source_was_url": is_url(args.source), "objective": args.objective,
        "objective_label": defaults["label"], "video_path": str(video), "metadata": meta,
        "range": {"start": start, "end": end, "effective_duration": eff_duration},
        "frames": frames, "frame_policy": {"fps": fps, "target": target, "max_frames": max_frames, "resolution": resolution},
        "transcript_file": str(transcript_path) if transcript_path else None, "transcript_segments": len(transcript),
        "audio_16k_wav": audio_path, "download_info": download_info,
        "governance": {"external_llm_used": False, "whisper_api_used": False, "pii_note": "Não envie vídeos de pacientes/leads para serviços externos sem aprovação e governança."},
    }
    json_path, html_path = write_reports(out_dir, data, transcript, frames)
    print(json.dumps({"ok": True, "out_dir": str(out_dir), "json": str(json_path), "html": str(html_path), "frames": len(frames), "transcript_segments": len(transcript), "audio": audio_path}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
