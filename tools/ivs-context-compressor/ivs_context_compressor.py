#!/usr/bin/env python3
"""
IVS Context Compressor — camada local de compressão segura de contexto.

Inspirado funcionalmente pelo reverse do Headroom, mas implementado do zero para o IVS:
- preserva original com SHA256;
- redige PII/secrets por padrão;
- extrai eventos/IDs/erros críticos;
- gera resumo compacto em Markdown ou JSON;
- permite recuperar o original por hash.

Não substitui fonte canônica. Use como pré-processador de leitura operacional.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_EVIDENCE_DIR = Path("/root/cerebro-vital-slim/ops/context-compressor/evidence")
DEFAULT_OUT_DIR = Path("/root/cerebro-vital-slim/ops/context-compressor/reports")

CRITICAL_RE = re.compile(
    r"(" 
    r"ERROR|ERR|FATAL|CRITICAL|Exception|Traceback|timeout|failed|failure|denied|unauthorized|forbidden|"
    r"NO_REPLY|quarkclinic_check_failed|zapi-fail|zapi-preflight|zapi-commit|patient_bridge|takeover|cooldown|"
    r"status[_ -]?code|HTTP/[0-9.]+|\b[45][0-9]{2}\b|messageId|trace[_-]?id|request[_-]?id|phone|telefone|jid|lead|paciente|"
    r"sent|delivered|received|webhook|POST|GET|PUT|DELETE|cron|assistant turn failed|token|secret|api[_-]?key"
    r")",
    re.IGNORECASE,
)

ID_PATTERNS = {
    "message_ids": re.compile(r"\b(?:messageId|message_id|msg_id|idMensagem)\s*[:=]\s*['\"]?([A-Za-z0-9._:-]{6,})", re.I),
    "trace_ids": re.compile(r"\b(?:trace[_-]?id|request[_-]?id|run[_-]?id)\s*[:=]\s*['\"]?([A-Za-z0-9._:-]{6,})", re.I),
    "status_codes": re.compile(r"\b(?:status[_ -]?code|status|HTTP/[0-9.]+)\s*[:= ]\s*([1-5][0-9]{2})\b", re.I),
    "timestamps": re.compile(r"\b(20\d{2}-\d{2}-\d{2}[T ][0-2]\d:[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z|[-+]\d{2}:?\d{2})?|\d{2}/\d{2}/20\d{2}\s+[0-2]\d:[0-5]\d(?::[0-5]\d)?)\b"),
}

REDACTIONS: List[Tuple[str, re.Pattern[str], str]] = [
    ("mcp_token", re.compile(r"([?&]mcp_token=)[^\s&#]+", re.I), r"\1[REDACTED_MCP_TOKEN]"),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.I), "Bearer [REDACTED_TOKEN]"),
    ("api_key", re.compile(r"\b(api[_-]?key|token|secret|password|senha)\s*[:=]\s*['\"]?[^\s,'\"]{8,}", re.I), r"\1=[REDACTED_SECRET]"),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    # Telefone primeiro, porque telefone BR com DDD também pode ter 11 dígitos como CPF.
    # Só redige telefone quando há rótulo operacional explícito ou formato humano (+55/(DD)).
    # Isso evita redigir unix timestamps, messageId, trace_id ou request_id numéricos.
    ("phone_br", re.compile(r"\b(phone|telefone|whatsapp|celular|jid)\s*[:=]\s*(?:\+?55\s*)?\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}\b", re.I), r"\1=[REDACTED_PHONE]"),
    ("phone_br_standalone", re.compile(r"(?<![A-Za-z0-9])(?:\+55\s*\d{2}\s*9?\d{4}[-\s]?\d{4}|\(\d{2}\)\s*9?\d{4}[-\s]?\d{4})(?![A-Za-z0-9])"), "[REDACTED_PHONE]"),
    ("cpf", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[REDACTED_CPF]"),
    ("zapi_instance", re.compile(r"\b(instanc(?:e|ia)[_-]?(?:id|token)?|zapi[_-]?(?:token|secret))\s*[:=]\s*['\"]?[^\s,'\"]{8,}", re.I), r"\1=[REDACTED_ZAPI]"),
]

TYPE_HINTS = {
    "clara-log": ["NO_REPLY", "zapi", "quarkclinic", "patient_bridge", "takeover", "messageId", "webhook"],
    "zapi-webhook": ["messageId", "phone", "fromMe", "chatName", "webhook", "status"],
    "cron-log": ["cron", "assistant turn failed", "Traceback", "exit_code", "timeout"],
    "gbrain-results": ["gbrain", "path", "score", "query", "cerebro"],
    "generic": [],
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def redact(text: str) -> Tuple[str, Dict[str, int]]:
    counts: Dict[str, int] = {}
    out = text
    for name, pattern, repl in REDACTIONS:
        out, n = pattern.subn(repl, out)
        if n:
            counts[name] = n
    return out, counts


def line_score(line: str, kind: str) -> int:
    score = 0
    if CRITICAL_RE.search(line):
        score += 5
    for hint in TYPE_HINTS.get(kind, []):
        if hint.lower() in line.lower():
            score += 2
    if len(line) > 400:
        score -= 1
    return score


def extract_critical_lines(lines: List[str], kind: str, max_lines: int) -> List[Dict[str, Any]]:
    scored = []
    for idx, line in enumerate(lines, start=1):
        score = line_score(line, kind)
        if score > 0:
            scored.append((score, idx, line.rstrip()))
    # Mantém ordem cronológica, mas limita por maior relevância quando necessário.
    if len(scored) > max_lines:
        selected_idx = {idx for _, idx, _ in sorted(scored, key=lambda x: (-x[0], x[1]))[:max_lines]}
        scored = [item for item in scored if item[1] in selected_idx]
    return [{"line": idx, "score": score, "text": line} for score, idx, line in scored]


def collect_ids(text: str) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for name, pattern in ID_PATTERNS.items():
        vals = []
        for m in pattern.finditer(text):
            value = m.group(1) if m.groups() else m.group(0)
            if value not in vals:
                vals.append(value)
            if len(vals) >= 30:
                break
        result[name] = vals
    return result


def estimate_tokens(text_or_chars: str | int) -> int:
    # Estimativa conservadora para triagem operacional. Não depende de tokenizer externo.
    chars = text_or_chars if isinstance(text_or_chars, int) else len(text_or_chars)
    return max(1, round(chars / 4)) if chars else 0


def reduction_metrics(text: str, redacted_text: str, critical: List[Dict[str, Any]], ids: Dict[str, List[str]], warnings: List[str]) -> Dict[str, Any]:
    compressed_chars = sum(len(item.get("text", "")) for item in critical)
    compressed_chars += len(json.dumps(ids, ensure_ascii=False))
    compressed_chars += sum(len(w) for w in warnings)
    original_chars = len(text)
    redacted_chars = len(redacted_text)
    reduction_pct = round((1 - (compressed_chars / original_chars)) * 100, 2) if original_chars else 0.0
    redaction_delta_pct = round(((redacted_chars - original_chars) / original_chars) * 100, 2) if original_chars else 0.0
    return {
        "compressed_context_char_count": compressed_chars,
        "estimated_tokens_original": estimate_tokens(original_chars),
        "estimated_tokens_redacted": estimate_tokens(redacted_chars),
        "estimated_tokens_compressed_context": estimate_tokens(compressed_chars),
        "estimated_token_reduction_pct": reduction_pct,
        "compression_effect": "reduced" if reduction_pct > 0 else ("expanded" if reduction_pct < 0 else "neutral"),
        "redaction_char_delta_pct": redaction_delta_pct,
    }


def summarize(text: str, redacted_text: str, kind: str, max_lines: int) -> Dict[str, Any]:
    lines = redacted_text.splitlines()
    critical = extract_critical_lines(lines, kind, max_lines=max_lines)
    ids = collect_ids(redacted_text)
    errors = [e for e in critical if re.search(r"ERROR|FATAL|CRITICAL|Exception|Traceback|failed|failure|timeout|\b[45][0-9]{2}\b", e["text"], re.I)]
    sends = [e for e in critical if re.search(r"sent|delivered|zapi-commit|messageId|POST|status", e["text"], re.I)]
    warnings = []
    if not critical:
        warnings.append("Nenhuma linha crítica detectada; revisar original se a decisão depender de detalhes finos.")
    if kind in {"clara-log", "zapi-webhook"}:
        warnings.append("Conteúdo potencialmente sensível: usar apenas versão redigida em relatórios e manter original restrito.")
    if any(ids.get(k) for k in ["message_ids", "trace_ids", "status_codes"]):
        warnings.append("IDs/status preservados para auditoria e recuperação.")
    metrics = reduction_metrics(text, redacted_text, critical, ids, warnings)
    return {
        "kind": kind,
        "line_count": len(lines),
        "char_count_original": len(text),
        "char_count_redacted": len(redacted_text),
        "critical_line_count": len(critical),
        "error_like_count": len(errors),
        "send_status_like_count": len(sends),
        "reduction": metrics,
        "ids": ids,
        "critical_lines": critical,
        "warnings": warnings,
    }


def write_evidence(input_path: Path, raw: bytes, evidence_dir: Path, digest: str) -> Dict[str, str]:
    ensure_dir(evidence_dir)
    suffix = input_path.suffix or ".txt"
    original_path = evidence_dir / f"{digest}{suffix}"
    meta_path = evidence_dir / f"{digest}.meta.json"
    if not original_path.exists():
        original_path.write_bytes(raw)
    meta = {
        "sha256": digest,
        "source_path": str(input_path),
        "stored_original": str(original_path),
        "created_at": utc_now(),
        "size_bytes": len(raw),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"original_path": str(original_path), "meta_path": str(meta_path)}


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        f"# IVS Context Compressor — {payload['input_name']}",
        "",
        f"- Gerado em: `{payload['created_at']}`",
        f"- Tipo: `{s['kind']}`",
        f"- SHA256 original: `{payload['sha256']}`",
        f"- Original preservado: `{payload['evidence']['original_path']}`",
        f"- Linhas: `{s['line_count']}`",
        f"- Caracteres original/redigido: `{s['char_count_original']}` / `{s['char_count_redacted']}`",
        f"- Contexto comprimido estimado: `{s['reduction']['compressed_context_char_count']}` chars / `{s['reduction']['estimated_tokens_compressed_context']}` tokens",
        f"- Redução estimada de tokens: `{s['reduction']['estimated_token_reduction_pct']}%` (`{s['reduction']['compression_effect']}`)",
        f"- Linhas críticas extraídas: `{s['critical_line_count']}`",
        f"- Eventos de erro/falha: `{s['error_like_count']}`",
        "",
        "## IDs/evidências preservadas",
    ]
    for key, vals in s["ids"].items():
        shown = ", ".join(f"`{v}`" for v in vals[:20]) or "—"
        lines.append(f"- **{key}**: {shown}")
    lines += ["", "## Alertas", ""]
    for warning in s["warnings"]:
        lines.append(f"- {warning}")
    lines += ["", "## Linhas críticas redigidas", ""]
    if s["critical_lines"]:
        for item in s["critical_lines"]:
            text = item["text"].replace("`", "ˋ")
            lines.append(f"- L{item['line']} · score {item['score']}: `{text}`")
    else:
        lines.append("Nenhuma linha crítica detectada.")
    lines += [
        "",
        "## Recuperação do original",
        "",
        "```bash",
        f"python3 /root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py --recover {payload['sha256']}",
        "```",
        "",
        "Governança: este resumo não substitui a fonte original/canônica.",
    ]
    return "\n".join(lines) + "\n"


def compress_raw(raw: bytes, source_name: str, source_path: str, args: argparse.Namespace) -> Dict[str, Any]:
    digest = sha256_bytes(raw)
    text = raw.decode(args.encoding, errors="replace")
    redacted_text, redaction_counts = redact(text)
    evidence = write_evidence(Path(source_name), raw, Path(args.evidence_dir), digest)
    summary = summarize(text, redacted_text, args.type, args.max_lines)
    summary["redactions"] = redaction_counts
    return {
        "ok": True,
        "created_at": utc_now(),
        "input_name": source_name,
        "input_path": source_path,
        "sha256": digest,
        "evidence": evidence,
        "summary": summary,
    }


def write_outputs(payload: Dict[str, Any], args: argparse.Namespace) -> Dict[str, str]:
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(payload["input_name"]).stem or "stdin")[:80]
    stem = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe_stem}-{payload['sha256'][:10]}"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    md_text = render_markdown(payload)
    payload["summary"]["reduction"]["markdown_report_char_count"] = len(md_text)
    payload["summary"]["reduction"]["estimated_tokens_markdown_report"] = estimate_tokens(md_text)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def emit_payload(payload: Dict[str, Any], args: argparse.Namespace) -> int:
    payload["outputs"] = write_outputs(payload, args)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(payload))
    return 0


def compress_file(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(json.dumps({"ok": False, "error": f"input not found: {input_path}"}, ensure_ascii=False), file=sys.stderr)
        return 2
    payload = compress_raw(input_path.read_bytes(), input_path.name, str(input_path), args)
    return emit_payload(payload, args)


def compress_stdin(args: argparse.Namespace) -> int:
    raw = sys.stdin.buffer.read()
    if not raw:
        print(json.dumps({"ok": False, "error": "stdin is empty"}, ensure_ascii=False), file=sys.stderr)
        return 2
    source_name = args.stdin_name or f"stdin-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    payload = compress_raw(raw, source_name, "stdin", args)
    return emit_payload(payload, args)


def recover(args: argparse.Namespace) -> int:
    digest = args.recover.strip()
    if not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
        print(json.dumps({"ok": False, "error": "recover expects full sha256"}, ensure_ascii=False), file=sys.stderr)
        return 2
    evidence_dir = Path(args.evidence_dir)
    matches = list(evidence_dir.glob(f"{digest}.*"))
    originals = [p for p in matches if not p.name.endswith(".meta.json")]
    if not originals:
        print(json.dumps({"ok": False, "error": f"original not found for sha256 {digest}", "evidence_dir": str(evidence_dir)}, ensure_ascii=False), file=sys.stderr)
        return 3
    original = originals[0]
    if args.copy_to:
        target = Path(args.copy_to).expanduser().resolve()
        ensure_dir(target.parent)
        shutil.copy2(original, target)
        print(json.dumps({"ok": True, "sha256": digest, "original": str(original), "copied_to": str(target)}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"ok": True, "sha256": digest, "original": str(original)}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="IVS Context Compressor")
    p.add_argument("--input", help="Arquivo de entrada a comprimir")
    p.add_argument("--stdin", action="store_true", help="Lê conteúdo bruto do stdin e preserva como evidência")
    p.add_argument("--stdin-name", default="stdin.txt", help="Nome sintético para relatórios/evidência quando usar --stdin")
    p.add_argument("--type", default="generic", choices=sorted(TYPE_HINTS.keys()), help="Tipo operacional do conteúdo")
    p.add_argument("--format", default="json", choices=["json", "md"], help="Formato impresso no stdout")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Diretório dos relatórios")
    p.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR), help="Diretório restrito para originais")
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--max-lines", type=int, default=80, help="Máximo de linhas críticas no resumo")
    p.add_argument("--recover", help="SHA256 completo para localizar original preservado")
    p.add_argument("--copy-to", help="Copia original recuperado para este caminho")
    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.recover:
        return recover(args)
    if args.stdin:
        return compress_stdin(args)
    if not args.input:
        parser.error("--input is required unless --recover or --stdin is used")
    return compress_file(args)


if __name__ == "__main__":
    raise SystemExit(main())
