#!/usr/bin/env python3
"""
e2e_real_test.py — Simula cenario real: Tiaro envia pedido e Clara gera carrossel
completo de 10 slides JPEG + envia pelo Telegram.

Tema teste: "Creatina para mulheres acima de 40" (diferente do ja armazenado sobre
creatina-cognitivo).
"""
import subprocess, os, base64, json, shutil
from pathlib import Path
from PIL import Image
from datetime import datetime

SCRIPTS = Path("/root/.openclaw/workspace/skills/tweet-carrossel/scripts")
MEM = Path("/root/.openclaw/workspace/skills/memoria-cientifica/scripts")
OUT_DIR = Path(f"/root/cerebro-vital-slim/deliverables/e2e-test-creatina-40-{datetime.now().strftime('%Y-%m-%d_%H%M')}")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP = OUT_DIR / "tmp"
TMP.mkdir(exist_ok=True)

os.environ["GOOGLE_API_KEY"] = "AIzaSyAQcy8URejQXMEQS1MYrVDRUgdNGH6CrDo"

errors = []


def step(name, fn):
    print(f"\n{'='*5} {name} {'='*5}")
    try:
        return fn()
    except Exception as e:
        errors.append(f"{name}: {e}")
        print(f"ERRO: {e}")
        return None


# ========== 1. Busca na memoria ==========
def search_memory():
    r = subprocess.run([
        "python3", str(MEM / "memory_search.py"),
        "--query", "creatina mulheres acima 40 anos menopausa",
        "--top-k", "2", "--format", "json"
    ], capture_output=True, text=True, timeout=90)
    try:
        data = json.loads(r.stdout)
        top_score = data[0]["score"] if data else 0
        print(f"Top-1 score: {top_score:.3f}")
        return top_score, data
    except:
        return 0, None


# ========== 2. Capturar paper PubMed ==========
def capture_paper():
    out = TMP / "pubmed_39070254.png"
    subprocess.run([
        "python3", str(SCRIPTS / "capture_pubmed.py"),
        "--pmid", "39070254", "--out", str(out)
    ], capture_output=True, text=True, timeout=300)
    ok = out.exists() and out.stat().st_size > 10_000
    print(f"Paper: {out.stat().st_size//1024 if out.exists() else 0}KB - {'OK' if ok else 'FALHOU'}")
    return ok, out


# ========== 3. Selecionar foto da Dra ==========
def select_photo():
    r = subprocess.run([
        "python3", str(SCRIPTS / "photo_selector.py"),
        "--theme", "creatina suplemento mulher saude feminina emagrecimento",
        "--top-k", "3", "--format", "json"
    ], capture_output=True, text=True, timeout=90)
    try:
        data = json.loads(r.stdout)
        best = data["best_match"]["filename"]
        score = data["best_match"]["semantic_score"]
        print(f"Foto: {best} (score {score})")
        return f"/root/.openclaw/workspace/fotos_dra/originais/{best}"
    except Exception as e:
        print(f"ERR: {e}")
        return "/root/.openclaw/workspace/fotos_dra/dra_seria_frontal.png"


# ========== 4. Gerar capa ==========
def gen_cover(foto):
    r = subprocess.run([
        "python3", str(SCRIPTS / "compose_cover.py"),
        "--foto", foto, "--tema", "consultorio medico moderno com luz natural lateral",
        "--headline", "CREATINA|NÃO É SÓ|PRA QUEM MALHA|É PRA MULHER 40+",
        "--destaques", "CREATINA,NÃO É SÓ,MULHER,40+",
        "--out", str(OUT_DIR / "slide_01.jpg")
    ], capture_output=True, text=True, timeout=600)
    ok = (OUT_DIR / "slide_01.jpg").exists()
    sz = (OUT_DIR / "slide_01.jpg").stat().st_size // 1024 if ok else 0
    print(f"Capa: {sz}KB - {'OK' if ok else 'FALHOU'}")
    return ok


# ========== 5. Gerar slide 2 (paper) ==========
def gen_slide2(paper_path):
    from base64 import b64encode
    # Crop paper
    img = Image.open(paper_path).convert("RGB")
    w, h = img.size
    if h < 1000:
        cropped = img.crop((0, 0, w, min(h, 800)))
    else:
        cropped = img.crop((0, 0, w, 720))
    crop_out = TMP / "paper_crop.png"
    cropped.save(crop_out)
    paper_b64 = b64encode(crop_out.read_bytes()).decode()

    avatar_b64 = Path("/root/avatar_hq_b64.txt").read_text().strip()

    lines = [
        "Meta-análise de <b>16 ECRs</b> com 492 participantes mostrou melhora em memória, atenção e processamento cognitivo.",
        "Os efeitos mais fortes apareceram em <b>mulheres</b>. &rarr;",
    ]
    lines_html = "".join(f"<p>{l}</p>" for l in lines)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1350px; background:#000; color:#c8c8c8;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  overflow:hidden; }}
body {{ padding:60px 64px; display:flex; flex-direction:column; }}
.header {{ display:flex; align-items:center; gap:28px; margin-bottom:44px; flex-shrink:0; }}
.avatar {{ width:96px; height:96px; border-radius:50%; overflow:hidden; flex-shrink:0; }}
.avatar img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.user-info {{ display:flex; flex-direction:column; gap:4px; }}
.name-row {{ display:flex; align-items:center; line-height:1.15; }}
.name {{ font-weight:700; font-size:40px; color:#fff; }}
.verified {{ display:inline-block; width:32px; height:32px; background:#1d9bf0;
  border-radius:50%; text-align:center; line-height:32px; font-size:17px; color:#fff;
  margin-left:10px; font-weight:700; }}
.handle {{ color:#71767b; font-size:30px; }}
p {{ font-size:44px; line-height:1.30; color:#c8c8c8; margin-bottom:28px; font-weight:400; }}
b {{ color:#fff; font-weight:600; }}
.breathing {{ flex:1; display:flex; align-items:center; justify-content:center; margin-top:24px; }}
.paper-wrap {{ width:100%; border-radius:10px; overflow:hidden; }}
.paper-wrap img {{ width:100%; display:block; }}
</style></head><body>
<div class="header">
  <div class="avatar"><img src="data:image/png;base64,{avatar_b64}"></div>
  <div class="user-info">
    <div class="name-row"><span class="name">Dra. Daniely Freitas</span><span class="verified">&#10003;</span></div>
    <div class="handle">@dradaniely.freitas</div>
  </div>
</div>
<div>{lines_html}</div>
<div class="breathing"><div class="paper-wrap"><img src="data:image/png;base64,{paper_b64}"></div></div>
</body></html>"""

    html_path = TMP / "slide_02.html"
    html_path.write_text(html, encoding="utf-8")
    png_out = TMP / "slide_02.png"
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox",
                    f"--screenshot={png_out}", "--window-size=1080,1350",
                    f"file://{html_path}"], capture_output=True, timeout=60)
    jpg_out = OUT_DIR / "slide_02.jpg"
    if png_out.exists():
        Image.open(png_out).convert("RGB").save(jpg_out, "JPEG", quality=85, optimize=True)
        print(f"Slide 2: {jpg_out.stat().st_size//1024}KB")
        return True
    return False


# ========== 6. Slides 3-10 ==========
def gen_slides_tweet():
    avatar_b64 = Path("/root/avatar_hq_b64.txt").read_text().strip()
    contents = {
        3: ["A creatina deixou de ser suplemento só de academia.",
            "Hoje ela é estudada como <b>aliada da saúde feminina</b>, principalmente depois dos 40.",
            "E os motivos são concretos. &rarr;"],
        4: ["<b>Eixo 1: Cérebro</b>",
            "Com 40+ anos, memória e foco podem piorar por queda hormonal e desgaste mitocondrial.",
            "Creatina aumenta fosfocreatina cerebral em <b>8-15%</b>, sustentando o ATP neural."],
        5: ["<b>Eixo 2: Massa magra</b>",
            "Após os 40, mulheres perdem massa muscular mais rápido.",
            "Creatina potencializa o treino e ajuda a <b>preservar músculo</b> - essencial para metabolismo ativo."],
        6: ["<b>Eixo 3: Humor e energia</b>",
            "Estudos recentes mostram efeito antidepressivo discreto mas consistente.",
            "Principalmente em mulheres com sintomas de fadiga mental e humor instável."],
        7: ["<b>Dose e forma</b>",
            "Creatina monohidratada micronizada",
            "<b>3-5g/dia</b> uso contínuo",
            "Tomar com refeição, evitar com café",
            "Efeito cognitivo aparece em 3-4 semanas."],
        8: ["<b>Atenção no consultório</b>",
            "Antes: creatinina, ureia, TFG",
            "30 dias: creatinina (pode subir 0,1-0,2 sem indicar lesão renal)",
            "Explicar ganho de 0,5-1kg de água intracelular (não gordura)."],
        9: ["Contraindicações:",
            "&rarr; IRC estágio 3+",
            "&rarr; Gravidez (dados insuficientes)",
            "&rarr; Diurético de alça em altas doses",
            "Com supervisão médica, creatina é segura."],
        10: ["Mulher 40+ que treina, trabalha, estuda, tem filho e ainda quer <b>cabeça leve e corpo forte</b>?",
            "Creatina pode ser uma das peças.",
            "<b>Salve este post</b>. Avaliação clínica? Manda <b>CREATINA</b> no direct. &rarr;"],
    }

    results = []
    for num, lines in contents.items():
        lines_html = "".join(f"<p>{l}</p>" for l in lines)
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1350px; background:#000; color:#c8c8c8;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  overflow:hidden; }}
body {{ padding:60px 64px; display:flex; flex-direction:column; }}
.centered {{ flex:1; display:flex; flex-direction:column; justify-content:center; }}
.header {{ display:flex; align-items:center; gap:28px; margin-bottom:44px; }}
.avatar {{ width:96px; height:96px; border-radius:50%; overflow:hidden; flex-shrink:0; }}
.avatar img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.user-info {{ display:flex; flex-direction:column; gap:4px; }}
.name-row {{ display:flex; align-items:center; line-height:1.15; }}
.name {{ font-weight:700; font-size:40px; color:#fff; }}
.verified {{ display:inline-block; width:32px; height:32px; background:#1d9bf0;
  border-radius:50%; text-align:center; line-height:32px; font-size:17px; color:#fff;
  margin-left:10px; font-weight:700; }}
.handle {{ color:#71767b; font-size:30px; }}
p {{ font-size:44px; line-height:1.30; color:#c8c8c8; margin-bottom:28px; font-weight:400; }}
b {{ color:#fff; font-weight:600; }}
</style></head><body>
<div class="centered">
<div class="header">
  <div class="avatar"><img src="data:image/png;base64,{avatar_b64}"></div>
  <div class="user-info">
    <div class="name-row"><span class="name">Dra. Daniely Freitas</span><span class="verified">&#10003;</span></div>
    <div class="handle">@dradaniely.freitas</div>
  </div>
</div>
<div>{lines_html}</div>
</div>
</body></html>"""
        html_path = TMP / f"slide_{num:02d}.html"
        html_path.write_text(html, encoding="utf-8")
        png_out = TMP / f"slide_{num:02d}.png"
        subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox",
                        f"--screenshot={png_out}", "--window-size=1080,1350",
                        f"file://{html_path}"], capture_output=True, timeout=60)
        jpg_out = OUT_DIR / f"slide_{num:02d}.jpg"
        if png_out.exists():
            Image.open(png_out).convert("RGB").save(jpg_out, "JPEG", quality=85, optimize=True)
            results.append((num, jpg_out.stat().st_size // 1024))
    print(f"Slides 3-10: {len(results)} gerados — {[r[1] for r in results]} KB")
    return len(results) == 8


# ========== 7. Validar ==========
def validate():
    files = sorted(OUT_DIR.glob("slide_*.jpg"))
    print(f"\n{len(files)} slides no diretorio:")
    for f in files:
        sz = f.stat().st_size
        print(f"  {f.name}: {sz//1024}KB" + (" OK" if sz > 10_000 else " ⚠️ PEQUENO"))
    return len(files) == 10 and all(f.stat().st_size > 10_000 for f in files)


# ========== 8. Enviar ==========
def send_telegram():
    r = subprocess.run([
        "python3", str(SCRIPTS / "send_to_telegram.py"),
        "--chat-id", "-1003803476669", "--thread-id", "4",
        "--dir", str(OUT_DIR),
        "--caption", "🧪 TESTE E2E VALIDACAO — Carrossel 'Creatina pra mulher 40+'. Pipeline completo rodado sem supervisao (memory_search + capture_pubmed + compose_cover + slide 2 paper + 8 slides tweet + send_telegram)."
    ], capture_output=True, text=True, timeout=120,
       env={**os.environ, "TELEGRAM_BOT_TOKEN": "8602727694:AAFr7C50fHVI67sh9IWcyfv8HdwjDxRt9LU"})
    ok = "OK:" in r.stdout
    print(r.stdout[-300:])
    return ok


# ========== Execucao ==========
print("🧪 TESTE E2E REAL — CARROSSEL NOVO 'CREATINA 40+'")
print("=" * 70)

score, _ = step("1. Busca na memoria", search_memory)
paper_ok, paper_path = step("2. Capturar paper PubMed", capture_paper)
foto = step("3. Selecionar foto", select_photo)
cover_ok = step("4. Gerar capa", lambda: gen_cover(foto))
slide2_ok = step("5. Slide 2 paper", lambda: gen_slide2(paper_path) if paper_ok else False)
slides_ok = step("6. Slides 3-10", gen_slides_tweet)
valid = step("7. Validar 10 JPEGs", validate)
sent = step("8. Enviar Telegram", send_telegram)

print("\n" + "=" * 70)
print("RESULTADO E2E")
print("=" * 70)
print(f"Memoria search:   score {score:.3f}")
print(f"Paper PubMed:     {'✅' if paper_ok else '❌'}")
print(f"Foto selecionada: {Path(foto).name}")
print(f"Capa:             {'✅' if cover_ok else '❌'}")
print(f"Slide 2:          {'✅' if slide2_ok else '❌'}")
print(f"Slides 3-10:      {'✅' if slides_ok else '❌'}")
print(f"Validacao:        {'✅' if valid else '❌'}")
print(f"Telegram:         {'✅' if sent else '❌'}")

if errors:
    print("\nERROS:")
    for e in errors:
        print(f"  - {e}")

print(f"\nDiretorio: {OUT_DIR}")
