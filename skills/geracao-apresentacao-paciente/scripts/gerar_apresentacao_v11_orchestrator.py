#!/usr/bin/env python3
"""Orchestrator V11 — pipeline em 5 etapas com gates rígidos.

Fluxo:
  Etapa 1: Análise estruturada do questionário (analisar_questionario_llm.py)
           GATE: queixas_principais >= 1 E completude >= 50%
  Etapa 2: Coleta de exames com acurácia total (reusa extrair_exames_llm.py + validador 11 layers)
           GATE: total_exames >= 5 E validados >= 80% do total
  Etapa 3: Interpretação clínica por exame (interpretar_exames_clinico_llm.py)
           GATE: total_exames_interpretados >= 5 E sistemas_fail == 0
  Etapa 4: Cruzamento Q × E (cruzar_q_x_e_llm.py)
           GATE: hipoteses_integradas >= 3
  Etapa 5: Renderização V11 (gerar_apresentacao_v11.py)
           GATE: HTML gerado E tamanho > 100KB

Uso:
  python3 gerar_apresentacao_v11_orchestrator.py <nome_paciente> [--sexo F] [--idade 49]
                                                  [--exames-pdf-dir <path>]
                                                  [--send-telegram]
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, subprocess
from pathlib import Path

BASE_SKILL = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente")
SCRIPTS = BASE_SKILL / "scripts"
AUDIT_BASE = BASE_SKILL / "state/auditoria_v11"
sys.path.insert(0, str(SCRIPTS))


def _slug(s):
    s = re.sub(r"[^\w\-]", "-", s.lower())
    return re.sub(r"-+", "-", s).strip("-")


def _print_gate(etapa, ok, detalhes):
    status = "✓ GATE OK" if ok else "✗ GATE FALHOU"
    print(f"\n[Etapa {etapa}] {status} — {detalhes}\n", file=sys.stderr)


def etapa1_questionario(paciente_meta, audit_dir, questionario_json_path):
    """Roda análise estruturada do questionário."""
    out = audit_dir / "etapa_1_questionario.json"
    cmd = [
        "python3", str(SCRIPTS / "analisar_questionario_llm.py"),
        str(questionario_json_path),
        "--paciente-nome", paciente_meta["nome"],
        "--paciente-sexo", paciente_meta.get("sexo", ""),
        "--paciente-idade", str(paciente_meta.get("idade", 0)),
        "--output", str(out),
    ]
    print(f"[etapa 1] {' '.join(cmd[:4])}...", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        return False, None
    info = json.loads(r.stdout)
    return info.get("gate_ok", False), out


def etapa2_exames(paciente_meta, audit_dir, exames_pdfs):
    """Reusa extrator V10 + validador 11 layers."""
    from gerar_apresentacao import extrair_todos_exames_llm, _flatten_exames_v9
    print(f"[etapa 2] extraindo {len(exames_pdfs)} PDFs via gpt-5.5...", file=sys.stderr)
    exames_parsed = extrair_todos_exames_llm(exames_pdfs, paciente_meta)

    # salva audit V11
    out = audit_dir / "etapa_2_exames.json"
    with open(out, "w") as f:
        json.dump(exames_parsed, f, ensure_ascii=False, indent=2)

    flat = _flatten_exames_v9(exames_parsed)
    total = len(flat)
    validados = sum(1 for ex in flat if ex.get("status") in ("normal", "alterado", "alert", "crit"))
    pct = (validados / total * 100) if total else 0
    gate_ok = total >= 5 and pct >= 80

    _print_gate(2, gate_ok, f"{total} exames extraídos, {validados} validados ({pct:.0f}%)")
    return gate_ok, out, exames_parsed, flat


def etapa3_interpretacao(paciente_meta, audit_dir, exames_path):
    """Interpretação clínica por exame via Sonnet 4.5."""
    out = audit_dir / "etapa_3_interpretacao.json"
    cmd = [
        "python3", str(SCRIPTS / "interpretar_exames_clinico_llm.py"),
        str(exames_path),
        "--paciente-nome", paciente_meta["nome"],
        "--paciente-sexo", paciente_meta.get("sexo", ""),
        "--paciente-idade", str(paciente_meta.get("idade", 0)),
        "--output", str(out),
    ]
    print(f"[etapa 3] interpretando via Sonnet 4.5 (pode levar ~2-4 min)...", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        return False, None
    info = json.loads(r.stdout)
    _print_gate(3, info.get("gate_ok", False),
                f"{info.get('total_exames_interpretados',0)} exames em {len(info.get('sistemas_processados',[]))} sistemas, {info.get('alertas_criticos',0)} alertas críticos")
    return info.get("gate_ok", False), out


def etapa4_cruzamento(paciente_meta, audit_dir, questionario_etapa1, interpretacao_etapa3):
    """Cruzamento Q × E via Sonnet 4.5."""
    out = audit_dir / "etapa_4_cruzamento.json"
    cmd = [
        "python3", str(SCRIPTS / "cruzar_q_x_e_llm.py"),
        str(questionario_etapa1),
        str(interpretacao_etapa3),
        "--output", str(out),
    ]
    print(f"[etapa 4] cruzando questionário x exames via Sonnet 4.5...", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        return False, None
    info = json.loads(r.stdout)
    _print_gate(4, info.get("gate_ok", False),
                f"{info.get('hipoteses_integradas',0)} hipóteses, {info.get('alvos_prioritarios',0)} alvos prioritários")
    return info.get("gate_ok", False), out


def etapa5_render(paciente_meta, audit_dir, questionario_raw, exames_parsed,
                  bioimpedancia, analise_q, interp_e, cruzamento, output_dir):
    """Renderiza V11 (interna + paciente)."""
    from gerar_apresentacao_v11 import render_apresentacao_v11
    print(f"[etapa 5] renderizando V11 (interna + paciente)...", file=sys.stderr)

    # CONTRATO: os renderers iteram uma LISTA de exames. Passar o dict {"grupos": [...]}
    # faz _process_exames iterar as CHAVES e devolver [] — apêndice técnico vazio EM SILÊNCIO.
    from gerar_apresentacao import _flatten_exames_v9  # type: ignore
    exames_para_render = exames_parsed
    if isinstance(exames_parsed, dict):
        exames_para_render = _flatten_exames_v9(exames_parsed)
        if exames_parsed.get("grupos") and not exames_para_render:
            raise RuntimeError("Exames vieram com grupos mas o achatamento resultou vazio — contrato quebrado.")

    out_interna = render_apresentacao_v11(
        paciente=paciente_meta, questionario=questionario_raw, exames=exames_para_render,
        output_dir=output_dir, versao_paciente=False,
        bioimpedancia=bioimpedancia,
        analise_questionario=analise_q, interpretacao_exames=interp_e, cruzamento=cruzamento,
    )
    out_paciente = render_apresentacao_v11(
        paciente=paciente_meta, questionario=questionario_raw, exames=exames_para_render,
        output_dir=output_dir, versao_paciente=True,
        bioimpedancia=bioimpedancia,
        analise_questionario=analise_q, interpretacao_exames=interp_e, cruzamento=cruzamento,
    )
    size_i = Path(out_interna).stat().st_size
    size_p = Path(out_paciente).stat().st_size
    gate_ok = size_i > 100_000 and size_p > 100_000
    _print_gate(5, gate_ok, f"interna {size_i:,}B / paciente {size_p:,}B")
    return gate_ok, out_interna, out_paciente


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nome", help="Nome completo do paciente")
    ap.add_argument("--sexo", default="F", choices=["F", "M"])
    ap.add_argument("--idade", type=int, required=True)
    ap.add_argument("--telefone", default="")
    ap.add_argument("--questionario", required=True, help="Path do JSON do questionário")
    ap.add_argument("--exames-pdfs", default="", help="JSON list de PDFs (formato buscar_exames_drive.py)")
    ap.add_argument("--bioimpedancia", default="", help="JSON da bioimpedância (opcional)")
    ap.add_argument("--output-dir", default="/root/cerebro-vital-slim/deliverables")
    ap.add_argument("--send-telegram", action="store_true")
    ap.add_argument("--skip-gates", action="store_true", help="DEV ONLY: continua mesmo se gate falhar")
    args = ap.parse_args()

    paciente_meta = {
        "nome": args.nome, "sexo": args.sexo, "idade": args.idade,
        "telefone": args.telefone, "data_consulta": time.strftime("%d.%m.%Y"),
    }

    slug = _slug(args.nome)
    ts = time.strftime("%Y%m%d_%H%M%S")
    audit_dir = AUDIT_BASE / f"{slug}_{ts}"
    audit_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[V11 ORCHESTRATOR] paciente={args.nome} audit={audit_dir}\n", file=sys.stderr)

    t0 = time.time()

    # ETAPA 1
    ok, etapa1_out = etapa1_questionario(paciente_meta, audit_dir, args.questionario)
    if not ok and not args.skip_gates:
        print("\n[ABORT] Etapa 1 gate falhou.", file=sys.stderr)
        sys.exit(1)

    # ETAPA 2 — exames
    if args.exames_pdfs:
        exames_pdfs = json.load(open(args.exames_pdfs))
    else:
        print("[etapa 2] --exames-pdfs não fornecido. Pulando extração; usando exames cached se houver.", file=sys.stderr)
        exames_pdfs = []
    if exames_pdfs:
        ok, etapa2_out, exames_parsed, flat = etapa2_exames(paciente_meta, audit_dir, exames_pdfs)
        if not ok and not args.skip_gates:
            print("\n[ABORT] Etapa 2 gate falhou.", file=sys.stderr)
            sys.exit(1)
    else:
        exames_parsed = {"grupos": []}
        flat = []
        etapa2_out = audit_dir / "etapa_2_exames.json"
        etapa2_out.write_text(json.dumps(exames_parsed, ensure_ascii=False, indent=2))

    # ETAPA 3
    if flat:
        ok, etapa3_out = etapa3_interpretacao(paciente_meta, audit_dir, etapa2_out)
        if not ok and not args.skip_gates:
            print("\n[ABORT] Etapa 3 gate falhou.", file=sys.stderr)
            sys.exit(1)
    else:
        print("[etapa 3] sem exames, pulando interpretação", file=sys.stderr)
        etapa3_out = audit_dir / "etapa_3_interpretacao.json"
        etapa3_out.write_text(json.dumps({"sistemas": {}, "alertas_criticos_globais": []}, ensure_ascii=False))

    # ETAPA 4
    if flat:
        ok, etapa4_out = etapa4_cruzamento(paciente_meta, audit_dir, etapa1_out, etapa3_out)
        if not ok and not args.skip_gates:
            print("\n[ABORT] Etapa 4 gate falhou.", file=sys.stderr)
            sys.exit(1)
    else:
        etapa4_out = None

    # ETAPA 5
    analise_q = json.load(open(etapa1_out))
    interp_e = json.load(open(etapa3_out)) if etapa3_out.exists() else None
    cruzamento = json.load(open(etapa4_out)) if etapa4_out and etapa4_out.exists() else None
    bioimp = json.load(open(args.bioimpedancia)) if args.bioimpedancia else None
    questionario_raw = json.load(open(args.questionario))

    ok, out_interna, out_paciente = etapa5_render(
        paciente_meta, audit_dir, questionario_raw, exames_parsed,
        bioimp, analise_q, interp_e, cruzamento, args.output_dir
    )
    if not ok and not args.skip_gates:
        sys.exit(1)

    dt_total = time.time() - t0
    print(f"\n[V11 COMPLETO] {dt_total/60:.1f} min", file=sys.stderr)
    print(json.dumps({
        "paciente": args.nome,
        "audit_dir": str(audit_dir),
        "etapa_1_questionario": str(etapa1_out),
        "etapa_2_exames": str(etapa2_out),
        "etapa_3_interpretacao": str(etapa3_out) if etapa3_out else None,
        "etapa_4_cruzamento": str(etapa4_out) if etapa4_out else None,
        "html_interna": str(out_interna),
        "html_paciente": str(out_paciente),
        "duracao_total_s": round(dt_total, 1),
    }, ensure_ascii=False, indent=2))

    if args.send_telegram:
        try:
            from gerar_apresentacao import enviar_apresentacao_para_topico_pacientes
            enviar_apresentacao_para_topico_pacientes(str(out_interna), paciente_meta, exames_parsed)
            print(f"[telegram] enviado pro tópico Pacientes", file=sys.stderr)
        except Exception as e:
            print(f"[telegram] falhou: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
