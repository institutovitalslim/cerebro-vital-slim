# -*- coding: utf-8 -*-
"""
codex_llm.py — cliente UNICO de LLM do Content Engine OS (texto E visao).

REGRA DO TIARO (durável): NUNCA OpenRouter. SEMPRE Codex GPT-5.5 via gateway OAuth.
Fala com o codex-gateway no host (codex_gateway.py -> `codex exec`, OAuth):
    POST http://<host>:<port>/generate  {system, prompt, model, timeout, images?, output_schema?} -> {ok, content}

Config (env primeiro, depois /etc/content-engine/codex-gateway.env):
    CODEX_GATEWAY_HOST (def 172.19.0.1), CODEX_GATEWAY_PORT (def 8030),
    CODEX_GATEWAY_TOKEN, CODEX_MODEL (def gpt-5.5)
"""
from __future__ import annotations
import os, json, base64, mimetypes, urllib.request

_ENV_FILE = "/etc/content-engine/codex-gateway.env"


def _cfg():
    host = os.environ.get("CODEX_GATEWAY_HOST")
    port = os.environ.get("CODEX_GATEWAY_PORT")
    token = os.environ.get("CODEX_GATEWAY_TOKEN")
    model = os.environ.get("CODEX_MODEL")
    if not (host and port and token and model) and os.path.exists(_ENV_FILE):
        try:
            for line in open(_ENV_FILE, encoding="utf-8"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if k == "CODEX_GATEWAY_HOST" and not host:
                    host = v
                elif k == "CODEX_GATEWAY_PORT" and not port:
                    port = v
                elif k == "CODEX_GATEWAY_TOKEN" and not token:
                    token = v
                elif k == "CODEX_MODEL" and not model:
                    model = v
        except Exception:
            pass
    return host or "172.19.0.1", port or "8030", token or "", model or "gpt-5.5"


def _to_data_url(im: str) -> str:
    """Caminho local -> data-URL base64; data-URL passa direto."""
    if isinstance(im, str) and im.startswith("data:"):
        return im
    mime = mimetypes.guess_type(im)[0] or "image/jpeg"
    b64 = base64.b64encode(open(im, "rb").read()).decode()
    return f"data:{mime};base64,{b64}"


def _post(payload: dict, timeout: int, retries: int) -> str:
    host, port, token, _ = _cfg()
    url = f"http://{host}:{port}/generate"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last = ""
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode("utf-8"))
            if d.get("ok") and d.get("content"):
                return d["content"]
            last = d.get("error", "sem content")
        except Exception as e:
            last = str(e)
    raise RuntimeError(f"codex_gateway_failed: {str(last)[:240]}")


def chat(system: str, user: str, model: str | None = None, timeout: int = 240, retries: int = 3) -> str:
    """Texto via Codex GPT-5.5 (OAuth). Levanta RuntimeError se falhar."""
    host, port, token, dmodel = _cfg()
    payload = {"prompt": user, "system": system or "", "model": model or dmodel,
               "timeout": max(30, timeout - 20)}
    return _post(payload, timeout, retries)


def vision_chat(system: str, user: str, images, output_schema: dict | None = None,
                model: str | None = None, timeout: int = 200, retries: int = 2) -> str:
    """Visao via Codex GPT-5.5 (OAuth). images = lista de caminhos locais ou data-URLs.
    output_schema (JSON Schema) opcional -> --output-schema no codex. Levanta RuntimeError se falhar."""
    host, port, token, dmodel = _cfg()
    norm = [_to_data_url(im) for im in (images or [])]
    payload = {"prompt": user, "system": system or "", "model": model or dmodel,
               "timeout": max(40, timeout - 20), "images": norm}
    if output_schema:
        payload["output_schema"] = output_schema
    return _post(payload, timeout, retries)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "vision":
        print(vision_chat("Descreva a imagem em 1 frase, em portugues.", "O que aparece?", [sys.argv[2]]))
    else:
        print(chat("Responda apenas OK e o nome do modelo.", "ping"))
