#!/usr/bin/env python3
"""Eduardo — baixa de estoque por PRESCRIÇÃO MÉDICA (visão).

Lê a IMAGEM da prescrição de um atendimento (com medicações aplicadas e, se houver,
os RÓTULOS de ampola colados), extrai medicação/dose/quantidade/lote via Gemini visão,
casa com o controle de estoque (clínica/área 2) e PROPÕE a baixa rastreável.
NÃO aplica sozinho — saída é uma PROPOSTA para o Eduardo confirmar/lançar (Omie = com aprovação).

Uso: eduardo_estoque_baixa.py <imagem_prescricao.jpg> [--json]
"""
import sys, os, json, base64, urllib.request, mimetypes, re, difflib

CONTROLE = "/root/.openclaw/workspace/memory/tactical/estoque_completo_area_2_atualizado_2026-06-12.json"
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]

def resolve_key():
    for envp in ("/root/.openclaw/.env.runtime", "/root/.openclaw/.env",
                 "/root/.openclaw/secure/google.env", "/root/.openclaw/secure/gemini.env"):
        try:
            for ln in open(envp):
                ln = ln.strip()
                for k in ("GOOGLE_API_KEY=", "GEMINI_API_KEY="):
                    if ln.startswith(k):
                        return ln.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

def gemini_vision(image_path, prompt):
    key = resolve_key()
    if not key:
        raise RuntimeError("sem GOOGLE_API_KEY (conta institutovitalslim)")
    data = base64.b64encode(open(image_path, "rb").read()).decode()
    mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    body = json.dumps({"contents": [{"parts": [
        {"inline_data": {"mime_type": mime, "data": data}},
        {"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}).encode()
    last = ""
    for m in GEMINI_MODELS:
        try:
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}",
                data=body, headers={"Content-Type": "application/json"}, method="POST")
            d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
            if "candidates" in d:
                return d["candidates"][0]["content"]["parts"][0]["text"]
            last = d.get("error", {}).get("message", "")[:140]
        except Exception as e:
            last = str(e)[:140]
    raise RuntimeError("Gemini visão falhou: " + last)

PROMPT = (
    "Esta é a imagem de uma PRESCRIÇÃO MÉDICA de um atendimento de clínica, que pode conter "
    "RÓTULOS de ampola/frasco colados. Extraia SOMENTE as medicações/insumos que foram APLICADOS/USADOS "
    "no atendimento. Responda em JSON: {\"paciente\": <nome se visível ou null>, \"data\": <se visível>, "
    "\"itens\": [{\"item\": \"<nome>\", \"concentracao\": \"<ex 100mg/ml ou null>\", "
    "\"quantidade\": <número de ampolas/unidades, inteiro>, \"lote\": \"<do rótulo, ou null>\"}]}. "
    "Se algo estiver ilegível, marque o campo como null. Não invente."
)

def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def load_control():
    try:
        d = json.load(open(CONTROLE, encoding="utf-8"))
        return d.get("rows", [])
    except Exception:
        return []

def match_item(name, rows):
    n = norm(name)
    best, score = None, 0.0
    for r in rows:
        item = r.get("item", "")
        cand = norm(item)
        if not cand:
            continue
        s = difflib.SequenceMatcher(None, n, cand).ratio()
        if n and (n in cand or cand in n):
            s = max(s, 0.9)
        if s > score:
            best, score = r, s
    return (best, round(score, 2)) if score >= 0.6 else (None, round(score, 2))

def to_int(v):
    try:
        return int(float(str(v).strip() or 0))
    except Exception:
        return 0

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(1)
    img = args[0]
    raw = gemini_vision(img, PROMPT)
    raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", raw.strip())
    ext = json.loads(raw)
    rows = load_control()
    proposta = []
    for it in ext.get("itens", []):
        m, conf = match_item(it.get("item", ""), rows)
        saldo_clin = to_int(m.get("estoque_clinica")) if m else None
        qtd = to_int(it.get("quantidade"))
        proposta.append({
            "item_prescricao": it.get("item"), "concentracao": it.get("concentracao"),
            "quantidade_baixa": qtd, "lote": it.get("lote"),
            "item_controle": m.get("item") if m else None, "match_confianca": conf,
            "saldo_clinica_atual": saldo_clin,
            "saldo_clinica_apos": (saldo_clin - qtd) if (saldo_clin is not None) else None,
            "status": "OK" if m else "SEM_MATCH_revisar_manual",
        })
    out = {"paciente": ext.get("paciente"), "data": ext.get("data"), "proposta_baixa": proposta,
           "aviso": "PROPOSTA — confirmar antes de lançar no Omie (altera saldo oficial)."}
    if "--json" in sys.argv:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return
    print(f"📦 Baixa por prescrição — paciente: {out['paciente']} | data: {out['data']}")
    print(f"{'ITEM (prescrição)':32} {'qtd':>4} {'lote':12} {'→ controle':28} {'saldo':>6}→{'novo':>5} {'status'}")
    for p in proposta:
        print(f"{(p['item_prescricao'] or '?')[:32]:32} {p['quantidade_baixa']:>4} {str(p['lote'] or '-')[:12]:12} "
              f"{str(p['item_controle'] or '—')[:28]:28} {str(p['saldo_clinica_atual']):>6}→{str(p['saldo_clinica_apos']):>5} {p['status']}")
    print("\n⚠️  " + out["aviso"])

if __name__ == "__main__":
    main()
