# -*- coding: utf-8 -*-
"""
regen_metodo.py — regenera SO o b-roll do "metodo" (broll_18) com o prompt endurecido
(laboratorio de pesquisa inequivoco), validando no gate de compliance via Codex GPT-5.5,
faz swap em public/broll/broll_18.mp4, re-renderiza o Reel e republica.
"""
import os, sys, json, shutil, subprocess
from broll_pipeline import do_image_phase, gen_video

PROJ = "/root/clone_dra/remotion-reel"
PUBLIC_BROLL = f"{PROJ}/public/broll"
DATA = f"{PROJ}/src/data.json"
WORK = "/tmp/regen_metodo"
DST_PUBLISH = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders/dra_test/reel_dra_v14.mp4"
os.makedirs(WORK, exist_ok=True)

# frase do metodo com o PROMPT ENDURECIDO (cena inequivoca de pesquisa, compliant)
p = {
    "idx": 18,
    "text": "nosso método é estudado e aprovado.",
    "concept": ("Laboratório de pesquisa científica com pesquisadores de jaleco branco analisando dados em "
                "microscópios, telas gráficas abstratas sem texto legível e moléculas 3D."),
    "image_prompt": ("Scientific research laboratory with researchers wearing white lab coats, microscopes, "
                     "laptops showing abstract unlabeled curves and molecular visuals, glass lab equipment without "
                     "medicine containers, scientists analyzing results seriously, no clinic, no consultation room, "
                     "no syringe, no pills, no readable labels, no text, no words, no letters, photorealistic, "
                     "cinematic, vertical 9:16"),
    "motion_prompt": ("slow cinematic push-in on scientists analyzing data, subtle screen glow, shallow depth of "
                      "field, no text"),
}

full_text = " ".join(w["text"] for w in json.load(open(DATA, encoding="utf-8"))["words"])

print("CONCEPT:", p["concept"], flush=True)
# FASE IMAGEM: gera + valida no Codex; se reprovar, redireciona (nunca cai pra Dra)
r = do_image_phase(p, WORK, full_text, max_attempts=5)
v = r.get("verdict", {})
print(f"IMAGE PHASE: {r['status']} att={r['attempts']} score={v.get('score')} "
      f"matches={v.get('matches_concept')} reason={str(v.get('reason'))[:160]}", flush=True)
if r["status"] != "approved":
    print("FALHOU no compliance — NAO faco swap. verdict:", json.dumps(v, ensure_ascii=False)[:400], flush=True)
    sys.exit(1)
print("conceito final aprovado:", r.get("concept", "")[:120], flush=True)

# FASE VIDEO
tmp_mp4 = f"{WORK}/broll_18_new.mp4"
if not gen_video(r["image"], p["motion_prompt"], tmp_mp4):
    print("VIDEO FAIL — abortando", flush=True)
    sys.exit(1)
print("VIDEO OK:", os.path.getsize(tmp_mp4), "bytes", flush=True)

# SWAP (backup do antigo 1x)
dst = f"{PUBLIC_BROLL}/broll_18.mp4"
bak = f"{PUBLIC_BROLL}/broll_18_corp.bak.mp4"
if not os.path.exists(bak):
    shutil.copy(dst, bak)
    print("backup do antigo ->", bak, flush=True)
shutil.copy(tmp_mp4, dst)
print("SWAP ->", dst, os.path.getsize(dst), flush=True)

# RE-RENDER + PUBLISH + frame de validacao
subprocess.run(f'cd {PROJ} && npx remotion render Reel out/reel_dra_v14.mp4 --log=error',
               shell=True, check=True)
shutil.copy(f"{PROJ}/out/reel_dra_v14.mp4", DST_PUBLISH)
subprocess.run(f'ffmpeg -y -loglevel error -ss 21.5 -i {PROJ}/out/reel_dra_v14.mp4 -frames:v 1 '
               f'{PROJ}/out/v14_metodo_new.png', shell=True)
dur = subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {PROJ}/out/reel_dra_v14.mp4',
                     shell=True, capture_output=True, text=True).stdout.strip()
print(f"REEL RE-RENDERED + PUBLISHED (dur={dur}s) + frame -> out/v14_metodo_new.png", flush=True)
print("ALL DONE", flush=True)
