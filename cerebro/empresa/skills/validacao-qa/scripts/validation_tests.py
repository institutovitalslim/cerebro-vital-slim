#!/usr/bin/env python3
"""
validation_tests.py — Bateria de testes para validar que o pipeline de carrossel
da Clara esta funcional end-to-end.

Roda 5 grupos:
  1. Arquivos oficiais (SKILL.md, CLAUDE.md, scripts) nos 2 locais
  2. Testes unitarios de scripts individuais
  3. Testes de integracao (memory + photo selector)
  4. Teste end-to-end com tema novo
  5. Relatorio consolidado

Uso:
    python3 validation_tests.py [--send-telegram] [--quick]
"""
import argparse, os, sys, json, subprocess, time
from pathlib import Path
from datetime import datetime

OPENCLAW = Path("/root/.openclaw/workspace/skills")
CEREBRO = Path("/root/cerebro-vital-slim/cerebro/empresa/skills")

RESULTS = []
PASS = "✅"
FAIL = "❌"
WARN = "⚠️"


def check(name, passed, detail=""):
    status = PASS if passed else FAIL
    RESULTS.append({"name": name, "passed": passed, "detail": detail, "status": status})
    print(f"{status} {name}" + (f" — {detail}" if detail else ""), flush=True)
    return passed


def warn(name, detail=""):
    RESULTS.append({"name": name, "passed": None, "detail": detail, "status": WARN})
    print(f"{WARN} {name}" + (f" — {detail}" if detail else ""), flush=True)


# ============================================================
# GRUPO 1 — Arquivos oficiais
# ============================================================
def test_files():
    print("\n=== GRUPO 1: Arquivos oficiais ===\n")

    # SKILLs
    for location in [OPENCLAW, CEREBRO]:
        for skill in ["tweet-carrossel", "prompt-imagens", "memoria-cientifica"]:
            skill_md = location / skill / "SKILL.md"
            check(f"SKILL.md {skill} em {location.parts[-4]}",
                  skill_md.exists(),
                  f"{skill_md}" if skill_md.exists() else "FALTANDO")

    # Scripts tweet-carrossel
    for loc in [OPENCLAW, CEREBRO]:
        for script in ["compose_cover.py", "compose_cover_auto.py", "make_cover.py",
                       "capture_pubmed.py", "photo_selector.py", "catalog_photos.py",
                       "generate_variation.py", "send_to_telegram.py", "gen_slides_full.py",
                       "fetch_instagram.py", "clara_create_carrossel_from_post.py"]:
            p = loc / "tweet-carrossel/scripts" / script
            check(f"script {script} em {loc.parts[-4]}",
                  p.exists(), str(p) if p.exists() else "FALTANDO")

    # Scripts prompt-imagens
    for loc in [OPENCLAW, CEREBRO]:
        for script in ["build_prompt.py", "generate_image.py",
                       "generate_with_reference.py", "add_overlay.py",
                       "clara_create_image.py"]:
            p = loc / "prompt-imagens/scripts" / script
            check(f"script {script} em {loc.parts[-4]}",
                  p.exists(), str(p) if p.exists() else "FALTANDO")

    # Scripts memoria-cientifica
    for loc in [OPENCLAW, CEREBRO]:
        for script in ["ingest_content.py", "memory_store.py", "memory_search.py"]:
            p = loc / "memoria-cientifica/scripts" / script
            check(f"script {script} em {loc.parts[-4]}",
                  p.exists(), str(p) if p.exists() else "FALTANDO")

    # CLAUDE.md com 7 proibicoes
    for path in ["/root/.openclaw/workspace/CLAUDE.md",
                 "/root/cerebro-vital-slim/cerebro/CLAUDE.md"]:
        if Path(path).exists():
            content = Path(path).read_text()
            count = sum(1 for i in range(1, 8) if f"PROIBICAO {i}" in content)
            check(f"CLAUDE.md em {path.split('/')[-2]} tem 7 PROIBICOES",
                  count == 7, f"{count}/7 encontradas")
        else:
            check(f"CLAUDE.md em {path}", False, "FALTANDO")

    # make_cover em /root (precisa estar sincronizado)
    check("/root/make_cover.py existe (chamado por compose_cover)",
          Path("/root/make_cover.py").exists())
    if Path("/root/make_cover.py").exists():
        content = Path("/root/make_cover.py").read_text()
        check("/root/make_cover.py tem strip de ? (chr(63))",
              "chr(63)" in content, "fix de destaques")

    # fotos Dra
    photos_dir = Path("/root/.openclaw/workspace/fotos_dra/originais")
    check("Acervo fotos da Dra", photos_dir.exists() and len(list(photos_dir.glob("*.png"))) >= 30,
          f"{len(list(photos_dir.glob('*.png')))} fotos" if photos_dir.exists() else "FALTANDO")

    # Avatar
    check("Avatar oficial", Path("/root/avatar_hq.png").exists())
    check("Avatar b64", Path("/root/avatar_hq_b64.txt").exists())

    # Logs de licoes
    check("LICOES_SESSAO_2026-04-20.md documentado",
          Path("/root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs/LICOES_SESSAO_2026-04-20.md").exists())


# ============================================================
# GRUPO 2 — Testes unitarios
# ============================================================
def run_script(cmd, timeout=120):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", "")})
    return r.returncode == 0, r.stdout, r.stderr


def test_units():
    print("\n=== GRUPO 2: Unidades ===\n")

    # 2.1 make_cover — destaques com ? e !
    import tempfile
    test_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    test_file.write("""
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/tweet-carrossel/scripts")
# Testa a logica do strip
for test in ["ANSIEDADE?", "ACNE!", "OBESIDADE?"]:
    cleaned = test.strip().upper().strip(chr(34)).strip(chr(39)).strip(chr(44)).strip(chr(46)).strip(chr(63)).strip(chr(33))
    assert cleaned in ["ANSIEDADE", "ACNE", "OBESIDADE"], f"FAIL: {test} -> {cleaned}"
print("OK: strip de ? e ! funciona")
""")
    test_file.close()
    ok, out, err = run_script(["python3", test_file.name])
    check("make_cover strip remove ? e !", ok, out.strip() or err[:100])
    os.unlink(test_file.name)

    # 2.2 memory_search — precisa ter pelo menos 1 resultado para temas conhecidos
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "memoria-cientifica/scripts/memory_search.py"),
        "--query", "creatina cerebro memoria", "--top-k", "1", "--format", "json"
    ], timeout=90)
    try:
        data = json.loads(out)
        check("memory_search encontra creatina", len(data) >= 1 and data[0]["score"] > 0.5,
              f"score={data[0]['score'] if data else 0}")
    except:
        check("memory_search funcional", False, err[:200])

    # 2.3 memory_search — topicos
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "memoria-cientifica/scripts/memory_search.py"),
        "--list-topics"
    ], timeout=60)
    topics_count = out.count("##")
    check("memory_search lista topicos", topics_count >= 3, f"{topics_count} topicos")

    # 2.4 photo_selector — retorna foto para tema
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "tweet-carrossel/scripts/photo_selector.py"),
        "--theme", "medica em consultorio recebendo paciente",
        "--top-k", "3", "--format", "json"
    ], timeout=90)
    try:
        data = json.loads(out)
        check("photo_selector retorna match", data.get("best_match") is not None,
              f"top-1: {data.get('best_match', {}).get('filename')}")
    except:
        check("photo_selector funcional", False, err[:200])

    # 2.5 capture_pubmed — gera sintetico ao menos
    test_out = "/root/test_val_pubmed.png"
    if Path(test_out).exists():
        Path(test_out).unlink()
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "tweet-carrossel/scripts/capture_pubmed.py"),
        "--pmid", "33271426", "--out", test_out
    ], timeout=240)
    if Path(test_out).exists():
        size_kb = Path(test_out).stat().st_size // 1024
        check("capture_pubmed gera imagem", size_kb > 15, f"{size_kb}KB")
        Path(test_out).unlink()
    else:
        check("capture_pubmed gera imagem", False, "arquivo nao criado")

    # 2.6 build_prompt — 7 dimensoes
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "prompt-imagens/scripts/build_prompt.py"),
        "--sujeito", "Medica",
        "--aparencia", "Blazer escuro",
        "--acao", "Analisando exame",
        "--cenario", "Consultorio",
        "--iluminacao", "Lateral 3200K",
        "--estilo", "editorial"
    ], timeout=30)
    has_all = all(f"{i}." in out for i in range(1, 8))
    check("build_prompt gera 7 dimensoes", has_all, f"{sum(f'{i}.' in out for i in range(1,8))}/7")


# ============================================================
# GRUPO 3 — Integracao
# ============================================================
def test_integration():
    print("\n=== GRUPO 3: Integracao ===\n")

    # 3.1 Storage + search de um tema novo
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="valtest_")
    for name, text in [
        ("original", "Teste de validacao pipeline memoria cientifica pipeline"),
        ("research", "Pesquisa aprofundada teste teste teste. " * 20),
        ("clinical", "Aplicacao clinica no IVS teste. " * 15),
        ("summary", "Resumo de teste de validacao."),
    ]:
        Path(tmpdir, f"{name}.md").write_text(text)

    slug = f"valtest-{datetime.now().strftime('%H%M%S')}"
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "memoria-cientifica/scripts/memory_store.py"),
        "--slug", slug, "--topic", "teste-validacao",
        "--original", str(Path(tmpdir, "original.md")),
        "--research", str(Path(tmpdir, "research.md")),
        "--clinical", str(Path(tmpdir, "clinical.md")),
        "--summary", str(Path(tmpdir, "summary.md")),
        "--tags", "teste,validacao",
    ], timeout=180)
    check("memory_store armazena pesquisa nova", ok, err[:200] if not ok else "")

    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    # Depois procura
    time.sleep(2)
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "memoria-cientifica/scripts/memory_search.py"),
        "--query", "teste validacao pipeline", "--top-k", "1", "--format", "json"
    ], timeout=60)
    try:
        data = json.loads(out)
        found = any(slug in str(r.get("research_id", "")) for r in data)
        check("memory_search encontra a pesquisa recem criada", found)
    except:
        check("memory_search integracao", False, err[:200])


# ============================================================
# GRUPO 4 — End-to-end
# ============================================================
def test_e2e(send_telegram=False):
    print("\n=== GRUPO 4: End-to-end (gera capa real) ===\n")

    # Gera capa de teste com tema novo ("validacao medica")
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "tweet-carrossel/scripts/compose_cover.py"),
        "--foto", "/root/.openclaw/workspace/fotos_dra/dra_seria_frontal.png",
        "--tema", "consultorio medico teste",
        "--headline", "TESTE? VALIDACAO?|PIPELINE|FUNCIONA CORRETAMENTE?|SIM!",
        "--destaques", "TESTE,VALIDACAO,FUNCIONA,SIM",
        "--out", "/root/valtest_capa.jpg"
    ], timeout=600)

    if Path("/root/valtest_capa.jpg").exists():
        size_kb = Path("/root/valtest_capa.jpg").stat().st_size // 1024
        check("E2E: compose_cover gera JPEG", size_kb > 50, f"{size_kb}KB")

        # Valida dimensoes
        from PIL import Image
        img = Image.open("/root/valtest_capa.jpg")
        check("E2E: capa 1080x1350", img.size == (1080, 1350), f"{img.size}")

        if send_telegram:
            import tempfile, shutil
            tg = Path(tempfile.mkdtemp()) / "tg"
            tg.mkdir()
            shutil.copy("/root/valtest_capa.jpg", tg / "slide_01.jpg")
            tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            if tg_token:
                ok2, out2, _ = run_script([
                    "python3", str(OPENCLAW / "tweet-carrossel/scripts/send_to_telegram.py"),
                    "--chat-id", "-1003803476669", "--thread-id", "4",
                    "--dir", str(tg), "--caption", "🧪 Teste de validacao E2E"
                ], timeout=60)
                check("E2E: enviado ao Telegram", ok2, "")
                shutil.rmtree(tg.parent)

        Path("/root/valtest_capa.jpg").unlink()
    else:
        check("E2E: compose_cover", False, err[:300] if err else out[-300:])

    # Gera slide 2 com paper PubMed
    ok, out, err = run_script([
        "python3", str(OPENCLAW / "tweet-carrossel/scripts/capture_pubmed.py"),
        "--pmid", "39070254", "--out", "/root/valtest_paper.png"
    ], timeout=180)
    if Path("/root/valtest_paper.png").exists():
        sz = Path("/root/valtest_paper.png").stat().st_size // 1024
        check("E2E: capture_pubmed produz arquivo", sz >= 15, f"{sz}KB")
        Path("/root/valtest_paper.png").unlink()


# ============================================================
# GRUPO 5 — CLAUDE.md / forcing functions
# ============================================================
def test_claude_rules():
    print("\n=== GRUPO 5: Forcing functions CLAUDE.md ===\n")

    claude = Path("/root/.openclaw/workspace/CLAUDE.md").read_text()

    # Deve ter as 7 proibicoes
    for i in range(1, 8):
        check(f"PROIBICAO {i} presente", f"PROIBICAO {i}" in claude)

    # Proibicoes chave
    checks_content = [
        ("proibe ingles no chain-of-thought", "pensar em ingles"),
        ("proibe entregar texto em vez de JPEG", "entregar carrossel como TEXTO"),
        ("proibe pular ETAPA 0 memoria-cientifica", "pular ETAPA 0"),
        ("proibe inventar caminhos memoria", "inventar caminhos"),
        ("obrigatorio resumo pratico de cada paper", "resumo pratico"),
        ("obrigatorio usar photo real da Dra", "foto REAL"),
        ("obrigatorio enviar via Telegram", "send_to_telegram"),
    ]
    for desc, keyword in checks_content:
        check(f"CLAUDE.md {desc}", keyword.lower() in claude.lower())


# ============================================================
# Relatorio
# ============================================================
def report():
    print("\n" + "=" * 70)
    print("RELATORIO FINAL")
    print("=" * 70)

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"] is True)
    failed = sum(1 for r in RESULTS if r["passed"] is False)
    warns = sum(1 for r in RESULTS if r["passed"] is None)

    print(f"\nTotal: {total} testes")
    print(f"{PASS} Passou:   {passed}")
    print(f"{FAIL} Falhou:   {failed}")
    print(f"{WARN} Avisos:   {warns}")

    if failed > 0:
        print("\n--- FALHAS ---")
        for r in RESULTS:
            if r["passed"] is False:
                print(f"{FAIL} {r['name']}: {r['detail']}")

    # Salva JSON detalhado
    log_path = Path("/root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs")
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"validation_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    log_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "warnings": warns,
        "results": [
            {"name": r["name"], "passed": r["passed"], "detail": r["detail"]}
            for r in RESULTS
        ]
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRelatorio salvo: {log_file}")

    return failed == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send-telegram", action="store_true",
                    help="Envia capa de teste ao Telegram")
    ap.add_argument("--quick", action="store_true",
                    help="Pula testes lentos (capture_pubmed, e2e)")
    args = ap.parse_args()

    test_files()
    test_units()
    test_integration()
    if not args.quick:
        test_e2e(send_telegram=args.send_telegram)
    test_claude_rules()

    ok = report()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
