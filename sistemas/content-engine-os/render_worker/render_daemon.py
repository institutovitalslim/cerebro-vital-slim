#!/usr/bin/env python3
"""render_daemon.py — Worker de render FOTO-LED no host do Content Engine OS.
Regra-mãe (Tiaro 2026-06-14): todo criativo nasce sobre uma IMAGEM com contexto.
Capa/CTA = foto da Dra. (autoridade); miolo = imagem de tema; overlay via gen_foto
(design-system-ivs canônico). Polling em creatives (gerado, gate score>=60).
Sem deps de DB no host: psql via docker exec.
"""
import glob
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request

DS = "/root/cerebro-vital-slim/skills/design-system-ivs"
sys.path.insert(0, DS)
import gen_foto  # noqa: E402
import gen_cientifico  # noqa: E402  (tweets + paper no system design IVS)

# capture_pubmed.py da skill tweet-carrossel: print REAL do paper (cascata de 5 estratégias)
TWEET_SKILL = "/root/.openclaw/workspace/skills/tweet-carrossel/scripts"


def render_cientifico(out, outdir):
    """Carrossel científico no system design IVS.

    Capa = gen_foto (a MESMA diagramação aprovada dos virais: foto real em rodízio,
    Playfair com destaques dourados, sem marca). Slide 2 = rehook tweet. Slide 3 =
    print do paper (capture_pubmed, se houver PMID) — credibilidade. Demais = tweets.
    """
    paths = []
    # 1) capa — idêntica à dos virais aprovados
    paths += gen_foto.render({
        "photo": real_cover(clean(out.get("title")) or ""), "safe_fit": True, "label": "",
        "anchor": 0.62, "zone": "bottom",
        "title": clean(out.get("title")) or "O que a ciência acabou de mostrar",
        "sub": sentences_fit(out.get("cover_sub") or "", 120)
               or "Um estudo que muda a conversa sobre o seu corpo.",
        "cta": "ARRASTA PRO LADO", "size": FEED}, outdir, "slide_01")

    tweets = [str(t).strip() for t in (out.get("tweets") or []) if str(t).strip()][:9]
    ref = (out.get("study_reference") or "").strip()
    pmid = re.sub(r"\D", "", str(out.get("pmid") or ""))

    # 2) paper real (se houver PMID): entra como slide 3, após o rehook
    paper_png = ""
    if pmid:
        cand = os.path.join(outdir, "paper.png")
        try:
            subprocess.run(["python3", os.path.join(TWEET_SKILL, "capture_pubmed.py"),
                            "--pmid", pmid, "--out", cand],
                           check=True, capture_output=True, text=True, timeout=300)
            if os.path.exists(cand) and os.path.getsize(cand) > 5000:
                paper_png = cand
        except Exception as e:
            print("[cientifico] capture_pubmed falhou (%s) -> segue sem slide de paper" % e, flush=True)

    idx = 2
    for i, t in enumerate(tweets):
        paths += gen_cientifico.render_tweet({"tweet": t}, outdir, "slide_%02d" % idx)
        idx += 1
        if i == 0 and paper_png:  # credibilidade logo depois do rehook
            paths += gen_cientifico.render_paper(
                {"paper_image": paper_png, "reference": ref,
                 "intro": "Não é opinião. O estudo existe, publicado e revisado:"},
                outdir, "slide_%02d" % idx)
            idx += 1
    return sorted(paths)

ASSETS = os.path.join(DS, "assets")
DRA_COVER = os.path.join(ASSETS, "dra_blazer.jpg")     # autoridade clínica (capa)
DRA_CTA = os.path.join(ASSETS, "dra_vestido.jpg")      # programa (CTA) — Dra c/ caixa de implantes hormonais (on-context p/ feed; medicação=só orgânico, trocar se for Meta Ads)
SOUL_ID = os.environ.get("DRA_SOUL_ID", "053e3faf-2743-42a3-ae5e-bd0913c3d250")  # Soul v3 Dra Daniely (capa contextual)
TEMAS = [os.path.join(ASSETS, "tema_card%d.png" % i) for i in (1, 2, 3, 4)]          # 4:5
TEMAS_916 = [os.path.join(ASSETS, "tema_card%d_916.png" % i) for i in (1, 2, 3, 4)]  # 9:16
# REGRA CANÔNICA (Tiaro): CARROSSEL/ESTÁTICO = 4:5 (feed) | STORIES/REELS = 9:16
FEED = (1080, 1350)
STORY = (1080, 1920)

RENDERS = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"
HF_CACHE = "/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/hf_cache"
# Produção deve priorizar estabilidade: Higgsfield fica opt-in.
# Quando ligado, cada chamada tem timeout hard com kill do process group para não travar a fila.
HF_ENABLE = os.environ.get("HF_ENABLE", "0") == "1"
HF_TIMEOUT = int(os.environ.get("HF_TIMEOUT", "220"))
HF_STYLE = ("{ctx}. Estilo: fotografia editorial cinematográfica premium, luz natural quente, "
            "tons terrosos e dourados discretos, profundidade de campo, atmosfera sofisticada e íntima, "
            "sem texto, sem palavras, sem letras, sem logotipo, alta qualidade")
PG = ["docker", "exec", "content-engine-postgres", "psql", "-U", "content_engine",
      "-d", "content_engine", "-tAc"]


def hf_image(ctx: str, aspect: str, idx) -> str | None:
    """Gera (ou reusa do cache) a foto de tema do slide via Higgsfield nano_banana_2.
    Retorna o caminho do PNG, ou None p/ cair no banco de assets."""
    if not HF_ENABLE or not ctx.strip():
        return None
    prompt = HF_STYLE.format(ctx=ctx.strip()[:160])
    os.makedirs(HF_CACHE, exist_ok=True)
    dest = os.path.join(HF_CACHE, hashlib.md5((prompt + aspect).encode()).hexdigest()[:16] + ".png")
    if os.path.exists(dest) and os.path.getsize(dest) > 2000:
        return dest
    try:
        cmd = [
            "higgsfield", "generate", "create", "nano_banana_2", "--prompt", prompt,
            "--aspect_ratio", aspect, "--resolution", "2k", "--wait", "--json",
        ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=HF_TIMEOUT)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            raise TimeoutError(f"higgsfield timeout após {HF_TIMEOUT}s")
        if proc.returncode != 0:
            raise RuntimeError((stderr or stdout or f"higgsfield rc={proc.returncode}").strip()[:500])
        url = json.loads(stdout)[0]["result_url"]
        urllib.request.urlretrieve(url, dest)
        if os.path.getsize(dest) > 2000:
            print("[hf] idx%s gerado: %s" % (idx, os.path.basename(dest)), flush=True)
            return dest
    except Exception as e:
        print("[hf-erro] idx%s: %s" % (idx, e), flush=True)
    return None


SOUL_COVER_ENABLE = os.environ.get("SOUL_COVER_ENABLE", "0") == "1"  # capa contextual da Dra (opt-in)


def _cover_has_text(img_path: str) -> bool:
    """OCR conservador (tesseract psm 6): True so com legenda/texto REAL (>=12 letras, >=2 tokens)."""
    try:
        r = subprocess.run(["tesseract", img_path, "-", "--psm", "6", "-l", "por+eng"],
                           capture_output=True, text=True, timeout=30)
        # so conta como TEXTO real se houver >=2 palavras longas (>=5 letras);
        # ruido de OCR em foto produz so tokens curtos (3-4 chars) -> nao dispara
        toks5 = [t for t in re.findall(r"[A-Za-zÀ-ÿ]+", r.stdout or "") if len(t) >= 5]
        return len(toks5) >= 2
    except Exception:
        return False


# Pool de fotos REAIS do ensaio (looks variados, sem props) p/ a capa ALTERNAR. Higgsfield nano_banana_2
# usa uma delas como referencia de identidade -> capa limpa, fiel e diferente a cada peca.
COVER_REFS = [os.environ.get("DRA_FACE_REF", "/root/clone_dra/dra_faces_num/13.png"),
              "/root/clone_dra/dra_faces_num/01.png",
              "/root/clone_dra/dra_faces_num/35.png",
              "/root/clone_dra/dra_faces_num/37.png",
              "/root/clone_dra/dra_faces_num/05.png"]


# Biblioteca de fotos REAIS da Dra (a mesma do módulo /biblioteca/dra). REGRA (feedback 2026-07-06):
# capa SEMPRE com foto real daqui — IA (soul_cover) só quando o roteiro pedir cena específica
# via cover_visual_context. Excluídos do pool de capa: props/contexto (caneta, biomeds, gordura)
# e artefatos (avatar, contact-sheets); seringa/mounjaro já vivem na _BLACKLIST_compliance.
DRA_LIB = "/root/cerebro-vital-slim/cerebro/assets/fotos-dra-daniely"
COVER_POOL_EXCLUDE = ("caneta", "biomeds", "gordura", "avatar", "seringa", "mounjaro")


def real_cover(title: str) -> str:
    """Foto real da biblioteca p/ a capa, em RODÍZIO persistido: cada render usa a próxima
    foto do pool (zero repetição até o pool inteiro circular — hash por título colidia)."""
    try:
        pool = sorted(p for p in glob.glob(os.path.join(DRA_LIB, "daniely-*.png"))
                      if not any(x in os.path.basename(p).lower() for x in COVER_POOL_EXCLUDE))
    except OSError:
        pool = []
    if not pool:
        return DRA_COVER
    state = os.path.join(HF_CACHE, "cover_rotation.json")
    try:
        idx = int(json.load(open(state)).get("i", 0)) % len(pool)
    except Exception:
        idx = int(hashlib.md5((title or "capa").encode()).hexdigest(), 16) % len(pool)
    try:
        os.makedirs(HF_CACHE, exist_ok=True)
        json.dump({"i": idx + 1}, open(state, "w"))
    except OSError:
        pass
    return pool[idx]


def soul_cover(ctx: str, aspect: str = "4:5") -> str | None:
    """Capa ALTERNANTE da Dra via Higgsfield nano_banana_2 (mesmo motor dos slides — limpo, sem texto).
    Seleciona uma foto real do ensaio (COVER_REFS) pelo hash do titulo -> alterna o look a cada peca,
    preservando o rosto real. OCR backstop -> fallback foto fixa. NAO usa text2image_soul_v2 (carimba texto)."""
    # capa contextual independe do HF_ENABLE dos slides (so depende do proprio flag) ->
    # nao altera o comportamento dos slides do miolo.
    if not SOUL_COVER_ENABLE or not (ctx or "").strip():
        return None
    os.makedirs(HF_CACHE, exist_ok=True)
    h = int(hashlib.md5((ctx or "").encode()).hexdigest(), 16)
    prompt = ("Professional studio headshot portrait of the exact woman in the reference image, "
              "same face and identity preserved faithfully, elegant outfit (no lab coat), head and shoulders, "
              "clean neutral studio background, soft premium portrait lighting, warm confident expression, "
              "photorealistic editorial quality, natural skin. Absolutely no text, no words, no letters, "
              "no numbers, no caption, no logo, no watermark, no frame.")
    for attempt in range(3):
        ref = COVER_REFS[(h + attempt) % len(COVER_REFS)]
        if not os.path.exists(ref):
            continue
        dest = os.path.join(HF_CACHE, "cover_" + hashlib.md5((ref + prompt + aspect).encode()).hexdigest()[:16] + ".png")
        if os.path.exists(dest) and os.path.getsize(dest) > 2000:
            if not _cover_has_text(dest):
                return dest
            continue
        try:
            cmd = ["higgsfield", "generate", "create", "nano_banana_2", "--prompt", prompt,
                   "--image", ref, "--aspect_ratio", aspect, "--resolution", "2k", "--wait", "--json"]
            proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, start_new_session=True)
            try:
                stdout, stderr = proc.communicate(timeout=HF_TIMEOUT)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
                raise TimeoutError("cover timeout apos %ss" % HF_TIMEOUT)
            if proc.returncode != 0:
                raise RuntimeError((stderr or stdout or "rc!=0").strip()[:500])
            url = json.loads(stdout)[0]["result_url"]
            urllib.request.urlretrieve(url, dest)
            if os.path.getsize(dest) > 2000 and not _cover_has_text(dest):
                print("[cover] capa alternante limpa (ref %s): %s" % (os.path.basename(ref), os.path.basename(dest)), flush=True)
                return dest
            print("[cover] tentativa %d com texto, trocando ref" % (attempt + 1), flush=True)
        except Exception as e:
            print("[cover-erro] tentativa %d: %s" % (attempt + 1, e), flush=True)
    print("[cover] sem capa limpa -> fallback foto fixa", flush=True)
    return None

def psql(sql: str) -> str:
    result = subprocess.run(PG + [sql], capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "psql failed").strip()
        raise RuntimeError(detail[:500])
    return result.stdout.strip()


def esc(s: str) -> str:
    return (s or "").replace("'", "''")


def clean(s) -> str:
    s = str(s or "").strip()
    s = re.sub(r"^\s*(slide|cena|frame)\s*\d+\s*(\([^)]*\))?\s*[–\-:]\s*", "", s, flags=re.I)
    if ":" in s[:24]:
        s = re.sub(r"^\s*[A-Za-zÀ-ú ]{2,18}:\s*", "", s)
    s = s.strip().strip('"')
    return " ".join(s.split())


def split_head_body(s: str):
    s = clean(s)
    m = re.split(r"[:–]\s+", s, maxsplit=1)
    if len(m) == 2 and len(m[0]) <= 42:
        return m[0].strip(), m[1].strip()
    parts = re.split(r"(?<=[.!?])\s+", s, maxsplit=1)
    return parts[0][:60].strip(), (parts[1].strip() if len(parts) > 1 else None)


def sentences_fit(s, n):
    s = clean(s)
    if not s:
        return None
    acc = ""
    for sent in re.findall(r"[^.!?]*[.!?]", s):
        if acc and len(acc) + len(sent) > n:  # so corta DEPOIS de ja ter 1 frase
            break
        acc += sent
    acc = (acc.strip() or s.strip())          # garante a 1a frase mesmo se passar de n
    if len(acc) > n:                          # trunca por palavra ate n, com reticencias
        cut = acc[:n].rsplit(" ", 1)[0].rstrip(",;:.- ")
        acc = (cut + "…") if cut else acc[:n]
    return acc or None


def parse_out(c):
    out = c.get("script")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            out = {}
    return out or {}


def build_slides(c):
    """Lista de specs gen_foto (foto-led) — um por peça/slide."""
    fmt = (c.get("format") or "estatico").lower()
    out = parse_out(c)

    if fmt == "carrossel":
        destino = out.get("destino", "feed")
        raw = out.get("slides") or []
        structured = bool(raw) and isinstance(raw[0], dict)
        word_v = re.sub(r"[^A-ZÀ-Ü]", "", (out.get("cta_comment_word") or "").upper())
        cta_label = "QUERO SER AVALIADA" if destino == "meta_ads" \
            else (("COMENTA " + word_v) if word_v else "SALVA E COMPARTILHA")
        # CAPA = stop-scroll: foto REAL da biblioteca (alterna por peça), SEM label de marca
        # (a Vital Slim só aparece nos slides de método/solução e no CTA). IA na capa apenas
        # quando o roteiro pede cena específica (cover_visual_context) que a biblioteca não tem.
        ctx_ai = (out.get("cover_visual_context") or "").strip()
        cover_photo = (soul_cover(ctx_ai, "4:5") if ctx_ai else None) \
            or real_cover(clean(out.get("title")) or "")
        slides = [{
            "photo": cover_photo, "safe_fit": True, "label": "", "anchor": 0.62, "zone": "bottom",
            "title": clean(out.get("title")) or "Toda mulher 40+ precisa saber disso.",
            "sub": sentences_fit(out.get("cover_sub") or out.get("hook", ""), 120)
                   or "O que ninguém te explicou sobre o seu corpo depois dos 40.",
            "cta": "ARRASTA PRO LADO", "size": FEED}]
        if structured:
            for i, s in enumerate(raw, 1):
                photo = hf_image((s.get("image_prompt") or "").strip(), "4:5", i) \
                    or TEMAS[(i - 1) % len(TEMAS)]
                slides.append({
                    "photo": photo, "label": s.get("label") or ("SINAL %d" % i),
                    "anchor": 0.5, "zone": "bottom", "title": clean(s.get("headline")) or "—",
                    "sub": sentences_fit(s.get("sub", ""), 160),
                    "cta": "ARRASTA PRO LADO", "size": FEED})
        else:  # legado: slides como strings
            mid = raw[1:-1] if len(raw) > 2 else raw
            for i, s in enumerate(mid, 1):
                head, body = split_head_body(s)
                ctx = ("%s %s" % (head, body or "")).strip()
                photo = hf_image(ctx, "4:5", i) or TEMAS[(i - 1) % len(TEMAS)]
                slides.append({
                    "photo": photo, "label": "SINAL %d" % i, "anchor": 0.5, "zone": "bottom",
                    "title": head, "sub": sentences_fit(body, 160),
                    "cta": "ARRASTA PRO LADO", "size": FEED})
        # CTA final (Dra. vestido) — label muda no Meta Ads (conversão)
        slides.append({
            "photo": DRA_CTA, "label": "INSTITUTO VITAL SLIM", "anchor": 0.5, "zone": "bottom",
            "title": clean(out.get("cta_headline")) or "Salve e compartilhe.",
            "sub": sentences_fit(out.get("cta_sub") or out.get("caption", ""), 170)
                   or "Mande para quem precisa ouvir isso.",
            "cta": cta_label, "size": FEED})
        return slides

    if fmt in ("reels", "stories"):
        return [{
            "photo": DRA_COVER, "story": True, "anchor": 0.55, "zone": "bottom",
            "label": "INSTITUTO VITAL SLIM",
            "title": clean(out.get("hook") or out.get("title")) or "Instituto Vital Slim",
            "cta": "SALVA ESSE VÍDEO"}]

    # estático — afirmação única foto-led (4:5 feed)
    return [{
        "photo": DRA_COVER, "anchor": 0.62, "zone": "bottom", "size": FEED,
        "title": clean(out.get("headline") or out.get("title")) or "Instituto Vital Slim",
        "sub": sentences_fit(out.get("body", ""), 160), "cta": "SALVA ESSE POST"}]


def fetch_pending():
    raw = psql("""
        with picked as (
            select id
            from creatives
            where status='gerado'
              and asset_url is null
              and coalesce(quality_score,0) >= 60
            order by created_at
            for update skip locked
            limit 5
        ), claimed as (
            update creatives c
            set status='renderizando'
            from picked p
            where c.id = p.id
            returning c.id::text as id, c.format, c.network,
                      c.script, c.title, c.caption
        )
        select coalesce(json_agg(claimed), '[]'::json)::text
        from claimed;
    """)
    try:
        return json.loads(raw or "[]")
    except Exception as exc:
        raise RuntimeError("invalid render claim payload") from exc


def process(c):
    cid = c["id"]
    outdir = os.path.join(RENDERS, cid)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):   # limpa renders antigos (evita stale/mistura de versões)
        try:
            os.remove(os.path.join(outdir, f))
        except OSError:
            pass
    try:
        out = parse_out(c)
        if (c.get("format") or "").lower() == "carrossel" and (out.get("modelo") or "").lower() == "cientifico":
            paths = render_cientifico(out, outdir)
        else:
            slides = build_slides(c)
            paths = []
            for i, spec in enumerate(slides, 1):
                paths += gen_foto.render(spec, outdir, "slide_%02d" % i)
        if not paths:
            raise RuntimeError("nenhum arquivo gerado")
        first = "/renders/%s/%s" % (cid, os.path.basename(sorted(paths)[0]))
        updated = psql(
            "update creatives set asset_url='%s', status='renderizado' "
            "where id='%s' and status='renderizando' returning id::text;"
            % (esc(first), cid)
        )
        if cid not in updated:
            raise RuntimeError("render claim was lost before completion")
        print("[ok] %s -> %d peça(s) foto-led (%s)" % (cid, len(paths), first), flush=True)
        try:  # aviso Telegram (cos_notify) — falha aqui NUNCA quebra o render
            titulo = (c.get("title") or "").strip() or cid[:8]
            subprocess.run(
                ["/usr/bin/python3", "/root/bin/cos_notify.py",
                 "🖼️ Peça pronta para revisar: %s → https://conteudo.institutovitalslim.com.br/banco-criativos" % titulo],
                capture_output=True, timeout=30)
        except Exception as _e:
            print("[aviso] %s notificacao falhou (nao-fatal): %s" % (cid, _e), flush=True)
        try:
            script_payload = c.get("script")
            if script_payload:
                import tts_dra
                narration = (
                    json.dumps(script_payload, ensure_ascii=False)
                    if isinstance(script_payload, (dict, list))
                    else str(script_payload)
                )
                tts_dra.narrate(narration, os.path.join(outdir, "narracao.mp3"))
                print("[ok] %s -> narracao (voz Dra PVC)" % cid, flush=True)
        except Exception as _e:
            print("[aviso] %s narracao falhou (nao-fatal): %s" % (cid, _e), flush=True)
    except Exception as e:
        psql("update creatives set status='render_erro' where id='%s';" % cid)
        print("[erro] %s: %s" % (cid, e), flush=True)


def main():
    os.makedirs(RENDERS, exist_ok=True)
    print("render-daemon FOTO-LED iniciado (poll 5s) -> %s" % RENDERS, flush=True)
    while True:
        for c in fetch_pending():
            process(c)
        time.sleep(5)


if __name__ == "__main__":
    main()
