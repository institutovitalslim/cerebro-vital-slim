# -*- coding: utf-8 -*-
"""gate_v14.py — roda o Virality Gate no reel_dra_v14 (brain_activity) + publica. distill via Codex."""
import virality_predictor as v
import json, shutil, os

VID = "/root/clone_dra/remotion-reel/out/reel_dra_v14.mp4"
OUTDIR = "/root/clone_dra/remotion-reel/out"
DST = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders/dra_test/reel_dra_v14.mp4"

ctx = {
    "hook": "v2 (cold-open S3 + card ancora-idade)",
    "recut_start_s": 11.36,
    "card": "Depois dos 40, o erro nao e seu",
    "dur_s": 34.84,
    "ab_test": "vencedor A/B de gancho: clipe 5s hook 0.469 vs controle 0.424 (+10.6%)",
    "changes": "abre em S3 'Mas no fundo voce ja percebeu...', corta 11s (drop S0-S2), 9 b-rolls deslocados -11.36s, gancho 100% Dra+card, ~35s",
}

r = v.predict_virality(VID, out_dir=OUTDIR, creative_id="reel_dra_v14", context=ctx)
json.dump(r, open(f"{OUTDIR}/_v14_gate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
brief = {k: r.get(k) for k in ("ok", "index_0_100", "verdict", "hook_score", "avg", "peak",
                               "peak_s", "retention_delta", "weak_seconds")}
print("GATE:", json.dumps(brief, ensure_ascii=False))

if r.get("ok"):
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copy(VID, DST)
    print("PUBLISHED:", DST, os.path.getsize(DST), "bytes")
else:
    print("GATE FALHOU — nao publiquei. erro:", r.get("error"))
