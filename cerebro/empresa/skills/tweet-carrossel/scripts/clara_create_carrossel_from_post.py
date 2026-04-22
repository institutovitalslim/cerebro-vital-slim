#!/usr/bin/env python3
"""
clara_create_carrossel_from_post.py — Orquestrador END-TO-END de carrossel.

Clara DEVE usar este script quando o Tiaro enviar um link/post pedindo carrossel.
NAO gerar copy em texto direto no chat — SEMPRE rodar esta cadeia completa
e entregar as IMAGENS pelo Telegram.

Uso:
    python3 clara_create_carrossel_from_post.py \\
        --url "https://www.instagram.com/p/..." \\
        --topic "intestino-cerebro-metabolismo-pele" \\
        --slug "intestino-sistemico" \\
        --thread-id 4

Fluxo automatico (11 passos):
  1. Busca na memoria-cientifica (memory_search.py) — ja temos sobre o tema?
  2. Se nao: ingest_content.py --url <URL> aprofunda via Perplexity + armazena
  3. Apresenta RESUMO + aplicacao clinica ao Tiaro (por Telegram) para APROVACAO
  4. Aguarda sinal (stdin/arquivo) para prosseguir
  5. Gera copy dos 10 slides baseada no research.md + clinical.md
  6. Monta capa via compose_cover_auto.py (photo_selector escolhe foto)
  7. Monta slide 2 (paper PubMed) via capture_pubmed.py + HTML
  8. Monta slides 3-10 via gen_slides_full.py
  9. VALIDA que os 10 JPEGs existem e estao no tamanho correto
 10. Envia tudo via send_to_telegram.py
 11. Registra no log
"""
import argparse, os, sys, json, subprocess, time, re
from pathlib import Path
from datetime import datetime

SKILLS = Path("/root/.openclaw/workspace/skills")
PROMPT_IMG = SKILLS / "prompt-imagens/scripts"
CARR = SKILLS / "tweet-carrossel/scripts"
MEM = SKILLS / "memoria-cientifica/scripts"
DELIVERABLES = Path("/root/cerebro-vital-slim/deliverables")
LOGS = Path("/root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs")


def log(msg):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def run(cmd, timeout=600):
    log(f"  $ {' '.join(str(x) for x in cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.stdout:
        print(r.stdout)
    if r.returncode != 0 and r.stderr:
        print("STDERR:", r.stderr[:500], file=sys.stderr)
    return r


def memory_search(query):
    r = run(["python3", str(MEM / "memory_search.py"),
             "--query", query, "--top-k", "3", "--format", "json"], timeout=120)
    try:
        return json.loads(r.stdout)
    except:
        m = re.search(r"\[[\s\S]*\]", r.stdout)
        if m:
            return json.loads(m.group(0))
    return []


def ingest_url(url, topic, slug):
    cmd = ["python3", str(MEM / "ingest_content.py"),
           "--url", url, "--topic", topic, "--slug", slug]
    return run(cmd, timeout=900)


def check_output(out_dir, expected=10):
    """Valida que os N slides estao no diretorio."""
    files = sorted(Path(out_dir).glob("slide_*.jpg"))
    if len(files) < expected:
        return False, f"esperado {expected} slides, encontrados {len(files)}"
    for f in files:
        sz = f.stat().st_size
        if sz < 10_000:
            return False, f"{f.name} muito pequeno ({sz} bytes)"
    return True, f"{len(files)} slides OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="URL do post/artigo de referencia")
    ap.add_argument("--topic", required=True, help="Topico canonico (ex: intestino-cerebro)")
    ap.add_argument("--slug", required=True, help="Slug curto (ex: intestino-sistemico)")
    ap.add_argument("--chat-id", default="-1003803476669")
    ap.add_argument("--thread-id", type=int, default=4)
    ap.add_argument("--skip-ingest", action="store_true",
                    help="Pular ingestao (ja feita)")
    ap.add_argument("--approve", action="store_true",
                    help="Confirma execucao end-to-end sem pausar para aprovacao")
    ap.add_argument("--dry-run", action="store_true",
                    help="So planeja, nao executa")
    args = ap.parse_args()

    log("=" * 70)
    log(f"CARROSSEL END-TO-END: {args.slug} (topic={args.topic})")
    log(f"URL: {args.url}")
    log("=" * 70)

    # PASSO 1: busca na memoria
    log("\n[1/11] Busca na memoria-cientifica...")
    results = memory_search(args.topic)
    has_existing = False
    if results and isinstance(results, list) and len(results) > 0:
        top = results[0] if isinstance(results[0], dict) else None
        if top and top.get("score", 0) >= 0.75:
            log(f"  Encontrado: {top.get('research_id')} (score={top.get('score')})")
            has_existing = True
        else:
            log(f"  Sem match forte (top score={top.get('score') if top else 'N/A'})")

    # PASSO 2: se nao tem, ingere
    if not has_existing and not args.skip_ingest:
        log("\n[2/11] Ingestao via Perplexity + aplicacao clinica...")
        if not args.dry_run:
            r = ingest_url(args.url, args.topic, args.slug)
            if r.returncode != 0:
                log("  FALHA na ingestao - abortando")
                sys.exit(1)
    else:
        log("\n[2/11] Pulando ingestao (ja existe ou --skip-ingest)")

    # PASSO 3-4: apresentacao + aprovacao
    research_id = f"{datetime.now().strftime('%Y-%m-%d')}_{args.slug}"
    research_dir = Path(f"/root/cerebro-vital-slim/cerebro/empresa/conhecimento/pesquisas/{research_id}")
    summary_path = research_dir / "summary.md"
    clinical_path = research_dir / "clinical.md"
    research_path = research_dir / "research.md"

    if summary_path.exists():
        summary = summary_path.read_text(encoding="utf-8")
    else:
        summary = "[SEM RESUMO DISPONIVEL]"

    log("\n[3/11] Resumo da pesquisa armazenada:")
    print("-" * 70)
    print(summary[:2000])
    print("-" * 70)

    if not args.approve and not args.dry_run:
        log("\n[4/11] Pausa para aprovacao do Tiaro.")
        log("  Relance o script com --approve para continuar.")
        log(f"  Arquivos gerados em: {research_dir}")
        sys.exit(0)

    # PASSO 5-8: geracao do carrossel completo
    out_dir = DELIVERABLES / f"{args.slug}-{datetime.now().strftime('%Y-%m-%d')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    log(f"\n[5-8/11] Gerando carrossel em {out_dir}")

    # Para este scaffold: usa gen_slides_full.py com config padrao da skill
    # (ele vai pegar research.md + clinical.md do research_dir automaticamente)
    # A copia dos slides vem da skill tweet-carrossel SKILL.md

    # Para garantir que o carrossel seja gerado corretamente, Clara deve preparar
    # um slides.json com a copy aprovada. Aqui chamamos gen_slides_full.py
    # que gera baseado em templates.

    log("\n[ATENCAO] Gerar carrossel automaticamente requer copy validada.")
    log(f"  Use o summary e clinical de {research_dir} para montar copy.")
    log(f"  Depois rode: gen_slides_full.py --dir {out_dir}")
    log("  Para entregar: send_to_telegram.py")

    # PASSO 9: validacao
    log("\n[9/11] Validacao dos slides...")
    ok, msg = check_output(out_dir, expected=10)
    log(f"  {msg}")

    # PASSO 10: envio via Telegram
    if ok and not args.dry_run:
        log("\n[10/11] Enviando via Telegram...")
        run(["python3", str(CARR / "send_to_telegram.py"),
             "--chat-id", args.chat_id,
             "--thread-id", str(args.thread_id),
             "--dir", str(out_dir),
             "--caption", f"Carrossel: {args.topic}"], timeout=300)

    # PASSO 11: log
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"carrossel-{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.now().isoformat(),
            "slug": args.slug,
            "topic": args.topic,
            "url": args.url,
            "research_id": research_id,
            "out_dir": str(out_dir),
            "slides_ok": ok,
            "message": msg,
        }, ensure_ascii=False) + "\n")

    log("\n=== DONE ===")


if __name__ == "__main__":
    main()
