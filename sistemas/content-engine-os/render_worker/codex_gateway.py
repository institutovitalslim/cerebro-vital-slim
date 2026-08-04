#!/usr/bin/env python3
"""Codex Gateway — ponte HTTP host->codex CLI (OAuth) para o Content Engine OS.
O container da API não tem o codex nem o OAuth; chama este gateway no host.
Roda `codex exec` (não-interativo, sandbox read-only) e devolve a resposta final.
Suporta TEXTO, VISÃO (imagens via -i/--image) e --output-schema (JSON estruturado).
Bind no IP do gateway docker (não público) + token compartilhado.
"""
import json
import os
import re
import base64
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("CODEX_GATEWAY_HOST", "172.19.0.1")
PORT = int(os.environ.get("CODEX_GATEWAY_PORT", "8030"))
TOKEN = os.environ.get("CODEX_GATEWAY_TOKEN", "")
DEFAULT_MODEL = os.environ.get("CODEX_MODEL", "gpt-5.5")

_EXT = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _decode_image(data_url: str, idx: int) -> str:
    """Aceita data-URL ('data:image/jpeg;base64,...') ou base64 cru; grava temp no host e devolve o caminho."""
    m = re.match(r"data:(image/[\w.+-]+);base64,(.*)$", data_url or "", re.S)
    if m:
        mime, b64 = m.group(1).lower(), m.group(2)
        ext = _EXT.get(mime, ".jpg")
    else:
        b64, ext = (data_url or ""), ".jpg"
    fd, path = tempfile.mkstemp(suffix=ext, prefix=f"codex_img{idx}_", dir="/tmp")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return path


def run_codex(prompt: str, system, model: str, timeout: int,
              images=None, output_schema=None) -> dict:
    full = prompt if not system else f"INSTRUÇÕES DO SISTEMA:\n{system}\n\n{prompt}"
    fd, out = tempfile.mkstemp(suffix=".txt", prefix="codex_", dir="/tmp")
    os.close(fd)
    tmp_imgs = []
    schema_file = None
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only",
           "-m", model, "-C", "/tmp", "-o", out]
    try:
        for i, im in enumerate(images or []):
            try:
                p = _decode_image(im, i)
                tmp_imgs.append(p)
                cmd += ["-i", p]
            except Exception as e:
                return {"ok": False, "error": f"imagem invalida[{i}]: {e}"}
        if output_schema:
            fd2, schema_file = tempfile.mkstemp(suffix=".json", prefix="codex_schema_", dir="/tmp")
            os.close(fd2)
            with open(schema_file, "w", encoding="utf-8") as f:
                json.dump(output_schema, f, ensure_ascii=False)
            cmd += ["--output-schema", schema_file]
        cmd.append(full)
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=timeout)
        content = ""
        try:
            with open(out, encoding="utf-8") as f:
                content = f.read().strip()
        except FileNotFoundError:
            pass
        if not content and p.returncode != 0:
            return {"ok": False, "error": (p.stderr or p.stdout or "")[-800:], "rc": p.returncode}
        return {"ok": True, "content": content, "model": model, "mode": "codex",
                "n_images": len(tmp_imgs)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout após {timeout}s", "rc": -1}
    finally:
        for f in [out, schema_file] + tmp_imgs:
            if f:
                try:
                    os.unlink(f)
                except OSError:
                    pass


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "model": DEFAULT_MODEL, "vision": True})
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path != "/generate":
            return self._send(404, {"ok": False, "error": "not found"})
        if TOKEN and self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self._send(401, {"ok": False, "error": "unauthorized"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            return self._send(400, {"ok": False, "error": f"bad json: {e}"})
        prompt = data.get("prompt", "")
        if not prompt:
            return self._send(400, {"ok": False, "error": "prompt obrigatório"})
        res = run_codex(prompt, data.get("system"), data.get("model") or DEFAULT_MODEL,
                        int(data.get("timeout", 180)),
                        images=data.get("images"), output_schema=data.get("output_schema"))
        self._send(200 if res.get("ok") else 502, res)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer((HOST, PORT), H)
    print(f"codex-gateway em http://{HOST}:{PORT} (modelo {DEFAULT_MODEL}, visao on)", flush=True)
    srv.serve_forever()
