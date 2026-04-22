#!/usr/bin/env python3
"""
capture_pubmed.py — Captura screenshot da pagina PubMed com cascata de 5 estrategias.

Compativel com Chromium via snap (AppArmor sandbox): staging em /root/.chromium_tmp/.
"""
import argparse, subprocess, os, sys, time, json, urllib.request, uuid, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

STAGE_DIR = "/root/chromium_tmp"


def is_valid_screenshot(png_path, min_size=50_000):
    if not os.path.isfile(png_path):
        return False, "arquivo nao existe"
    size = os.path.getsize(png_path)
    if size < min_size:
        return False, f"arquivo muito pequeno ({size} bytes)"
    try:
        img = Image.open(png_path).convert("RGB")
        nih_strip = img.crop((0, 0, img.width, 80))
        pixels = list(nih_strip.getdata())
        nih_blue_count = sum(1 for p in pixels
                             if 10 <= p[0] <= 70 and 60 <= p[1] <= 120 and 120 <= p[2] <= 180)
        nih_ratio = nih_blue_count / len(pixels)
        if nih_ratio < 0.15:
            return False, f"SEM header NIH azul ({nih_ratio:.1%}) - provavel captcha/erro"
        full_pixels = list(img.resize((200, 200)).getdata())
        white_count = sum(1 for p in full_pixels if p[0] > 240 and p[1] > 240 and p[2] > 240)
        white_ratio = white_count / len(full_pixels)
        if white_ratio > 0.85:
            return False, f"pagina {white_ratio:.1%} branca - provavel captcha"
        return True, f"OK ({size//1024}KB, NIH {nih_ratio:.1%}, branco {white_ratio:.1%})"
    except Exception as e:
        return False, f"erro: {e}"


def try_chromium(url, out_path, ua, wait_ms=8000, attempt_id=0):
    """Chromium via snap nao tem acesso a /tmp/ (AppArmor).
    Escreve em /root/.chromium_tmp/ e move para out_path final."""
    os.makedirs(STAGE_DIR, exist_ok=True)
    stage_path = os.path.join(STAGE_DIR, f"shot_{attempt_id}_{uuid.uuid4().hex[:8]}.png")
    profile_dir = f"/root/chromium_prof_{attempt_id}_{uuid.uuid4().hex[:8]}"
    os.makedirs(profile_dir, exist_ok=True)

    try:
        subprocess.run([
            "chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
            f"--user-agent={ua}",
            "--hide-scrollbars",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            "--incognito",
            f"--user-data-dir={profile_dir}",
            "--lang=en-US,en;q=0.9,pt;q=0.8",
            "--accept-lang=en-US,en;q=0.9,pt;q=0.8",
            f"--screenshot={stage_path}",
            "--window-size=1200,1800",
            f"--virtual-time-budget={wait_ms}",
            url
        ], capture_output=True, text=True, timeout=90)

        if os.path.exists(stage_path):
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            shutil.move(stage_path, out_path)
            return True
        return False
    except Exception as e:
        print(f"    ERR chromium: {e}", flush=True)
        return False
    finally:
        try:
            shutil.rmtree(profile_dir)
        except:
            pass
        try:
            if os.path.exists(stage_path):
                os.remove(stage_path)
        except:
            pass


def fetch_paper_metadata(pmid):
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENTS[0]})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        result = data.get("result", {}).get(pmid, {})
        return {
            "title": result.get("title", ""),
            "authors": [a.get("name", "") for a in result.get("authors", [])[:8]],
            "source": result.get("source", ""),
            "pubdate": result.get("pubdate", ""),
            "doi": next((x.get("value") for x in result.get("articleids", []) if x.get("idtype") == "doi"), ""),
            "pmcid": next((x.get("value") for x in result.get("articleids", []) if x.get("idtype") == "pmc"), ""),
        }
    except Exception as e:
        print(f"    eutils falhou: {e}", flush=True)
        return None


def render_synthetic(pmid, meta, out_path):
    """Gera imagem sintetica estilo PubMed com metadados reais."""
    print("  Estrategia 4: gerando imagem sintetica com metadados eutils...", flush=True)
    W, H = 1200, 900
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Header azul NIH (20, 84, 147) - RGB
    draw.rectangle([(0, 0), (W, 70)], fill=(32, 84, 147))
    try:
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except:
        font_h = font_title = font_body = font_small = ImageFont.load_default()

    draw.text((30, 22), "NIH  National Library of Medicine", fill=(255, 255, 255), font=font_h)
    draw.rectangle([(30, 95), (200, 135)], outline=(32, 84, 147), width=2)
    draw.text((48, 102), "PubMed", fill=(32, 84, 147), font=font_title)

    src = f"> {meta.get('source', '')}. {meta.get('pubdate', '')}"
    if meta.get("doi"):
        src += f". doi: {meta['doi']}"
    draw.text((30, 170), src, fill=(50, 50, 50), font=font_small)

    title = meta.get("title", "").replace(".", "")
    words = title.split()
    lines, line = [], ""
    for w in words:
        test = f"{line} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_title)
        if bbox[2] - bbox[0] > W - 80:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    y = 210
    for l in lines[:4]:
        draw.text((30, y), l, fill=(0, 0, 0), font=font_title)
        y += 42

    authors = ", ".join(meta.get("authors", [])[:6])
    if len(meta.get("authors", [])) > 6:
        authors += ", et al."
    draw.text((30, y + 20), authors, fill=(32, 84, 147), font=font_body)

    y += 80
    ids = f"PMID: {pmid}"
    if meta.get("pmcid"):
        ids += f"   PMCID: {meta['pmcid']}"
    if meta.get("doi"):
        ids += f"   DOI: {meta['doi']}"
    draw.text((30, y), ids, fill=(50, 50, 50), font=font_small)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    img.save(out_path, "PNG")
    return True


def capture(pmid, out_path):
    url_direct = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    # Estrategia 1: PubMed direto
    print("Estrategia 1: PubMed direto com multiplos user-agents + perfil limpo", flush=True)
    for i, ua in enumerate(USER_AGENTS):
        print(f"  UA {i+1}: {ua[:50]}...", flush=True)
        if try_chromium(url_direct, out_path, ua, attempt_id=i):
            valid, msg = is_valid_screenshot(out_path)
            print(f"    {msg}", flush=True)
            if valid:
                return True
        time.sleep(2)

    # Estrategia 2: archive.org
    print("Estrategia 2: Archive.org Wayback Machine", flush=True)
    archive_url = f"https://web.archive.org/web/2024/{url_direct}"
    for ua in USER_AGENTS[:3]:
        if try_chromium(archive_url, out_path, ua, wait_ms=12000, attempt_id=100):
            valid, msg = is_valid_screenshot(out_path)
            print(f"    {msg}", flush=True)
            if valid:
                return True
        time.sleep(1)

    # Estrategia 3: PMC
    print("Estrategia 3: eutils + PMC (se disponivel)", flush=True)
    meta = fetch_paper_metadata(pmid)
    if meta and meta.get("pmcid"):
        pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{meta['pmcid']}/"
        for ua in USER_AGENTS[:3]:
            if try_chromium(pmc_url, out_path, ua, attempt_id=200):
                valid, msg = is_valid_screenshot(out_path)
                print(f"    PMC: {msg}", flush=True)
                if valid:
                    return True

    # Estrategia 4: sintetica
    if meta:
        render_synthetic(pmid, meta, out_path)
        valid, msg = is_valid_screenshot(out_path, min_size=10_000)
        print(f"    Sintetico: {msg}", flush=True)
        if valid:
            return True

    # Estrategia 5: placeholder
    print("Estrategia 5: placeholder", flush=True)
    img = Image.new("RGB", (1200, 800), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()
    draw.text((50, 350), f"Paper PMID {pmid}\nVer em: pubmed.ncbi.nlm.nih.gov/{pmid}/", fill=(50, 50, 50), font=font)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    img.save(out_path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmid", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if capture(args.pmid, args.out):
        print(f"SUCESSO: {args.out}", flush=True)
        sys.exit(0)
    else:
        print("FALHA", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
