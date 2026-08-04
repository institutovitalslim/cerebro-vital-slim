# -*- coding: utf-8 -*-
"""
broll_pipeline.py — Pipeline de b-roll compliance-aware (content-engine-os / render_worker).

Fase IMAGEM (esta): para cada frase 'broll' do plano do diretor ->
  gera imagem (Higgsfield) com o prompt compliant -> VALIDA no gate (creative_compliance) ->
  regenera as reprovadas (reforcando proibicoes) -> grava imagens aprovadas + manifest.json.
Fase VIDEO (--video): anima cada imagem aprovada (Higgsfield kling, --image + motion_prompt).

Uso: python3 broll_pipeline.py <cid> <plan.json> [--video]
"""
from __future__ import annotations
import os, sys, json, re, shutil, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from creative_compliance import assess_visual_creative

ASSETS = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"
LIB = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/stories_broll"  # b-roll REAL da Dra
SOUL = "053e3faf-2743-42a3-ae5e-bd0913c3d250"  # Soul ID do rosto da Dra Daniely
REINFORCE = (" Strictly NO medication, NO pills, NO capsule, NO vial, NO syringe, NO weighing scale, "
             "NO measuring tape, NO before-after, NO exposed body/belly, NO nudity, "
             "absolutely NO text, NO words, NO letters, NO numbers.")


def _lib_video(text: str):
    """Clipe de VÍDEO real da biblioteca da Dra que melhor casa com o texto (>0 palavras em comum).
    None se não houver biblioteca/clipe/match — aí o pipeline gera por IA como antes. Nunca lança."""
    try:
        metaf = os.path.join(LIB, "library.json")
        if not os.path.exists(metaf):
            return None
        items = json.load(open(metaf, encoding="utf-8"))
        vids = [it for it in items if it.get("kind") == "video"
                and os.path.exists(os.path.join(LIB, it.get("file", "")))]
        if not vids:
            return None
        kws = set(re.findall(r"\w{4,}", (text or "").lower()))
        best, bs = None, 0
        for it in vids:
            hay = (it.get("tags", "") + " " + it.get("theme", "") + " " + it.get("note", "")).lower()
            s = sum(1 for k in kws if k in hay)
            if s > bs:
                bs, best = s, it
        return os.path.join(LIB, best["file"]) if best else None
    except Exception:
        return None


def _hf(args: list[str], timeout: int) -> str:
    return subprocess.run(["higgsfield", "generate", "create", *args],
                          capture_output=True, text=True, timeout=timeout).stdout


def _url(out: str) -> str | None:
    try:
        return next((x["result_url"] for x in json.loads(out) if x.get("result_url")), None)
    except Exception:
        return None


def gen_image(prompt: str, dest: str, use_soul: bool = False, use_gpt: bool = False) -> bool:
    if use_gpt:  # gpt_image_2 = texto LEGÍVEL na imagem (ex.: receituário)
        args = ["gpt_image_2", "--prompt", prompt, "--aspect_ratio", "9:16",
                "--quality", "high", "--resolution", "2k", "--wait", "--wait-timeout", "6m", "--json"]
    elif use_soul:
        args = ["text2image_soul_v2", "--prompt", prompt, "--custom_reference_id", SOUL,
                "--aspect_ratio", "9:16", "--wait", "--wait-timeout", "5m", "--json"]
    else:
        args = ["nano_banana_2", "--prompt", prompt, "--aspect_ratio", "9:16", "--wait", "--wait-timeout", "5m", "--json"]
    out = _hf(args, 400)
    u = _url(out)
    if not u:
        return False
    try:
        urllib.request.urlretrieve(u, dest)
        return os.path.getsize(dest) > 5000
    except Exception:
        return False


def gen_video(image: str, motion: str, dest: str) -> bool:
    # seedance_2_0 = vídeo b-roll principal (image-to-video via --start-image, 1080p)
    out = _hf(["seedance_2_0", "--start-image", image, "--prompt", motion or "subtle cinematic camera motion, no text",
               "--aspect_ratio", "9:16", "--duration", "5", "--resolution", "1080p", "--generate-audio", "false",
               "--wait", "--wait-timeout", "20m", "--json"], 1300)
    u = _url(out)
    if not u:  # fallback kling se seedance falhar
        out = _hf(["kling2_6", "--image", image, "--prompt", motion or "subtle cinematic camera motion, no text",
                   "--aspect_ratio", "9:16", "--wait", "--wait-timeout", "18m", "--json"], 1200)
        u = _url(out)
    if not u:
        return False
    try:
        urllib.request.urlretrieve(u, dest)
        return os.path.getsize(dest) > 20000
    except Exception:
        return False


def do_image_phase(p: dict, outdir: str, full_text: str, max_attempts: int = 6) -> dict:
    """Gera+valida; se reprovar, RE-DIRECIONA (novo conceito diferente) ate aprovar.
    NUNCA cai pra Dra por reprovacao — sempre gera outro b-roll compliant."""
    from broll_director import direct_one
    use_soul = bool(p.get("use_soul"))
    use_gpt = bool(p.get("use_gpt"))    # gpt_image_2 p/ texto legivel
    allow_text = bool(p.get("allow_text"))  # cena com texto PT aprovado (ex.: "Programa de Acompanhamento")
    locked = bool(p.get("locked")) or use_gpt  # conceito aprovado: nao troca, so ajusta
    concept = p["concept"]
    prompt = p["image_prompt"]
    motion = p.get("motion_prompt", "")
    tried = [concept]
    last = {}
    for attempt in range(max_attempts):
        tmp = f"{outdir}/_b{p['idx']:02d}_t{attempt}.png"
        pr = prompt + (REINFORCE if (attempt and not allow_text) else "")
        if gen_image(pr, tmp, use_soul=use_soul, use_gpt=use_gpt):
            v = assess_visual_creative(tmp, concept, allow_text=allow_text)
            last = v
            if v.get("approved"):
                final = f"{outdir}/broll_{p['idx']:02d}.png"
                os.replace(tmp, final)
                return {"idx": p["idx"], "image": final, "verdict": v, "attempts": attempt + 1,
                        "status": "approved", "concept": concept, "image_prompt": pr, "motion_prompt": motion}
            try:
                os.remove(tmp)
            except Exception:
                pass
        else:
            last = {"error": "gen_fail"}
        if use_soul:
            # cena com o rosto da Dra: NAO troca o conceito; ajusta o prompt p/ corrigir o que reprovou (ex.: fundo)
            prompt = (p["image_prompt"] + " plain neutral elegant studio background, soft light, NOT a clinic, "
                      "no medical office, no clinic furniture, no text.")
            tried.append("soul_retry")
            continue
        if locked:
            # conceito APROVADO pelo usuario: mantem a cena, so reforca correcao (sem trocar de conceito)
            prompt = (p["image_prompt"] + REINFORCE +
                      " Keep EXACTLY this same scene/concept; only fix the compliance issue; any screen/label "
                      "text must be blurred and ILLEGIBLE.")
            tried.append("locked_retry")
            continue
        # b-roll comum: pede conceito NOVO e diferente ao diretor (nunca cai pra Dra)
        try:
            nd = direct_one(p["text"], full_text, tried, reason=json.dumps(last, ensure_ascii=False)[:300])
        except Exception as e:
            nd = {}
            last = {**last, "redirect_error": str(e)[:120]}
        if nd.get("image_prompt"):
            concept = nd.get("concept", concept)
            prompt = nd["image_prompt"]
            motion = nd.get("motion_prompt", motion)
            tried.append(concept)
    return {"idx": p["idx"], "image": None, "verdict": last, "attempts": max_attempts,
            "status": "failed", "tried": tried}


def main():
    cid, planf = sys.argv[1], sys.argv[2]
    video = "--video" in sys.argv
    plan = json.load(open(planf, encoding="utf-8"))
    outdir = f"{ASSETS}/{cid}/broll"
    os.makedirs(outdir, exist_ok=True)
    broll = [p for p in plan if p.get("who") == "broll"]

    full_text = " ".join(p.get("text", "") for p in plan)
    if not video:
        results = {}
        todo = []
        for p in broll:
            # 1º: usa clipe REAL da biblioteca da Dra se houver match (footage real > IA; sem custo/gate)
            libclip = _lib_video(p.get("text", ""))
            if libclip:
                try:
                    shutil.copy(libclip, f"{outdir}/broll_{p['idx']:02d}.mp4")
                    results[p["idx"]] = {"idx": p["idx"], "image": None, "status": "approved", "attempts": 0,
                                         "from_library": os.path.basename(libclip), "verdict": {"library": True},
                                         "concept": p.get("concept"), "motion_prompt": p.get("motion_prompt")}
                    print(f"[{p['idx']:02d}] BIBLIOTECA: {os.path.basename(libclip)} (clipe real da Dra)", flush=True)
                    continue
                except Exception as e:
                    print(f"[{p['idx']:02d}] falha ao usar biblioteca ({e}); gera por IA", flush=True)
            img = f"{outdir}/broll_{p['idx']:02d}.png"
            if os.path.exists(img) and os.path.getsize(img) > 5000:
                results[p["idx"]] = {"idx": p["idx"], "image": img, "status": "approved", "attempts": 0,
                                     "verdict": {"skipped": True}, "concept": p.get("concept"),
                                     "motion_prompt": p.get("motion_prompt")}
                print(f"[{p['idx']:02d}] skip (ja existe)", flush=True)
            else:
                todo.append(p)
        with ThreadPoolExecutor(max_workers=5) as ex:
            futs = {ex.submit(do_image_phase, p, outdir, full_text): p for p in todo}
            for f in as_completed(futs):
                r = f.result()
                results[r["idx"]] = r
                v = r.get("verdict", {})
                print(f"[{r['idx']:02d}] {r['status']} att={r['attempts']} score={v.get('score')} "
                      f":: {r.get('concept','')[:55]}", flush=True)
        manifest = []
        for p in plan:
            r = results.get(p["idx"])
            extra = {}
            if r and r.get("status") == "approved":
                extra = {"concept": r.get("concept", p.get("concept")),
                         "motion_prompt": r.get("motion_prompt", p.get("motion_prompt"))}
            manifest.append({**p, **extra, "image": (r or {}).get("image"),
                             "status": (r or {}).get("status", "dra"), "verdict": (r or {}).get("verdict")})
        json.dump(manifest, open(f"{outdir}/manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        ok = sum(1 for r in results.values() if r["status"] == "approved")
        print(f"DONE imagens: {ok}/{len(broll)} aprovadas -> {outdir}/manifest.json", flush=True)
    else:
        manifest = json.load(open(f"{outdir}/manifest.json", encoding="utf-8"))
        appr = [m for m in manifest if m.get("status") == "approved" and m.get("image")]
        def anim(m):
            dest = f"{outdir}/broll_{m['idx']:02d}.mp4"
            if os.path.exists(dest) and os.path.getsize(dest) > 20000:
                return (m["idx"], dest)  # incremental: ja animado
            ok = gen_video(m["image"], m.get("motion_prompt", ""), dest)
            return (m["idx"], dest if ok else None)
        with ThreadPoolExecutor(max_workers=4) as ex:
            for idx, dest in ex.map(anim, appr):
                print(f"[{idx:02d}] video {'OK' if dest else 'FAIL'} {dest or ''}", flush=True)
        for m in manifest:
            mp4 = f"{outdir}/broll_{m['idx']:02d}.mp4"
            if os.path.exists(mp4):
                m["video"] = mp4
        json.dump(manifest, open(f"{outdir}/manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("DONE video phase", flush=True)


if __name__ == "__main__":
    main()
