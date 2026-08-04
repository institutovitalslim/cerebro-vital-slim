#!/usr/bin/env python3
"""
V10 — Renderer da Apresentação V2 do Programa de Acompanhamento Avançado IVS

Implementação fiel ao briefing do Conselho Growth (padrão conselho.html, 05/05/2026).

Estrutura DOM (na ordem):
  body
    header.topbar
    nav.progress-nav
    main
      section.hero-clinical-document
      section.executive-diagnosis
      section.patient-mirror
      section.critical-levers
      section.spin-guided
      section.ivs-machine
      section.proof-by-process
      section.program-180-days
      section.objection-preemption
      section.decision-checklist
      section.final-cta
      section.technical-appendix

Compliance:
  - Sem "garantido", "cura", "X dias", "reverte com certeza"
  - Disclaimer "Resultados individuais variam..." nos casos reais
  - Linguagem: "pode", "tende", "merece atenção", "minha recomendação"
"""
from __future__ import annotations
import base64
import json
import re
from datetime import date, datetime
from html import escape as _html_escape
from pathlib import Path

ASSETS_DIR = Path("/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/assets")
SITE_IMAGES = ASSETS_DIR / "site-images"
BIBLIOTECA_PATH = ASSETS_DIR / "biblioteca_implicacoes.json"
REFS_PATH = ASSETS_DIR / "refs_canonicas.json"


def safe_html(s):
    if s is None:
        return ""
    return _html_escape(str(s), quote=False)


def img_b64(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    ext = path.suffix.lstrip(".").lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{data}"


def calcular_idade(data_nasc_ms):
    if not data_nasc_ms:
        return None
    try:
        d = datetime.fromtimestamp(int(data_nasc_ms) / 1000)
        today = date.today()
        return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CSS — paleta IVS (creme + dourado), tipografia premium, responsivo, print
# ---------------------------------------------------------------------------
CSS = r"""
:root{
  --gold:#9F8844; --gold2:#D4BC79; --gold-dark:#6B5A2B;
  --cream:#F7F2E4; --paper:#FFFFFF; --elev:#FBF6E8;
  --ink:#1F1A12; --body:#3D3528; --muted:#756A55;
  --line:rgba(107,90,43,.18); --line-strong:rgba(107,90,43,.32);
  --red:#8E2417; --amber:#A06D0A; --green:#155527;
  --serif:Georgia, "Playfair Display", serif;
  --sans:"Inter", -apple-system, "Segoe UI", Roboto, sans-serif;
  --max-w:1240px;
  --s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px; --s-5:24px;
  --s-6:32px; --s-7:48px; --s-8:64px; --s-9:96px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body{
  font-family: var(--sans); font-size: 16px; line-height: 1.62;
  color: var(--body); background: var(--cream);
  text-rendering: optimizeLegibility; font-weight: 400;
}
img { max-width: 100%; height: auto; display: block; }
a { color: var(--gold-dark); text-decoration: none; }

h1, h2, h3, h4 { font-family: var(--serif); color: var(--ink); line-height: 1.15; font-weight: 500; }
h1 { font-size: clamp(36px, 5vw, 64px); letter-spacing: -0.015em; }
h2 { font-size: clamp(28px, 3.6vw, 48px); margin-bottom: var(--s-5); }
h3 { font-size: clamp(20px, 2.2vw, 26px); margin-bottom: var(--s-4); }
h4 { font-family: var(--sans); font-size: 12px; font-weight: 600; text-transform: uppercase;
     letter-spacing: 0.18em; color: var(--gold-dark); margin-bottom: var(--s-3); }
p { font-family: var(--sans); margin-bottom: var(--s-4); }

.wrap { max-width: var(--max-w); margin: 0 auto; padding: 0 var(--s-5); }
.section { padding: var(--s-9) 0; border-top: 1px solid var(--line); }
.section:first-of-type { border-top: none; }

/* === TOPBAR === */
.topbar{
  background:#FFFFFF; padding:var(--s-3) var(--s-5);
  border-bottom:1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max-w); margin:0 auto;
  display:flex; justify-content:space-between; align-items:center;
  min-height:96px; gap: var(--s-5);
}
.topbar .logo{ height:80px; max-width:280px; object-fit:contain; }
.topbar .doctor-tag{
  font-family:var(--sans); font-size:11px; font-weight:500;
  text-transform:uppercase; letter-spacing:0.18em; color:var(--muted);
  text-align:right; line-height:1.5;
}
.topbar .doctor-tag .name{
  display:block; font-family:var(--serif); font-size:16px; font-weight:500;
  font-style:italic; text-transform:none; letter-spacing:0;
  color:var(--ink); margin-bottom:2px;
}

/* === PROGRESS NAV === */
.progress-nav{
  position:sticky; top:0; z-index:50;
  background:rgba(247,242,228,0.95); backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line);
}
.progress-nav-inner{
  max-width:var(--max-w); margin:0 auto;
  padding:var(--s-3) var(--s-5);
  display:flex; gap:var(--s-2); flex-wrap:wrap; align-items:center;
  font-size:11px; letter-spacing:0.10em; text-transform:uppercase; font-weight:600;
}
.progress-step{
  display:inline-flex; align-items:center;
  color:var(--muted); padding:6px 12px; border-radius:999px;
  cursor:pointer; transition:all 0.2s; border:1px solid transparent;
}

.progress-step, .mode-btn{ text-decoration:none; }

.progress-step:focus-visible, .mode-btn:focus-visible{
  outline:2px solid var(--gold-dark); outline-offset:2px;
}
.progress-step.active{ background:var(--gold); color:#fff; border-color:var(--gold); }
.progress-step:hover{ color:var(--ink); }
.progress-toggle{
  margin-left:auto; padding:6px 14px; border-radius:999px;
  border:1px solid var(--gold); color:var(--gold-dark); background:transparent;
  font-size:11px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
  cursor:pointer; font-family:var(--sans);
}
.progress-toggle:hover{ background:var(--gold); color:#fff; }
.progress-toggle.active{ background:var(--gold-dark); color:#fff; border-color:var(--gold-dark); }

/* === HERO CLINICAL DOCUMENT === */
.hero-clinical-document{
  padding:var(--s-9) 0 var(--s-8);
  background:linear-gradient(180deg, var(--paper) 0%, var(--cream) 100%);
}
.hero-meta-bar{
  display:flex; gap:var(--s-6); flex-wrap:wrap;
  padding-bottom:var(--s-5); margin-bottom:var(--s-6);
  border-bottom:1px solid var(--line);
}
.hero-meta-item{ font-size:13px; color:var(--muted); }
.hero-meta-item strong{
  display:block; color:var(--ink); font-family:var(--serif);
  font-size:18px; font-weight:500; font-style:italic; margin-top:2px;
}
.hero-clinical-h1{ max-width:920px; margin-bottom:var(--s-5); }
.hero-clinical-lead{
  font-size:clamp(17px, 1.5vw, 20px); color:var(--ink);
  max-width:780px; line-height:1.55; font-weight:400;
}
.hero-clinical-lead strong{ color:var(--gold-dark); font-weight:600; }

/* === EXECUTIVE DIAGNOSIS === */
.executive-diagnosis{ background:var(--paper); }
.diag-grid{ display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--s-5); margin-top:var(--s-6); }
.diag-card{
  background:var(--cream); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-6); border-top:3px solid var(--gold);
}
.diag-card h4{ color:var(--gold-dark); margin-bottom:var(--s-3); }
.diag-card .body-text{ font-size:15px; line-height:1.6; color:var(--body); margin:0; }
.diag-recomendacao{
  background:#1F1A12; color:#F7F2E4; border-radius:14px;
  padding:var(--s-6) var(--s-7); margin-top:var(--s-6);
  font-family:var(--serif); font-size:clamp(18px, 1.8vw, 22px);
  font-style:italic; line-height:1.5;
}
.diag-recomendacao strong{ color:var(--gold2); font-style:normal; }

/* === PATIENT MIRROR === */
.patient-mirror{ background:var(--cream); }
.mirror-grid{ display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--s-4); margin-top:var(--s-5); }
.mirror-card{
  background:var(--paper); border:1px solid var(--line); border-radius:12px;
  padding:var(--s-5);
}
.mirror-card .label{
  font-size:11px; font-weight:600; text-transform:uppercase;
  letter-spacing:0.16em; color:var(--gold-dark); margin-bottom:var(--s-3);
}
.mirror-card .value{
  font-family:var(--serif); font-size:20px; font-weight:500;
  color:var(--ink); line-height:1.3;
}
.mirror-card .value.empty{
  font-family:var(--sans); font-size:13px; font-style:italic;
  color:var(--muted); font-weight:400;
}
.mirror-card .sub{ font-size:13px; color:var(--muted); margin-top:var(--s-2); }
.mirror-card.feature{ grid-column:span 3; border-left:4px solid var(--gold); }
/* === Bioimpedância === */
.bioimped-section{ background: var(--cream); padding-top: var(--s-7); padding-bottom: var(--s-7); }
.bioimped-meta{ font-size:13px;color:var(--muted);margin-bottom:var(--s-5); }
.bio-grid{ display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s-4); }
.bio-card{
  background:var(--paper);border:1px solid var(--line);border-radius:14px;
  padding:var(--s-5);
}
.bio-card h4{
  margin:0 0 var(--s-3);font-size:14px;font-weight:600;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:0.06em;
}
.bio-card .kpis{ display:grid;gap:var(--s-2); }
.bio-kpi{ display:flex;justify-content:space-between;align-items:baseline;padding:6px 0;border-bottom:1px dashed var(--line); }
.bio-kpi:last-child{ border-bottom:none; }
.bio-kpi .label{ font-size:13px;color:var(--ink-soft); }
.bio-kpi .value{ font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink); }
.bio-kpi .value .unit{ font-size:11px;color:var(--muted);font-weight:400;margin-left:3px; }
.bio-kpi .value .delta{ font-size:11px;color:var(--muted);margin-left:6px; }
.bio-kpi .value .delta.up{ color:#2D8A3F; }
.bio-kpi .value .delta.down{ color:#BE3226; }
.bio-highlight{
  background:linear-gradient(135deg, rgba(193,154,69,0.08), rgba(193,154,69,0.02));
  border:1px solid rgba(193,154,69,0.2);
  border-radius:14px;padding:var(--s-5);margin-top:var(--s-5);
}
.bio-highlight h4{
  margin:0 0 var(--s-3);font-size:13px;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:0.1em;font-weight:600;
}
.bio-highlight ul{ margin:0;padding-left:var(--s-4);list-style:none; }
.bio-highlight li{
  position:relative;padding:6px 0 6px 22px;font-size:14px;color:var(--ink);line-height:1.55;
}
.bio-highlight li::before{
  content:"";position:absolute;left:6px;top:14px;width:7px;height:7px;border-radius:50%;
  background:var(--gold);
}
.bio-highlight li.alert::before{ background:#D4A000; }
.bio-highlight li.crit::before{ background:#BE3226; }
.bio-highlight li.ok::before{ background:#2D8A3F; }
.bio-highlight li b{ color:var(--ink); font-weight:600; }
.bio-image-wrap{
  margin-top:var(--s-5);background:var(--paper);border:1px solid var(--line);
  border-radius:14px;padding:var(--s-4);text-align:center;
}
.bio-image-wrap h4{
  margin:0 0 var(--s-3);font-size:13px;font-weight:600;color:var(--gold-dark);
  text-transform:uppercase;letter-spacing:0.1em;
}
.bio-image-wrap img{
  max-width:100%;height:auto;border-radius:10px;
  box-shadow:0 4px 18px rgba(0,0,0,0.06);
  border:1px solid var(--line);
}
.bio-image-wrap .caption{
  display:block;margin-top:var(--s-2);font-size:12px;color:var(--muted);
}
@media (max-width: 900px){ .bio-grid{ grid-template-columns:1fr; } }


/* === CRITICAL LEVERS === */
.critical-levers{ background:var(--paper); }
.lever-list{ display:flex; flex-direction:column; gap:var(--s-5); margin-top:var(--s-6); }
.lever-card{
  background:var(--cream); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-6); display:grid; grid-template-columns:1fr 2fr; gap:var(--s-6);
}
.lever-card[data-sev="crit"]{ border-left:4px solid #BE3226; }
.lever-card[data-sev="alert"],
.lever-card[data-sev="low"],
.lever-card[data-sev="attn"]{ border-left:4px solid #D4A000; }
.lever-card[data-sev="ok"],
.lever-card[data-sev="normal"]{ border-left:4px solid #2D8A3F; }
.lever-numeric .name{
  font-family:var(--serif); font-size:22px; font-weight:500;
  color:var(--ink); margin-bottom:var(--s-3);
}
.lever-numeric .value{
  font-family:var(--serif); font-size:42px; font-weight:600;
  color:var(--ink); line-height:1; margin-bottom:var(--s-2);
}
.lever-numeric .value .unit{
  font-size:0.45em; color:var(--muted); margin-left:6px; font-weight:400;
}
.lever-numeric .ref{ font-size:13px; color:var(--muted); margin-bottom:var(--s-3); }
.lever-numeric .badge{
  display:inline-block; padding:4px 10px; border-radius:6px;
  font-size:11px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
}
.lever-card[data-sev="crit"] .badge{ background:rgba(190,50,38,0.12); color:#8E2417; }
.lever-card[data-sev="alert"] .badge,
.lever-card[data-sev="low"] .badge,
.lever-card[data-sev="attn"] .badge{ background:rgba(212,160,0,0.16); color:#806100; }
.lever-card[data-sev="ok"] .badge,
.lever-card[data-sev="normal"] .badge{ background:rgba(40,130,60,0.10); color:#1F6E2D; }
.lever-narrative h4{ color:var(--gold-dark); margin-bottom:var(--s-2); }
.lever-narrative .interp{
  font-size:15px; line-height:1.55; color:var(--body); margin-bottom:var(--s-3);
}
.lever-narrative .impact{
  font-size:14px; color:var(--muted); margin-bottom:var(--s-4);
  padding:var(--s-3) var(--s-4); background:var(--paper); border-radius:8px;
  border-left:2px solid var(--line);
}
.lever-narrative .spin-q{
  font-family:var(--serif); font-size:16px; font-style:italic;
  color:var(--ink); padding-left:var(--s-4); border-left:3px solid var(--gold);
  line-height:1.5;
}
.lever-narrative .spin-q::before{ content:"Pergunta: "; color:var(--gold-dark); font-style:normal; font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:0.14em; display:block; margin-bottom:var(--s-2); }
.lever-narrative.compact-decision .impact{ margin-bottom:10px; padding:12px 14px; }
.lever-narrative.compact-decision .spin-q{ font-style:normal; font-weight:600; background:rgba(184,140,50,0.10); padding:12px 14px; border-left:3px solid var(--gold); border-radius:8px; }
.lever-narrative.compact-decision .spin-q::before{ content:""; display:none; }

/* === SPIN GUIDED === */
.spin-guided{ background:var(--cream); }
.spin-step-block{
  background:var(--paper); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-6) var(--s-7); margin-bottom:var(--s-5);
}
.spin-step-block .step-tag{
  display:inline-block; font-size:11px; font-weight:700; letter-spacing:0.20em;
  text-transform:uppercase; color:var(--gold); margin-bottom:var(--s-3);
}
.spin-step-block h3{ margin-bottom:var(--s-4); }
.spin-step-block .body-text{ font-size:15px; line-height:1.6; color:var(--body); margin-bottom:var(--s-4); }
.spin-step-block .confirmation{
  background:var(--cream); padding:var(--s-4) var(--s-5);
  border-left:3px solid var(--gold); border-radius:0 8px 8px 0;
  font-family:var(--serif); font-style:italic; font-size:16px; color:var(--ink);
  margin-top:var(--s-4);
}
.spin-step-block .confirmation::before{
  content:"Pergunta de confirmação:"; display:block;
  font-family:var(--sans); font-style:normal; font-weight:600;
  font-size:11px; letter-spacing:0.18em; text-transform:uppercase;
  color:var(--gold-dark); margin-bottom:var(--s-2);
}
.spin-table{ width:100%; border-collapse:collapse; margin:var(--s-4) 0; font-size:14px; }
.spin-table th, .spin-table td{
  padding:var(--s-3) var(--s-4); text-align:left; vertical-align:top;
  border-bottom:1px solid var(--line);
}
.spin-table th{
  background:var(--cream); font-size:11px; font-weight:700;
  letter-spacing:0.14em; text-transform:uppercase; color:var(--gold-dark);
}
.spin-table tr:last-child td{ border-bottom:none; }

/* === IVS MACHINE === */
.ivs-machine{ background:var(--paper); }
.machine-flow{
  display:grid; grid-template-columns:repeat(6, 1fr); gap:var(--s-3);
  margin-top:var(--s-7); position:relative;
}
.machine-step{
  background:var(--cream); border:1px solid var(--line); border-radius:12px;
  padding:var(--s-5) var(--s-4); text-align:center; position:relative;
}
.machine-step .num{
  width:36px; height:36px; border-radius:50%;
  background:var(--gold); color:#fff; display:flex;
  align-items:center; justify-content:center; font-weight:700;
  font-size:14px; margin:0 auto var(--s-3);
}
.machine-step .title{
  font-family:var(--serif); font-size:15px; font-weight:500;
  color:var(--ink); margin-bottom:var(--s-2); line-height:1.25;
}
.machine-step .desc{ font-size:12px; color:var(--muted); line-height:1.5; }

/* === PROOF BY PROCESS === */
.proof-by-process{ background:var(--cream); }
.proof-list{ display:flex; flex-direction:column; gap:var(--s-7); margin-top:var(--s-6); }
.proof-card{
  display:grid; grid-template-columns:1.2fr 1fr; gap:var(--s-7);
  background:var(--paper); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-6); align-items:center;
}
.proof-card:nth-child(even){ grid-template-columns:1fr 1.2fr; }
.proof-card:nth-child(even) .proof-imgs{ order:2; }
.proof-imgs{
  display:grid; grid-template-columns:1fr 1fr; gap:var(--s-3);
}
.proof-img{ position:relative; aspect-ratio:3/4; overflow:hidden; border-radius:10px; background:var(--cream); }
.proof-img img{ width:100%; height:100%; object-fit:cover; object-position:center top; }
.proof-img .label{
  position:absolute; top:var(--s-3); left:var(--s-3);
  background:rgba(255,255,255,0.95); padding:4px 10px; border-radius:4px;
  font-size:10px; font-weight:700; letter-spacing:0.16em;
  text-transform:uppercase; color:var(--ink);
}
.proof-text .step-eyebrow{
  font-size:11px; font-weight:600; text-transform:uppercase;
  letter-spacing:0.20em; color:var(--gold-dark); margin-bottom:var(--s-3);
  display:block;
}
.proof-text h3{ margin-bottom:var(--s-4); }
.proof-text blockquote{
  font-family:var(--serif); font-size:17px; font-style:italic;
  line-height:1.55; color:var(--body); margin:0 0 var(--s-5);
  padding-left:var(--s-4); border-left:2px solid var(--gold);
}
.proof-disclaimer{
  margin-top:var(--s-7); padding:var(--s-4) var(--s-5);
  background:var(--paper); border:1px solid var(--line); border-radius:8px;
  font-size:12px; color:var(--muted); font-style:italic; line-height:1.5;
}

/* === PROGRAM 180 DAYS === */
.program-180-days{ background:var(--paper); }
.program-timeline{
  display:flex; flex-direction:column; gap:var(--s-5); margin-top:var(--s-6);
}
.program-phase{
  display:grid; grid-template-columns:120px 1fr; gap:var(--s-6);
  padding:var(--s-5) 0; border-bottom:1px solid var(--line); align-items:start;
}
.program-phase:last-child{ border-bottom:none; }
.program-phase .phase-marker{
  width:120px; padding:var(--s-3) 0; text-align:center;
  background:var(--cream); border:1px solid var(--line); border-radius:10px;
}
.program-phase .phase-marker .num{
  font-family:var(--serif); font-size:24px; font-weight:600; color:var(--gold-dark);
  font-style:italic; line-height:1;
}
.program-phase .phase-marker .label{
  font-size:10px; font-weight:600; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--muted); margin-top:4px;
}
.program-phase .phase-content h4{ font-family:var(--serif); font-size:20px; font-weight:500; color:var(--ink); margin-bottom:var(--s-3); text-transform:none; letter-spacing:-0.01em; }
.program-phase .phase-content .desc{ font-size:14px; line-height:1.6; color:var(--body); margin-bottom:var(--s-3); }
.program-phase .phase-content ul{ list-style:none; padding:0; }
.program-phase .phase-content li{
  font-size:13px; color:var(--muted); padding:4px 0 4px var(--s-4);
  position:relative; line-height:1.5;
}
.program-phase .phase-content li::before{
  content:""; position:absolute; left:0; top:13px;
  width:6px; height:6px; border-radius:50%; background:var(--gold);
}

/* === OBJECTION PREEMPTION === */
.objection-preemption{ background:var(--cream); }
.obj-grid{ display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--s-4); margin-top:var(--s-6); }
.obj-card{
  background:var(--paper); border:1px solid var(--line); border-radius:12px;
  padding:var(--s-5); border-top:3px solid var(--gold-dark);
}
.obj-card .obj-q{
  font-family:var(--serif); font-size:17px; font-weight:500; font-style:italic;
  color:var(--ink); margin-bottom:var(--s-4); line-height:1.35;
}
.obj-card .obj-a{ font-size:13px; line-height:1.6; color:var(--body); }

/* === DECISION CHECKLIST === */
.decision-checklist{ background:var(--paper); }
.checklist-card{
  max-width:780px; margin:var(--s-6) auto 0;
  background:var(--cream); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-7);
}
.checklist-item{
  display:flex; align-items:flex-start; gap:var(--s-4);
  padding:var(--s-4) 0; border-bottom:1px solid var(--line); cursor:pointer;
}
.checklist-item:last-child{ border-bottom:none; }
.checklist-item .check{
  flex:0 0 28px; width:28px; height:28px; border-radius:6px;
  border:1.5px solid var(--gold); background:#fff;
  display:flex; align-items:center; justify-content:center;
  margin-top:2px; transition:all 0.2s;
}
.checklist-item.checked .check{ background:var(--gold); }
.checklist-item.checked .check::after{
  content:""; width:8px; height:14px; border:solid #fff;
  border-width:0 2px 2px 0; transform:rotate(45deg) translate(-1px, -1px);
}
.checklist-item .text{ font-size:15px; line-height:1.5; color:var(--ink); flex:1; padding-top:2px; }
.checklist-item.checked .text{ color:var(--muted); }

/* === FINAL CTA === */
.final-cta{ background:var(--cream); }
.cta-decision{ display:grid; grid-template-columns:1fr; gap:var(--s-5); margin-top:var(--s-6); max-width:640px; margin-left:auto; margin-right:auto; }
.cta-card{
  background:var(--paper); border:1px solid var(--line); border-radius:14px;
  padding:var(--s-7); display:flex; flex-direction:column; gap:var(--s-4);
}
.cta-card.recommended{ border-top:4px solid var(--gold); background:#FFFCF3; }
.cta-card.alternative{ opacity:0.85; }
.cta-card .label{
  font-size:11px; font-weight:700; letter-spacing:0.20em;
  text-transform:uppercase;
}
.cta-card.recommended .label{ color:var(--gold-dark); }
.cta-card.alternative .label{ color:var(--muted); }
.cta-card h3{ margin-bottom:var(--s-3); }
.cta-card .desc{ font-size:14px; line-height:1.6; color:var(--body); flex:1; }
.cta-card .button{
  display:inline-block; padding:var(--s-4) var(--s-6);
  border-radius:8px; font-size:13px; font-weight:700;
  letter-spacing:0.16em; text-transform:uppercase; cursor:pointer;
  font-family:var(--sans); border:none; text-decoration:none; text-align:center;
  margin-top:var(--s-3);
}
.cta-card.recommended .button{ background:var(--gold-dark); color:#fff; }
.cta-card.alternative .button{ background:transparent; color:var(--muted); border:1px solid var(--line-strong); }

.cta-signature{
  text-align:center; margin-top:var(--s-8); padding-top:var(--s-6);
  border-top:1px solid var(--line);
}
.cta-signature .name{
  font-family:var(--serif); font-size:22px; font-weight:500;
  font-style:italic; color:var(--ink); margin-bottom:var(--s-2);
}
.cta-signature .meta{
  font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted);
}

/* === TECHNICAL APPENDIX === */
.technical-appendix{ background:var(--paper); }
.appendix-controls{
  display:flex; justify-content:space-between; align-items:center;
  flex-wrap:wrap; gap:var(--s-3); margin-bottom:var(--s-5);
}
.appendix-controls .lead{ font-size:14px; color:var(--muted); margin:0; max-width:680px; }
.appendix-toggle-all{
  padding:8px 16px; border-radius:8px; border:1px solid var(--gold);
  background:transparent; color:var(--gold-dark); font-size:11px;
  font-weight:700; letter-spacing:0.16em; text-transform:uppercase;
  cursor:pointer; font-family:var(--sans);
}
.appendix-toggle-all:hover{ background:var(--gold); color:#fff; }

.exam-group{
  border:1px solid var(--line);
  border-radius:10px;
  margin-bottom:var(--s-3);
  overflow:hidden;
  background:var(--paper);
}
.exam-group-header{
  padding:var(--s-4) var(--s-5);
  cursor:pointer;
  display:flex;
  justify-content:space-between;
  align-items:center;
  background:var(--paper);
  user-select:none;
  border-bottom:1px solid var(--line);
}
.exam-group-header h4{
  font-family:var(--serif); font-size:18px; font-weight:500;
  color:var(--ink); text-transform:none; letter-spacing:-0.005em; margin:0;
}
.exam-group-header .meta{
  display:flex; gap:var(--s-3); align-items:center; font-size:12px; color:var(--muted);
}
.exam-group-header .toggle{
  width:24px; height:24px; display:flex; align-items:center; justify-content:center;
  transition:transform 0.2s;
}
.exam-group.open .exam-group-header .toggle{ transform:rotate(180deg); }
.exam-group-body{ display:none; padding:0 var(--s-5); background:var(--paper); }
.exam-group.open .exam-group-body{ display:block; }
.exam-row{
  display:block;
  padding:12px 0;
  margin:0;
  border-bottom:1px solid var(--line);
  font-size:14px;
  background:transparent;
  box-shadow:none;
}
.exam-row:last-child{ border-bottom:none; }
.exam-row .e-nome{
  display:block;
  font-family:var(--serif); font-weight:500; font-size:16px; color:var(--ink);
  line-height:1.35;
}
.exam-row .e-valor{
  display:block;
  margin-top:4px;
  font-family:var(--serif); font-weight:600; font-size:18px; color:var(--ink);
  line-height:1.2;
}
.exam-row .e-valor .e-unit{ color:var(--muted); font-size:13px; margin-left:4px; font-weight:400; }
.exam-row .e-ref{ display:block; margin-top:3px; font-size:12px; color:var(--muted); }
.exam-row .e-status{
  display:block;
  margin-top:6px;
  font-size:10px; font-weight:700; letter-spacing:0.14em;
  text-transform:uppercase; text-align:left;
}
/* === Coloração semântica das linhas de exame — layout técnico simples === */
.exam-row{ transition:none; }
.exam-row[data-sev="crit"] .e-nome,
.exam-row[data-sev="crit"] .e-valor,
.exam-row[data-sev="crit"] .e-status{ color: #8E2417; }
.exam-row[data-sev="alert"] .e-nome,
.exam-row[data-sev="low"] .e-nome,
.exam-row[data-sev="attn"] .e-nome,
.exam-row[data-sev="alert"] .e-valor,
.exam-row[data-sev="low"] .e-valor,
.exam-row[data-sev="attn"] .e-valor,
.exam-row[data-sev="alert"] .e-status,
.exam-row[data-sev="low"] .e-status,
.exam-row[data-sev="attn"] .e-status{ color: #8B6A00; }
.exam-row[data-sev="ok"] .e-status,
.exam-row[data-sev="normal"] .e-status{ color: #1F6E2D; font-weight: 700; }

/* === Mobile === */
@media(max-width: 900px){
  .diag-grid, .mirror-grid, .machine-flow, .obj-grid, .cta-decision { grid-template-columns: 1fr; }
  .lever-card, .proof-card, .proof-card:nth-child(even), .program-phase{ grid-template-columns: 1fr; }
  .proof-card:nth-child(even) .proof-imgs{ order:0; }
  .machine-flow{ grid-template-columns: repeat(2, 1fr); }
  .progress-nav-inner{ overflow-x:auto; flex-wrap:nowrap; }
  .topbar .doctor-tag{ display:none; }
  .topbar .logo{ height:60px; max-width:200px; }
  .hero-meta-bar{ flex-direction:column; gap:var(--s-3); }
  .program-phase .phase-marker{ width:auto; padding:var(--s-3) var(--s-4); }
  .program-phase{ gap:var(--s-3); }
  .exam-row{
    padding:10px 0;
  }
  .exam-row .e-status{ text-align:left; }
  .lever-card{ gap:var(--s-3); }
  .lever-numeric{ display:flex; align-items:baseline; gap:var(--s-3); flex-wrap:wrap; }
}

/* === Print === */
@media print{
  .progress-nav, .progress-toggle, .appendix-toggle-all{ display:none !important; }
  body{ background:#fff; color:#000; font-size:12pt; }
  .section{ padding:24pt 0; page-break-inside:avoid; border-top-color:#ccc; }
  h1{ font-size:24pt; }
  h2{ font-size:18pt; }
  h3{ font-size:14pt; }
  .exam-group, .exam-group-body{ display:block !important; }
  .exam-group-header .toggle{ display:none; }
  .lever-card, .diag-card, .obj-card, .mirror-card, .cta-card{
    page-break-inside:avoid; box-shadow:none;
  }
  .proof-disclaimer, .checklist-card{ page-break-inside:avoid; }
}

/* CSS dos 3 modos é gerenciado abaixo (V2.5) */








/* ========================================================================
   V2.5 — 3 modos de visualização (exclusivos)
   ======================================================================== */

/* Mode switcher (substitui progress-toggle) */
.mode-switcher{
  display: inline-flex; gap: 4px; padding: 4px;
  border: 1px solid var(--line); border-radius: 999px;
  background: rgba(255,255,255,0.85);
  margin-left: auto;
}
.mode-btn{
  padding: 6px 14px; border-radius: 999px;
  border: none; background: transparent;
  font-family: var(--sans); font-size: 11px;
  font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--muted); cursor: pointer;
  transition: all 0.2s;
}
.mode-btn:hover{ color: var(--ink); }
.mode-btn.active{ background: var(--gold-dark); color: #fff; box-shadow: 0 2px 6px rgba(107,90,43,0.20); }

/* === MODO APRESENTAÇÃO === (default) */
/* Mostra fluxo principal, esconde apêndices */
body.js-enabled.modo-apresentacao .technical-appendix,
body.js-enabled.modo-apresentacao .medical-mode,
body.js-enabled.modo-apresentacao .doctor-objections{
  display: none !important;
}

/* === MODO EXAMES === */
/* Mostra apenas o painel técnico de exames */
body.js-enabled.modo-exames main > section:not(.technical-appendix){
  display: none !important;
}
body.js-enabled.modo-exames .technical-appendix{ padding-top: var(--s-7); }

/* === MODO OBJEÇÕES === */
/* Mostra apenas o painel de objeções da médica */
body.js-enabled.modo-objecoes main > section:not(#doctor-objections):not(.medical-mode){
  display: none !important;
}
body.js-enabled.modo-objecoes .doctor-objections{ padding-top: var(--s-7); }

@media print{
  .mode-switcher{ display: none !important; }
}

/* ========================================================================
   V2.5 — Painel de objeções otimizado para consulta rápida
   ======================================================================== */

/* Barra de busca + categorias no topo do painel */
.obj-toolbar{
  position: sticky; top: 76px; z-index: 5;
  background: rgba(247,242,228,0.95); backdrop-filter: blur(10px);
  padding: var(--s-4) 0; margin-bottom: var(--s-5);
  border-bottom: 1px solid var(--line);
}
.obj-search-wrap{ position: relative; max-width: 920px; margin: 0 auto; }
.obj-search{
  width: 100%; padding: var(--s-4) var(--s-5) var(--s-4) 48px;
  border: 1px solid var(--line); border-radius: 12px;
  background: var(--paper);
  font-family: var(--sans); font-size: 16px;
  color: var(--ink); outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.obj-search:focus{
  border-color: var(--gold);
  box-shadow: 0 0 0 4px rgba(159,136,68,0.15);
}
.obj-search::placeholder{ color: var(--muted); }
.obj-search-icon{
  position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
  width: 20px; height: 20px; color: var(--muted); pointer-events: none;
}
.obj-search-clear{
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  width: 28px; height: 28px; border-radius: 50%;
  border: none; background: var(--cream); color: var(--muted);
  cursor: pointer; display: none; align-items: center; justify-content: center;
  font-size: 16px; line-height: 1;
}
.obj-search-clear.visible{ display: flex; }
.obj-search-clear:hover{ background: var(--gold); color: #fff; }

.obj-cats{
  display: flex; gap: 6px; flex-wrap: wrap; max-width: 920px; margin: var(--s-3) auto 0;
}
.obj-cat-chip{
  padding: 5px 12px; border-radius: 999px;
  border: 1px solid var(--line); background: var(--paper);
  font-family: var(--sans); font-size: 11px; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase; color: var(--muted);
  cursor: pointer; transition: all 0.2s;
}
.obj-cat-chip:hover{ border-color: var(--gold); color: var(--ink); }
.obj-cat-chip.active{
  background: var(--gold-dark); color: #fff; border-color: var(--gold-dark);
}

.obj-counter{
  max-width: 920px; margin: var(--s-3) auto 0;
  font-size: 12px; color: var(--muted);
  font-weight: 600; letter-spacing: 0.10em; text-transform: uppercase;
}

/* Lista de objeções — 1 coluna max-width 920px */
.doctor-obj-list{
  max-width: 920px; margin: 0 auto;
  display: flex; flex-direction: column; gap: var(--s-3);
}

/* Card collapsable */
.doctor-obj-card{
  background: var(--paper); border: 1px solid var(--line);
  border-left: 3px solid var(--gold);
  border-radius: 10px;
  padding: 0;
  transition: box-shadow 0.25s, border-color 0.25s;
  overflow: hidden;
}
.doctor-obj-card.hidden{ display: none; }
.doctor-obj-card:hover{
  border-color: var(--gold);
  box-shadow: 0 8px 18px -10px rgba(54,43,24,0.12);
}
.doctor-obj-card .obj-header{
  display: flex; align-items: center; gap: var(--s-3);
  padding: var(--s-4) var(--s-5); cursor: pointer;
  user-select: none;
}
.doctor-obj-card .obj-cat-tag{
  flex-shrink: 0;
  padding: 3px 9px; border-radius: 4px;
  font-family: var(--sans); font-size: 9px; font-weight: 700;
  letter-spacing: 0.16em; text-transform: uppercase;
  background: rgba(159,136,68,0.10); color: var(--gold-dark);
}
.doctor-obj-card .obj-header h3{
  flex: 1; font-family: var(--serif); font-size: 17px;
  font-weight: 500; font-style: italic; color: var(--ink);
  margin: 0; line-height: 1.4;
}
.doctor-obj-card .obj-toggle{
  flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%;
  background: rgba(159,136,68,0.10); color: var(--gold-dark);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; transition: transform 0.25s;
}
.doctor-obj-card.open .obj-toggle{ transform: rotate(180deg); }
.doctor-obj-card .obj-body{
  display: none; padding: 0 var(--s-5) var(--s-5);
  border-top: 1px dashed var(--line);
  margin-top: 0;
}
.doctor-obj-card.open .obj-body{ display: block; padding-top: var(--s-4); }
.doctor-obj-card .obj-body p{
  font-size: 14px; line-height: 1.55; color: var(--body); margin-bottom: var(--s-3);
}
.doctor-obj-card .obj-body p:last-child{ margin-bottom: 0; }
.doctor-obj-card .obj-body p strong{
  color: var(--gold-dark); font-weight: 700;
  font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase;
  display: block; margin-bottom: 4px;
}
.doctor-obj-card .obj-body .cond{
  border-top: 1px dashed var(--line);
  padding-top: var(--s-3); margin-top: var(--s-3);
  font-style: italic; color: var(--ink);
}
.doctor-obj-card .obj-body .cond strong{ color: var(--gold-dark); font-style: normal; }

/* Estado: nenhum resultado */
.obj-empty{
  text-align: center; padding: var(--s-8) 0;
  color: var(--muted); font-style: italic;
}

/* Atalho de teclado hint */
.obj-shortcut{
  position: absolute; right: 52px; top: 50%; transform: translateY(-50%);
  font-size: 10px; color: var(--muted); font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase;
  background: var(--cream); padding: 2px 8px; border-radius: 4px;
  border: 1px solid var(--line);
  pointer-events: none;
}
.obj-search:focus + .obj-shortcut{ display: none; }

@media(max-width: 720px){
  .obj-toolbar{ top: 60px; }
  .obj-cats{ overflow-x: auto; flex-wrap: nowrap; padding-bottom: 2px; }
  .obj-cat-chip{ flex-shrink: 0; }
  .doctor-obj-card .obj-cat-tag{ display: none; }
  .doctor-obj-card .obj-header h3{ font-size: 15px; }
  .obj-shortcut{ display: none; }
}


/* V2.6 — Inclusos com 8 cards e ícones premium maiores */
.inclusos-grid{ grid-template-columns: repeat(4, 1fr) !important; gap: var(--s-4); }
.incluso-card{ padding: var(--s-5) var(--s-4); }
.incluso-card .incluso-icon{
  width: 40px; height: 40px;
  margin-bottom: var(--s-4);
  color: var(--gold-dark);
  background: linear-gradient(135deg, rgba(159,136,68,0.12) 0%, rgba(212,188,121,0.08) 100%);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  padding: 6px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.incluso-card:hover .incluso-icon{
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
  color: #fff;
  transform: scale(1.05);
}
.incluso-card .incluso-titulo{
  font-size: 15px;
  line-height: 1.3;
  margin-bottom: var(--s-3);
}
.incluso-card .incluso-desc{
  font-size: 12.5px;
  line-height: 1.55;
}
@media(max-width: 1100px){
  .inclusos-grid{ grid-template-columns: repeat(2, 1fr) !important; }
}
@media(max-width: 600px){
  .inclusos-grid{ grid-template-columns: 1fr !important; }
}

/* V2.4 — Apêndice da médica (legacy, sobrescrito por V2.5) */
.doctor-objections{
  background: linear-gradient(180deg, var(--paper) 0%, var(--cream) 100%);
  border-top: 1px dashed var(--gold);
}
.doctor-objections .doctor-tag{
  display: inline-block;
  font-size: 11px; font-weight: 700; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--gold-dark);
  background: rgba(159,136,68,0.10);
  padding: 6px 12px; border-radius: 4px;
  margin-bottom: var(--s-4);
}
.doctor-objections h2{
  font-family: var(--serif); font-size: clamp(28px, 3vw, 40px);
  font-weight: 500; color: var(--ink); letter-spacing: -0.01em;
  margin-bottom: var(--s-4);
}
.doctor-objections .lead{
  max-width: 780px; font-size: 15px; line-height: 1.6;
  color: var(--muted); margin-bottom: var(--s-7); font-style: italic;
}
.doctor-obj-grid{
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: var(--s-5);
}
.doctor-obj-card{
  background: var(--paper); border: 1px solid var(--line);
  border-left: 3px solid var(--gold);
  border-radius: 12px; padding: var(--s-5) var(--s-6);
  transition: box-shadow 0.3s;
}
.doctor-obj-card:hover{ box-shadow: 0 14px 28px -14px rgba(54,43,24,0.12); }
.doctor-obj-card h3{
  font-family: var(--serif); font-size: 19px; font-weight: 500;
  font-style: italic; color: var(--ink); margin-bottom: var(--s-4);
  line-height: 1.4;
}
.doctor-obj-card p{
  font-size: 13.5px; line-height: 1.55; color: var(--body);
  margin-bottom: var(--s-3);
}
.doctor-obj-card p strong{
  color: var(--gold-dark); font-weight: 700;
  font-size: 11px; letter-spacing: 0.10em; text-transform: uppercase;
  display: inline-block; margin-right: 6px;
}
.doctor-obj-card .cond{
  border-top: 1px dashed var(--line);
  padding-top: var(--s-3); margin-top: var(--s-3);
  font-style: italic; color: var(--ink);
}

@media(max-width: 900px){
  .doctor-obj-grid{ grid-template-columns: 1fr; }
}

/* Ocultar em modo apresentação (uso médico interno apenas) */
/* doctor-objections gerenciado pelas regras de modo (V2.5) */

/* Print: oculto também (não é parte do documento entregue ao paciente) */
@media print{
  .doctor-objections{ display: none !important; }
}

/* V2.3 — Programa enxuto (4 fases simples) */
.program-180-days .program-phase{ padding: var(--s-6) 0; }
.program-180-days .phase-marker .num{
  font-family: var(--serif); font-size: 26px; font-weight: 600;
  color: var(--gold-dark); font-style: italic; line-height: 1;
}
.program-180-days .phase-content h4{
  font-family: var(--serif); font-size: clamp(20px, 2vw, 24px);
  font-weight: 500; color: var(--ink); margin-bottom: var(--s-3);
  text-transform: none; letter-spacing: -0.005em;
}
.program-180-days .phase-content .desc{ font-size: 15px; line-height: 1.6; color: var(--body); margin: 0; }

/* V2.3 — Leitura integrada do caso (substitui SPIN visível) */
.leitura-integrada{ background: var(--cream); }
.leitura-block{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: var(--s-6) var(--s-7);
  margin-bottom: var(--s-5);
  position: relative;
  background: linear-gradient(180deg, var(--paper) 0%, #fffcf3 100%);
  transition: box-shadow 0.3s;
}
.leitura-block:hover{ box-shadow: 0 18px 36px -16px rgba(54,43,24,0.10); }
.leitura-block h3{
  font-family: var(--serif); font-size: clamp(20px, 2.2vw, 26px);
  font-weight: 500; color: var(--ink); margin-bottom: var(--s-3);
  letter-spacing: -0.01em;
}
.leitura-block .body-text{
  font-size: 15px; line-height: 1.6; color: var(--body); margin-bottom: var(--s-4);
}
.leitura-block .alinhamento{
  background: linear-gradient(135deg, #fffcf3 0%, var(--cream) 100%);
  border-left: 3px solid var(--gold);
  padding: var(--s-4) var(--s-5); border-radius: 0 8px 8px 0;
  font-family: var(--serif); font-style: italic; font-size: 16px;
  color: var(--ink); margin-top: var(--s-4); position: relative;
}
.leitura-block .alinhamento::after{
  content:"›"; position:absolute; right:var(--s-5); top:50%; transform:translateY(-50%);
  font-size:32px; color:var(--gold); font-weight:300; font-family:var(--serif);
}

/* V2.2 — Hero com foto da Dra */
.hero-grid{
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--s-7);
  align-items: center;
}
.hero-text{ min-width: 0; }
.hero-photo{
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: var(--cream-elev);
  box-shadow: 0 30px 60px -25px rgba(31,26,18,0.30), 0 14px 28px -10px rgba(159,136,68,0.15);
  aspect-ratio: 4 / 5;
  max-width: 380px;
  justify-self: end;
  width: 100%;
}
.hero-photo img{
  width: 100%; height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}
.hero-photo::after{
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, transparent 60%, rgba(31,26,18,0.45) 100%);
}
.hero-photo-caption{
  position: absolute; left: var(--s-5); right: var(--s-5); bottom: var(--s-5);
  z-index: 2; color: #F7F2E4;
  font-family: var(--sans); font-size: 11px;
  letter-spacing: 0.16em; text-transform: uppercase; line-height: 1.5;
}
.hero-photo-caption strong{
  display: block;
  font-family: var(--serif);
  font-size: 17px;
  font-weight: 500;
  font-style: italic;
  text-transform: none;
  letter-spacing: -0.005em;
  margin-bottom: 4px;
  color: #FFFFFF;
}

@media(max-width: 900px){
  .hero-grid{ grid-template-columns: 1fr; gap: var(--s-5); }
  .hero-photo{ max-width: 280px; justify-self: center; aspect-ratio: 3 / 4; }
  .hero-photo-caption{ font-size: 10px; }
  .hero-photo-caption strong{ font-size: 15px; }
}

/* V2.2 — Progress nav: scroll suave sem sobreposição */
section[id]{ scroll-margin-top: 76px; }
@media(max-width: 900px){ section[id]{ scroll-margin-top: 60px; } }

/* V2.2 — Grid 2 colunas no Diagnóstico Executivo */
.diag-grid-2col{ grid-template-columns: 1fr 1fr !important; }
@media(max-width: 900px){ .diag-grid-2col{ grid-template-columns: 1fr !important; } }

/* === Tese clínica do caso (P1.7) === */
.tese-clinica{
  background: linear-gradient(135deg, #1F1A12 0%, #2D2310 100%);
  border-radius:14px; padding:var(--s-6) var(--s-7);
  margin-bottom:var(--s-6); position:relative; overflow:hidden;
  border:1px solid rgba(212,188,121,0.20);
  box-shadow: 0 18px 36px -16px rgba(31,26,18,0.40);
}
.tese-clinica::before{
  content:""; position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg, var(--gold) 0%, var(--gold2) 50%, var(--gold) 100%);
}
.tese-clinica .tese-tag{
  font-size:11px; font-weight:700; letter-spacing:0.20em;
  text-transform:uppercase; color:var(--gold2);
  display:block; margin-bottom:var(--s-3);
}
.tese-clinica .tese-texto{
  font-family:var(--serif); font-size:clamp(18px, 1.9vw, 22px);
  line-height:1.5; color:#F7F2E4; font-style:italic; margin:0;
}
.tese-clinica .tese-texto strong{ color:var(--gold2); font-style:normal; font-weight:600; }

/* === Conexão exame → sintoma (P1.8) === */
.conexao-sintoma{
  background:linear-gradient(135deg, rgba(159,136,68,0.06) 0%, rgba(159,136,68,0.02) 100%);
  border-left:2px solid var(--gold);
  padding:var(--s-3) var(--s-4); margin:var(--s-4) 0;
  border-radius:0 8px 8px 0;
}
.conexao-sintoma .conexao-tag{
  font-size:10px; font-weight:700; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--gold-dark); display:block; margin-bottom:4px;
}
.conexao-sintoma p{
  font-family:var(--serif); font-size:14px; font-style:italic;
  color:var(--ink); margin:0; line-height:1.5;
}

/* === Custo de não acompanhar (P0.4) === */
.custo-nao-acompanhar{ background:var(--paper); }
.custo-grid{
  display:grid; grid-template-columns:repeat(2, 1fr);
  gap:var(--s-4); margin-top:var(--s-6);
}
.custo-card{
  background: linear-gradient(180deg, var(--cream) 0%, var(--paper) 100%);
  border:1px solid var(--line); border-radius:12px;
  padding:var(--s-5) var(--s-6); border-left:3px solid var(--amber);
  position:relative;
}
.custo-card .custo-icon{
  width:32px; height:32px; color:var(--amber); margin-bottom:var(--s-3);
}
.custo-card .custo-icon svg{ width:100%; height:100%; }
.custo-card .custo-titulo{
  font-family:var(--serif); font-size:18px; font-weight:500;
  color:var(--ink); margin-bottom:var(--s-3); text-transform:none; letter-spacing:-0.005em;
}
.custo-card .custo-desc{
  font-size:14px; line-height:1.55; color:var(--body); margin:0;
}

/* === Inclusos (P0.5) === */
.inclusos{ background:var(--cream); }
.inclusos-grid{
  display:grid; grid-template-columns:repeat(4, 1fr);
  gap:var(--s-4); margin-top:var(--s-6);
}
.incluso-card{
  background:var(--paper); border:1px solid var(--line); border-radius:12px;
  padding:var(--s-5); text-align:left;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position:relative; border-top:3px solid var(--gold);
}
.incluso-card:hover{
  transform: translateY(-3px);
  box-shadow: 0 18px 36px -16px rgba(54,43,24,0.14);
  border-top-color: var(--gold-dark);
}
.incluso-card .incluso-icon{
  width:32px; height:32px; color:var(--gold-dark); margin-bottom:var(--s-3);
}
.incluso-card .incluso-icon svg{ width:100%; height:100%; }
.incluso-card .incluso-titulo{
  font-family:var(--serif); font-size:16px; font-weight:500;
  color:var(--ink); margin-bottom:var(--s-2); text-transform:none; letter-spacing:-0.005em;
}
.incluso-card .incluso-desc{
  font-size:13px; line-height:1.55; color:var(--body); margin:0;
}

/* === Proof thesis (P1.9) === */
.proof-thesis{
  margin:var(--s-6) 0; padding:var(--s-5) var(--s-6);
  background: linear-gradient(135deg, var(--paper) 0%, #fffcf3 100%);
  border:1px solid var(--line); border-radius:12px; border-left:3px solid var(--gold);
}
.proof-thesis p{
  font-family:var(--serif); font-size:17px; font-style:italic;
  color:var(--ink); margin:0; line-height:1.55;
}
.proof-thesis strong{ color:var(--gold-dark); font-style:normal; font-weight:600; }

/* === Objection close (P1.10) === */
.obj-card{ display:flex; flex-direction:column; }
.obj-card .obj-a{ flex:1; }
.obj-card .obj-close{
  margin-top:var(--s-4); padding-top:var(--s-4);
  border-top:1px dashed var(--line);
  font-family:var(--serif); font-size:14px; font-style:italic;
  color:var(--gold-dark); line-height:1.5;
  display:flex; gap:var(--s-3); align-items:flex-start;
}
.obj-card .obj-close-marker{ color:var(--gold); font-weight:700; font-style:normal; flex-shrink:0; }

/* === Modo apresentação: oculta detalhes técnicos das alavancas (P2.11) === */
body.js-enabled.modo-apresentacao .lever-narrative h4,
body.js-enabled.modo-apresentacao .lever-narrative .impact{
  display:none !important;
}

/* === Mobile padding (P2.13) === */
@media(max-width: 900px){
  .section{ padding: var(--s-7) 0; }
  .custo-grid, .inclusos-grid{ grid-template-columns: 1fr; }
}
@media(max-width: 600px){
  .inclusos-grid{ grid-template-columns: 1fr; }
}
@media(min-width: 601px) and (max-width: 900px){
  .inclusos-grid{ grid-template-columns: repeat(2, 1fr); }
  .custo-grid{ grid-template-columns: 1fr; }
}

/* Fade-up p/ tese-clinica + proof-thesis + custo-card + incluso-card já é aplicado na classe */

/* Print: novas seções */
@media print{
  .tese-clinica{ background:#fff !important; color:#000 !important; border:1px solid #ccc !important; box-shadow:none !important; }
  .tese-clinica .tese-texto{ color:#000 !important; }
  .tese-clinica .tese-tag{ color:#666 !important; }
  .custo-card, .incluso-card, .proof-thesis{ box-shadow:none !important; background:#fff !important; }
}


/* === PREMIUM REFINEMENTS === */

/* Tipografia variable + features */
body{
  font-feature-settings: "ss01", "kern", "liga", "calt", "tnum";
  text-underline-offset: 2px;
}
.tabular { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }

/* Background com texture sutil */
body::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:-1;
  background-image:
    radial-gradient(circle at 20% 10%, rgba(159,136,68,0.04) 0%, transparent 40%),
    radial-gradient(circle at 80% 90%, rgba(159,136,68,0.05) 0%, transparent 40%);
}

/* Decorative gold corner brackets em cards principais */
.diag-recomendacao{
  position:relative; overflow:hidden;
  background:linear-gradient(135deg, #1F1A12 0%, #2D2310 100%);
  border:1px solid rgba(212,188,121,0.20);
  box-shadow:0 30px 60px -20px rgba(31,26,18,0.50), 0 18px 36px -12px rgba(159,136,68,0.15);
}
.diag-recomendacao::before, .diag-recomendacao::after{
  content:""; position:absolute; width:42px; height:42px;
  border:1.5px solid var(--gold2); opacity:0.55;
}
.diag-recomendacao::before{ top:14px; left:14px; border-right:none; border-bottom:none; }
.diag-recomendacao::after{ bottom:14px; right:14px; border-left:none; border-top:none; }

/* Diagnostic cards com subtle gradient + hover depth */
.diag-card{
  position:relative; transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s, border-color 0.35s;
  background: linear-gradient(180deg, var(--paper) 0%, var(--cream) 100%);
}
.diag-card:hover{
  transform: translateY(-3px);
  border-color: rgba(159,136,68,0.30);
  box-shadow: 0 22px 42px -18px rgba(54,43,24,0.18);
}
.diag-card::after{
  content:""; position:absolute; top:0; left:50%; width:60px; height:3px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--gold2) 100%);
  transform: translateX(-50%);
}

/* Hero — decorative eyebrow ornament */
.hero-clinical-document{ position:relative; }
.hero-clinical-document::before{
  content:""; position:absolute; top:0; left:50%; transform:translateX(-50%);
  width:60px; height:1px; background:var(--gold); opacity:0.4;
}
.hero-meta-bar{ position:relative; }
.hero-meta-item strong{ font-feature-settings:"tnum"; }

/* Mirror cards com hover lift */
.mirror-card{
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background:linear-gradient(180deg, #fff 0%, #fbf6e8 100%);
}
.mirror-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 14px 28px -12px rgba(54,43,24,0.10);
  border-color: rgba(159,136,68,0.25);
}
.mirror-card.feature{
  background:linear-gradient(135deg, #fffcf3 0%, #fbf6e8 50%, #f7f2e4 100%);
}

/* Critical Levers — severity ring + sparkline visual */
.lever-card{
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  background:linear-gradient(180deg, var(--cream) 0%, var(--paper) 100%);
  position:relative;
  overflow:hidden;
}
.lever-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 22px 44px -20px rgba(54,43,24,0.16);
}
.lever-card::before{
  content:""; position:absolute; left:0; top:0; bottom:0; width:4px;
}
.lever-card[data-sev="crit"]::before{ background:linear-gradient(180deg, var(--red) 0%, #6e1d12 100%); }
.lever-card[data-sev="alert"]::before{ background:linear-gradient(180deg, var(--amber) 0%, #7a5108 100%); }

.lever-numeric{
  display:flex; flex-direction:column; gap:var(--s-2);
  padding-right:var(--s-5); border-right:1px solid var(--line);
}
.lever-numeric .name{
  display:flex; align-items:center; gap:var(--s-3);
}
.lever-numeric .value{ font-feature-settings:"tnum"; letter-spacing:-0.025em; }

/* Severity Ring (donut) */
.sev-ring{
  width:54px; height:54px; flex-shrink:0; position:relative;
}
.sev-ring svg{ width:100%; height:100%; transform:rotate(-90deg); }
.sev-ring .ring-track{ fill:none; stroke:var(--line); stroke-width:6; }
.sev-ring .ring-fill{ fill:none; stroke-width:6; stroke-linecap:round; transition:stroke-dashoffset 1.2s cubic-bezier(0.16, 1, 0.3, 1); }
.lever-card[data-sev="crit"] .sev-ring .ring-fill{ stroke:#BE3226; }
.lever-card[data-sev="alert"] .sev-ring .ring-fill,
.lever-card[data-sev="low"] .sev-ring .ring-fill,
.lever-card[data-sev="attn"] .sev-ring .ring-fill{ stroke:#D4A000; }
.lever-card[data-sev="ok"] .sev-ring .ring-fill,
.lever-card[data-sev="normal"] .sev-ring .ring-fill{ stroke:#2D8A3F; }
.lever-card[data-sev="low"] .sev-ring .ring-fill{ stroke:var(--amber); }
.sev-ring .ring-label{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size:11px; font-weight:700; letter-spacing:0.05em; color:var(--ink);
  font-family:var(--sans); font-feature-settings:"tnum";
}

/* Sparkline (valor x faixa) */
.lever-sparkline{
  margin-top:var(--s-3); padding-top:var(--s-3); border-top:1px dashed var(--line);
}
.lever-sparkline .sparkline-label{
  font-size:10px; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted);
  margin-bottom:6px; font-weight:600;
}
.lever-sparkline svg{ width:100%; height:36px; display:block; }
.spark-track{ fill:rgba(159,136,68,0.08); }
.spark-range{ fill:rgba(21,85,39,0.18); }
.spark-marker{ fill:var(--ink); }
.spark-marker.alert,
.spark-marker.low,
.spark-marker.attn{ fill:#D4A000; }
.spark-marker.crit{ fill:#BE3226; }
.spark-marker.ok,
.spark-marker.normal{ fill:#2D8A3F; }
.spark-tick{ stroke:var(--muted); stroke-width:1; }
.spark-label{ font-size:9px; fill:var(--muted); font-family:var(--sans); font-feature-settings:"tnum"; }

/* Lever narrative — subtle improvements
   2026-06-05: removido ícone pseudo-elemento "⚡".
   Em iPhone/visualizador do Telegram ele quebrava a tipografia e invadia o texto
   de "Implicação clínica" / "Necessidade de solução". */
.lever-narrative .impact{
  background:linear-gradient(180deg, var(--paper) 0%, #fff 100%);
  position:relative;
}
.lever-narrative .impact::before{
  content:none !important;
  display:none !important;
}

/* SPIN steps — number badges decorativos */
.spin-step-block{
  position:relative;
  background:linear-gradient(180deg, var(--paper) 0%, #fffcf3 100%);
  transition: box-shadow 0.3s;
}
.spin-step-block:hover{ box-shadow: 0 18px 36px -16px rgba(54,43,24,0.10); }
.spin-step-block .step-tag{
  background:linear-gradient(90deg, var(--gold) 0%, var(--gold2) 100%);
  color:#fff !important;
  padding:5px 14px; border-radius:6px;
  display:inline-block;
}
.spin-step-block .confirmation{
  background:linear-gradient(135deg, #fffcf3 0%, var(--cream) 100%);
  position:relative;
}
.spin-step-block .confirmation::after{
  content:"›"; position:absolute; right:var(--s-5); top:50%; transform:translateY(-50%);
  font-size:32px; color:var(--gold); font-weight:300; font-family:var(--serif);
}

/* IVS Machine — connected flow (linha conectora) */
.machine-flow{ position:relative; }
.machine-flow::before{
  content:""; position:absolute; top:50px; left:8%; right:8%; height:1px;
  background: linear-gradient(90deg, transparent 0%, var(--gold) 20%, var(--gold) 80%, transparent 100%);
  opacity:0.35; z-index:0;
}
.machine-step{
  position:relative; z-index:1;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background:linear-gradient(180deg, var(--paper) 0%, var(--cream) 100%);
}
.machine-step:hover{
  transform: translateY(-3px);
  box-shadow: 0 16px 32px -14px rgba(54,43,24,0.16);
  border-color: rgba(159,136,68,0.30);
}
.machine-step .num{
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
  box-shadow: 0 4px 12px rgba(159,136,68,0.30);
  border:2px solid #fff;
}

/* Proof — refinement das imagens */
.proof-card{
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  background:linear-gradient(180deg, var(--paper) 0%, #fffcf3 100%);
}
.proof-card:hover{ box-shadow: 0 22px 44px -20px rgba(54,43,24,0.18); }
.proof-img{ box-shadow: 0 6px 16px -8px rgba(54,43,24,0.20); }
.proof-img .label{
  background:rgba(31,26,18,0.85); color:#f7f2e4 !important;
  backdrop-filter: blur(4px);
}
.proof-text blockquote{ position:relative; }
.proof-text blockquote::before{
  content:"\201C"; position:absolute; left:-22px; top:-12px;
  font-family:var(--serif); font-size:48px; color:var(--gold); opacity:0.30; line-height:1;
}

/* Program timeline — phase markers premium */
.program-phase .phase-marker{
  background:linear-gradient(135deg, var(--paper) 0%, var(--cream) 100%);
  box-shadow: 0 4px 12px -4px rgba(54,43,24,0.10);
}
.program-phase .phase-marker .num{ font-feature-settings:"tnum"; }
.program-phase{ transition: background 0.3s; }
.program-phase:hover{ background: rgba(255,253,247,0.5); }

/* Objection cards */
.obj-card{
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background:linear-gradient(180deg, var(--paper) 0%, #fffcf3 100%);
}
.obj-card:hover{
  transform: translateY(-3px);
  box-shadow: 0 18px 36px -16px rgba(54,43,24,0.14);
}

/* Decision Checklist — animação */
.checklist-card{
  background:linear-gradient(135deg, var(--cream) 0%, #fffcf3 100%);
  position:relative; overflow:hidden;
  box-shadow: 0 24px 50px -22px rgba(54,43,24,0.12);
}
.checklist-card::before{
  content:""; position:absolute; top:0; left:0; right:0; height:4px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--gold2) 50%, var(--gold) 100%);
}
.checklist-item{ transition: all 0.25s; }
.checklist-item:hover{ background: rgba(255,255,255,0.5); padding-left: 6px; padding-right: 6px; border-radius:6px; }
.checklist-item .check{ box-shadow: 0 2px 6px -2px rgba(159,136,68,0.20); }
.checklist-progress{
  margin-top:var(--s-5); padding-top:var(--s-4); border-top:1px solid var(--line);
  display:flex; align-items:center; gap:var(--s-3);
}
.checklist-progress-bar{
  flex:1; height:6px; background:rgba(159,136,68,0.15); border-radius:999px; overflow:hidden;
}
.checklist-progress-fill{
  height:100%; background: linear-gradient(90deg, var(--gold) 0%, var(--gold2) 100%);
  width:0%; transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.checklist-progress-text{
  font-size:11px; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted);
  font-weight:700; font-feature-settings:"tnum";
}

/* Final CTA — premium buttons */
.cta-card{
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position:relative;
}
.cta-card.recommended{
  background: linear-gradient(180deg, #FFFCF3 0%, var(--paper) 100%);
  box-shadow: 0 30px 60px -25px rgba(159,136,68,0.30);
}
.cta-card.recommended::before{
  content:""; position:absolute; top:0; left:0; right:0; height:4px;
  background: linear-gradient(90deg, var(--gold) 0%, var(--gold2) 50%, var(--gold) 100%);
  border-radius:14px 14px 0 0;
}
.cta-card.recommended:hover{ transform: translateY(-4px); box-shadow: 0 40px 80px -30px rgba(159,136,68,0.40); }
.cta-card .button{
  position:relative; overflow:hidden; transition: all 0.3s;
}
.cta-card.recommended .button{
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
  box-shadow: 0 6px 18px -4px rgba(107,90,43,0.40);
}
.cta-card.recommended .button:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -4px rgba(107,90,43,0.50);
}

.cta-signature{ position:relative; }
.cta-signature::before{
  content:""; display:block; width:48px; height:1px; background:var(--gold);
  margin:0 auto var(--s-5);
}

/* Technical Appendix — versão estável para Telegram/iPhone */
.exam-group{
  transition:none;
  background:var(--paper);
}
.exam-group:hover{ border-color: var(--line); }
.exam-group.open{ box-shadow:none; }
.exam-group-header{
  background:var(--paper);
  transition:none;
}
.exam-group-header:hover{ background:var(--paper); }
.exam-group-header .toggle{
  font-size:18px; color:var(--gold-dark);
  background:transparent; border-radius:0;
  width:24px; height:24px;
}
.exam-row:hover{ background:transparent; }
.exam-row .e-valor{ font-feature-settings:"tnum"; }
.exam-row[data-sev="crit"] .e-status::before,
.exam-row[data-sev="alert"] .e-status::before,
.exam-row[data-sev="low"] .e-status::before,
.exam-row[data-sev="ok"] .e-status::before,
.exam-row[data-sev="normal"] .e-status::before{
  content:"●"; margin-right:4px;
}

/* RC-25 — Diagramação técnica dos exames: formato de tabela legível em desktop */
@media(min-width: 901px){
  .technical-appendix .exam-group{ border-radius:14px; overflow:hidden; }
  .technical-appendix .exam-group-body{ padding:0; }
  .technical-appendix .exam-table-head{
    display:grid;
    grid-template-columns:minmax(240px,1.45fr) minmax(130px,.55fr) minmax(180px,.85fr) 110px;
    gap:18px;
    padding:10px 22px;
    background:rgba(184,140,50,0.07);
    border-bottom:1px solid var(--line);
    font-family:var(--sans);
    font-size:10px;
    font-weight:800;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:var(--muted);
  }
  .technical-appendix .exam-row{
    display:grid;
    grid-template-columns:minmax(240px,1.45fr) minmax(130px,.55fr) minmax(180px,.85fr) 110px;
    gap:18px;
    align-items:center;
    padding:12px 22px;
    border-bottom:1px solid rgba(54,43,24,.10);
    min-height:56px;
  }
  .technical-appendix .exam-row:nth-child(odd){ background:rgba(250,248,242,.55); }
  .technical-appendix .exam-row .e-nome,
  .technical-appendix .exam-row .e-valor,
  .technical-appendix .exam-row .e-ref,
  .technical-appendix .exam-row .e-status{
    display:block; margin:0; min-width:0;
  }
  .technical-appendix .exam-row .e-nome{
    font-family:var(--sans); font-size:14px; font-weight:650; line-height:1.25;
  }
  .technical-appendix .exam-row .e-valor{
    font-family:var(--serif); font-size:20px; font-weight:650; line-height:1; white-space:nowrap;
  }
  .technical-appendix .exam-row .e-valor .e-unit{
    display:inline-block; font-size:11px; margin-left:5px; white-space:nowrap;
  }
  .technical-appendix .exam-row .e-ref{
    font-size:12px; line-height:1.25; color:var(--muted);
  }
  .technical-appendix .exam-row .e-status{
    justify-self:end; text-align:center;
    padding:6px 9px; border-radius:999px;
    font-size:9px; letter-spacing:.12em;
    background:rgba(31,110,45,.08); color:#1F6E2D;
  }
  .technical-appendix .exam-row[data-sev="crit"] .e-status{ background:rgba(142,36,23,.10); color:#8E2417; }
  .technical-appendix .exam-row[data-sev="alert"] .e-status,
  .technical-appendix .exam-row[data-sev="low"] .e-status,
  .technical-appendix .exam-row[data-sev="attn"] .e-status{ background:rgba(139,106,0,.10); color:#8B6A00; }
}

/* Animações scroll-triggered */
.fade-up{ opacity:0; transform: translateY(24px); transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-up.in{ opacity:1; transform: translateY(0); }
.fade-up.delay-1{ transition-delay: 0.10s; }
.fade-up.delay-2{ transition-delay: 0.20s; }
.fade-up.delay-3{ transition-delay: 0.30s; }
.fade-up.delay-4{ transition-delay: 0.40s; }

/* Section icons */
.section-icon{
  width:32px; height:32px; color:var(--gold-dark); margin-bottom:var(--s-3);
  display:inline-block;
}
.section-icon svg{ width:100%; height:100%; stroke:currentColor; fill:none; stroke-width:1.4; stroke-linecap:round; stroke-linejoin:round; }

/* Eyebrow / pill premium */
h2 + p, .section-header p{ font-feature-settings:"kern", "liga"; }


/* P2.13 — Modo apresentação amplificado */
/* Sparkline e sev-ring ficam visíveis em modo apresentação (V2.10) */
body.js-enabled.modo-apresentacao .lever-numeric .name{ font-size:24px; }
body.js-enabled.modo-apresentacao .lever-numeric{ border-right:none; padding-right:0; }
body.js-enabled.modo-apresentacao .lever-card{ grid-template-columns: 1fr 1.6fr; }
body.js-enabled.modo-apresentacao .technical-appendix{ display:none !important; }

/* P2.12 — Apêndice toggle só desktop */
@media(max-width: 768px){
  .appendix-toggle-all{ display:none; }
}

/* P1.10 — CTA frame */
.cta-frame{
  margin: 0 auto var(--s-7);
  max-width: 880px;
  padding: var(--s-6) var(--s-7);
  background: linear-gradient(135deg, var(--paper) 0%, var(--cream) 100%);
  border: 1px solid var(--line);
  border-radius: 14px;
  border-left: 4px solid var(--gold);
  box-shadow: 0 14px 28px -14px rgba(54,43,24,0.12);
}
.cta-frame-text{
  font-family: var(--serif);
  font-size: clamp(17px, 1.7vw, 21px);
  line-height: 1.55;
  color: var(--ink);
  margin: 0;
  font-style: italic;
}
.cta-frame-text strong{ color: var(--gold-dark); font-style: normal; font-weight: 600; }
.cta-frame-text em{ font-style: italic; color: var(--muted); }

/* P1.9 — Sev ring tooltip */
.sev-ring{ cursor: help; }
.sev-ring::after{
  content: attr(title);
  position: absolute; top: -32px; left: 50%; transform: translateX(-50%);
  background: var(--ink); color: var(--cream);
  padding: 4px 10px; border-radius: 6px;
  font-size: 10px; font-weight: 600; letter-spacing: 0.10em;
  text-transform: uppercase; white-space: nowrap;
  opacity: 0; pointer-events: none; transition: opacity 0.2s;
}
.sev-ring:hover::after{ opacity: 1; }

/* P0.2 — números com tabular-nums em todo o documento */
.exam-row, .lever-numeric .value, .program-phase .num,
.checklist-progress-text, .ring-label, .spark-label, .e-valor{
  font-feature-settings: "tnum"; font-variant-numeric: tabular-nums;
}

/* Print refinements */
@media print{
  body::before{ display:none; }
  .diag-recomendacao::before, .diag-recomendacao::after{ display:none; }
  .lever-card, .diag-card, .obj-card, .mirror-card, .cta-card, .exam-group{
    box-shadow: none !important;
    background: #fff !important;
    border: 1px solid #ddd !important;
  }
  .machine-flow::before{ display:none; }
  .fade-up{ opacity:1 !important; transform:none !important; }
}


/* ========================================================================
   V2.7 — Botão "Enviar ao paciente" + Modal + Mobile responsivo
   ======================================================================== */

/* Topbar right cluster */
.topbar-right{ display: flex; align-items: center; gap: var(--s-4); }
.topbar-send-btn{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 14px;
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  color: #fff; border: none; border-radius: 999px;
  font-family: var(--sans); font-size: 12px;
  font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase;
  cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 10px rgba(37,211,102,0.25);
}
.topbar-send-btn:hover{
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37,211,102,0.35);
}
.topbar-send-btn svg{ width: 16px; height: 16px; }

/* Garantia: versão paciente nunca mostra botão de envio */
body.versao-paciente .topbar-send-btn,
body.versao-paciente #send-modal{ display: none !important; }

/* Modal de envio */
.send-modal{
  position: fixed; inset: 0; z-index: 9999;
  display: none;
  align-items: center; justify-content: center;
  padding: var(--s-4);
}
.send-modal.is-open{ display: flex !important; }
body.modal-locked{ overflow: hidden; }
.send-modal-backdrop{
  position: absolute; inset: 0;
  background: rgba(31,26,18,0.55);
  backdrop-filter: blur(4px);
}
.send-modal-card{
  position: relative; z-index: 1;
  background: var(--paper); border-radius: 16px;
  padding: var(--s-7) var(--s-7) var(--s-6);
  max-width: 480px; width: 100%;
  box-shadow: 0 30px 60px -20px rgba(31,26,18,0.40);
  animation: slideUpModal 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUpModal {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.send-modal-close{
  position: absolute; top: 12px; right: 12px;
  width: 36px; height: 36px; border: none; border-radius: 50%;
  background: var(--cream); color: var(--muted);
  font-size: 24px; line-height: 1; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.send-modal-close:hover{ background: var(--gold); color: #fff; }
.send-modal-card h3{
  font-family: var(--serif); font-size: 22px; font-weight: 500;
  color: var(--ink); margin: 0 0 var(--s-2); padding-right: 32px;
}
.send-modal-sub{
  font-size: 13px; color: var(--muted); font-style: italic;
  margin: 0 0 var(--s-5);
}
.send-field{ display: block; margin-bottom: var(--s-4); }
.send-field span{
  display: block; font-size: 11px; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--gold-dark); margin-bottom: 6px;
}
.send-field input, .send-field textarea{
  width: 100%; padding: var(--s-3) var(--s-4);
  border: 1px solid var(--line); border-radius: 8px;
  background: var(--cream); font-family: var(--sans);
  font-size: 14px; color: var(--ink); resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.send-field input:focus, .send-field textarea:focus{
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(159,136,68,0.15);
  background: var(--paper);
}
.send-actions{
  display: flex; gap: var(--s-3); margin-top: var(--s-5); flex-wrap: wrap;
}
.send-btn-primary, .send-btn-secondary{
  flex: 1; min-width: 140px;
  padding: var(--s-4); border: none; border-radius: 10px;
  font-family: var(--sans); font-size: 13px;
  font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase;
  cursor: pointer; transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
}
.send-btn-primary{
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  color: #fff; box-shadow: 0 4px 12px rgba(37,211,102,0.30);
}
.send-btn-primary:hover{
  transform: translateY(-1px); box-shadow: 0 8px 18px rgba(37,211,102,0.40);
}
.send-btn-primary svg{ width: 16px; height: 16px; }
.send-btn-secondary{
  background: var(--paper); color: var(--ink);
  border: 1px solid var(--line);
}
.send-btn-secondary:hover{ background: var(--cream); border-color: var(--gold); }
.send-hint{
  margin-top: var(--s-4); padding-top: var(--s-3);
  border-top: 1px dashed var(--line);
  font-size: 11px; color: var(--muted); line-height: 1.5;
}

@media print{ .send-modal, .topbar-send-btn{ display: none !important; } }

/* ========================================================================
   V2.7 — Mobile responsivo (revisão geral)
   ======================================================================== */
@media(max-width: 900px){
  /* Topbar */
  .topbar{ padding: var(--s-2) var(--s-4); }
  .topbar-inner{ min-height: 60px; gap: var(--s-3); }
  .topbar .logo{ height: 50px; max-width: 180px; }
  .topbar .doctor-tag{ display: none; }
  /* topbar-send-btn estilizado pela media V2.8 (linhas abaixo) */

  /* Progress nav */
  .progress-nav-inner{ padding: var(--s-2) var(--s-3); gap: var(--s-1); overflow-x: auto; flex-wrap: nowrap; }
  .progress-step{ font-size: 9px; padding: 4px 8px; flex-shrink: 0; }
  .mode-switcher{ padding: 2px; gap: 2px; flex-shrink: 0; margin-left: 0; order:-1; }
  .mode-btn{ font-size: 9px; padding: 4px 8px; letter-spacing: 0.08em; }

  /* Hero */
  .hero-meta-bar{ gap: var(--s-3); flex-wrap: wrap; }
  .hero-meta-item{ font-size: 11px; }
  .hero-meta-item strong{ font-size: 14px; }
  .hero-clinical-h1{ font-size: clamp(26px, 6vw, 38px); }

  /* Diagnóstico */
  .diag-grid, .diag-grid-2col{ grid-template-columns: 1fr !important; gap: var(--s-3); }
  .diag-card{ padding: var(--s-5); }
  .diag-recomendacao{ padding: var(--s-5); font-size: 16px; }
  .tese-clinica{ padding: var(--s-5); }
  .tese-clinica .tese-texto{ font-size: 16px; }

  /* Mirror */
  .mirror-grid{ grid-template-columns: 1fr; gap: var(--s-3); }
  .mirror-card.feature{ grid-column: span 1; }

  /* Critical Levers */
  .lever-card{
    grid-template-columns: 1fr !important;
    gap: var(--s-4); padding: var(--s-5);
  }
  .lever-numeric{
    border-right: none !important;
    border-bottom: 1px solid var(--line);
    padding-right: 0; padding-bottom: var(--s-4);
  }
  .lever-numeric .name{ font-size: 18px; gap: var(--s-2); }
  .lever-numeric .value{ font-size: 32px; }
  .sev-ring{ width: 44px; height: 44px; }
  .lever-sparkline svg{ height: 32px; }

  /* Leitura integrada */
  .leitura-block{ padding: var(--s-5); }
  .leitura-block h3{ font-size: 18px; }
  .spin-table{ font-size: 13px; display: block; overflow-x: auto; }
  .spin-table th, .spin-table td{ padding: var(--s-2) var(--s-3); }

  /* IVS Machine */
  .machine-flow{ grid-template-columns: 1fr 1fr !important; gap: var(--s-2); }
  .machine-flow::before{ display: none; }
  .machine-step{ padding: var(--s-3); }
  .machine-step .num{ width: 30px; height: 30px; font-size: 12px; }
  .machine-step .title{ font-size: 13px; }
  .machine-step .desc{ font-size: 11px; }

  /* Proof */
  .proof-card{ grid-template-columns: 1fr !important; gap: var(--s-4); padding: var(--s-4); }
  .proof-card:nth-child(even) .proof-imgs{ order: 0; }
  .proof-text blockquote{ font-size: 15px; padding-left: var(--s-3); }
  .proof-text blockquote::before{ font-size: 36px; left: -16px; top: -8px; }

  /* Programa */
  .program-phase{ grid-template-columns: 80px 1fr !important; gap: var(--s-4); padding: var(--s-4) 0; }
  .program-phase .phase-marker{ width: 80px; padding: var(--s-2); }
  .program-phase .phase-marker .num{ font-size: 22px; }
  .program-phase .phase-content h4{ font-size: 17px; }
  .program-phase .phase-content .desc{ font-size: 14px; }

  /* Inclusos — 1 coluna no mobile */
  .inclusos-grid{ grid-template-columns: 1fr !important; gap: var(--s-3); }
  .incluso-card{ padding: var(--s-4); }

  /* CTA */
  .cta-decision{ grid-template-columns: 1fr !important; gap: var(--s-3); }
  .cta-card{ padding: var(--s-5); }
  .cta-card h3{ font-size: 20px; }
  .cta-frame{ padding: var(--s-4) var(--s-5); }
  .cta-frame-text{ font-size: 16px; }

  /* Checklist */
  .checklist-card{ padding: var(--s-5); }
  .checklist-item .text{ font-size: 14px; }

  /* Apêndice técnico — tabela em mobile */
  .exam-row{
    grid-template-columns: 2fr 1fr !important;
    row-gap: 4px; font-size: 13px;
  }
  .exam-row .e-ref, .exam-row .e-status{ grid-column: span 2; font-size: 11px; }
  .exam-group-header{ padding: var(--s-3) var(--s-4); }
  .exam-group-body{ padding: 0 var(--s-4) var(--s-4); }

  section[id]{ scroll-margin-top: 60px; }

  /* Modal mobile */
  .send-modal-card{ padding: var(--s-5) var(--s-5) var(--s-5); }
  .send-modal-card h3{ font-size: 18px; }
  .send-actions{ flex-direction: column; }
  .send-btn-primary, .send-btn-secondary{ width: 100%; min-width: 0; }

  /* Garantir nada vaza largura no mobile */
  body{ overflow-x: hidden; }
  .wrap{ padding: 0 var(--s-4); }
  img, svg, table{ max-width: 100%; }
}

@media(max-width: 600px){
  .progress-step, .mode-btn{ font-size: 9px; }
  .hero-meta-bar{ flex-direction: column; align-items: flex-start; }
  .doctor-obj-card .obj-header h3{ font-size: 14px; }
  .machine-flow{ grid-template-columns: 1fr !important; }
}


/* ========================================================================
   V2.8 — Mobile responsivo (refatorado com guard rails agressivos)
   ======================================================================== */

/* Guard rails globais: nada estoura viewport */
html, body{ max-width: 100%; overflow-x: hidden; }
img, svg, video, table, iframe{ max-width: 100%; height: auto; }
.wrap{ max-width: 100%; box-sizing: border-box; }

/* Tablet & Mobile (≤900px) */
@media(max-width: 900px){
  /* Topbar */
  .topbar{ padding: 8px 14px; }
  .topbar-inner{ min-height: 56px; gap: 10px; flex-wrap: nowrap; }
  .topbar .logo{ height: 44px; max-width: 160px; flex-shrink: 1; min-width: 0; }
  .topbar .doctor-tag{ display: none !important; }
  .topbar-right{ gap: 8px; flex-shrink: 0; }
  /* Botão de envio: ícone-only no mobile, com touch target 44x44 mínimo (Apple HIG) */
  .topbar-send-btn{
    padding: 0;
    width: 44px; height: 44px;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .topbar-send-btn svg{ width: 20px; height: 20px; }
  .topbar-send-btn .lbl{ display: none !important; }

  /* Progress nav: scroll horizontal sem scrollbar visível */
  .progress-nav{ padding: 0; }
  .progress-nav-inner{
    padding: 8px 12px; gap: 4px;
    overflow-x: auto; overflow-y: hidden;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .progress-nav-inner::-webkit-scrollbar{ display: none; }
  .progress-step{ font-size: 9px; padding: 4px 8px; flex-shrink: 0; letter-spacing: 0.06em; white-space: nowrap; }
  .mode-switcher{ padding: 2px; gap: 2px; flex-shrink: 0; margin-left: 0; order:-1; }
  .mode-btn{ font-size: 9px; padding: 4px 8px; letter-spacing: 0.06em; white-space: nowrap; }

  /* Sections — padding reduzido */
  .section{ padding: 32px 0 !important; }
  section[id]{ scroll-margin-top: 56px; }
  h2{ font-size: 22px !important; line-height: 1.2 !important; margin-bottom: 12px !important; }
  h3{ font-size: 17px !important; }
  p, li{ font-size: 14px !important; }

  /* Hero */
  .hero-clinical-document{ padding: 32px 0 !important; }
  .hero-meta-bar{
    flex-wrap: wrap; gap: 10px;
    padding-bottom: 14px; margin-bottom: 16px;
  }
  .hero-meta-item{
    flex: 1 1 calc(50% - 5px); min-width: 0; font-size: 10px;
  }
  .hero-meta-item strong{ font-size: 13px; margin-top: 2px; }
  .hero-grid{
    grid-template-columns: 1fr !important;
    gap: 16px;
  }
  .hero-text{ order: 1; }
  .hero-photo{
    order: 2; max-width: 220px; aspect-ratio: 3/4;
    justify-self: center; margin: 0 auto;
  }
  .hero-photo-caption{ font-size: 9px; }
  .hero-photo-caption strong{ font-size: 14px; }
  .hero-clinical-h1{ font-size: 22px !important; line-height: 1.2 !important; }

  /* Reset agressivo de TODOS os grids para 1 coluna */
  .diag-grid, .diag-grid-2col,
  .mirror-grid,
  .machine-flow,
  .obj-grid,
  .cta-decision,
  .inclusos-grid,
  .resultados-list,
  .doctor-obj-grid{
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }

  /* Cards genéricos */
  .diag-card, .mirror-card, .obj-card, .cta-card, .incluso-card,
  .leitura-block, .machine-step, .doctor-obj-card{
    padding: 16px !important;
  }

  /* Diagnóstico */
  .tese-clinica{ padding: 16px !important; }
  .tese-clinica .tese-texto{ font-size: 15px !important; line-height: 1.45 !important; }
  .diag-recomendacao{ padding: 16px !important; font-size: 14px !important; line-height: 1.5 !important; }

  /* Mirror */
  .mirror-card.feature{ grid-column: span 1 !important; border-left: 4px solid var(--gold) !important; }

  /* Critical Levers — stack vertical */
  .lever-card{
    grid-template-columns: 1fr !important;
    gap: 14px !important; padding: 16px !important;
  }
  .lever-numeric{
    border-right: none !important; border-bottom: 1px solid var(--line) !important;
    padding-right: 0 !important; padding-bottom: 14px !important;
    flex-direction: row !important; align-items: flex-start !important;
    flex-wrap: wrap; gap: 10px !important;
  }
  .lever-numeric .name{ font-size: 16px !important; flex: 1 1 100%; gap: 8px; }
  .lever-numeric .value{ font-size: 28px !important; }
  .lever-numeric .ref{ font-size: 11px; flex: 1 1 100%; }
  .lever-numeric .badge{ flex-shrink: 0; }
  .sev-ring{ width: 38px !important; height: 38px !important; }
  .sev-ring .ring-label{ font-size: 9px !important; }
  .lever-sparkline{ width: 100%; }
  .lever-sparkline svg{ height: 28px; }
  .lever-narrative h4{ font-size: 12px; }
  .lever-narrative .interp{ font-size: 13px !important; }
  .lever-narrative .impact{ font-size: 12px !important; padding: 10px 12px !important; }
  .lever-narrative .conexao-sintoma{ padding: 10px 14px !important; }
  .lever-narrative .conexao-sintoma p{ font-size: 12px !important; }
  .lever-narrative .spin-q{ font-size: 13px !important; line-height: 1.4 !important; }

  /* Leitura integrada */
  .leitura-block h3{ font-size: 17px !important; }
  .leitura-block .body-text{ font-size: 13px !important; }
  .leitura-block .alinhamento{ padding: 10px 14px !important; font-size: 13px !important; }
  .leitura-block .alinhamento::after{ font-size: 24px !important; right: 12px !important; }

  /* Tabela leitura — scroll horizontal se precisar */
  .spin-table{ font-size: 12px !important; display: block; overflow-x: auto; }
  .spin-table thead, .spin-table tbody{ display: table; width: 100%; min-width: 480px; }
  .spin-table th, .spin-table td{ padding: 8px 10px !important; }

  /* Machine step — 1 coluna no mobile pequeno */
  .machine-flow::before{ display: none !important; }
  .machine-step{ padding: 14px !important; }
  .machine-step .num{ width: 32px !important; height: 32px !important; font-size: 13px !important; }
  .machine-step .title{ font-size: 14px !important; }
  .machine-step .desc{ font-size: 12px !important; }

  /* Proof */
  .proof-card{ grid-template-columns: 1fr !important; gap: 14px; padding: 14px !important; }
  .proof-card:nth-child(even) .proof-imgs{ order: 0 !important; }
  .proof-card:nth-child(even) .proof-text{ order: 1 !important; }
  .proof-imgs{ grid-template-columns: 1fr 1fr !important; gap: 8px !important; }
  .proof-img{ aspect-ratio: 3/4; }
  .proof-text h3{ font-size: 18px !important; }
  .proof-text blockquote{ font-size: 14px !important; padding-left: 14px !important; }
  .proof-text blockquote::before{ font-size: 32px !important; left: -14px !important; }
  .proof-disclaimer{ font-size: 11px !important; padding: 12px 14px !important; }

  /* Programa em fases */
  .program-phase{
    grid-template-columns: 70px 1fr !important;
    gap: 14px !important; padding: 16px 0 !important;
  }
  .program-phase .phase-marker{
    width: 70px !important; padding: 8px !important;
  }
  .program-phase .phase-marker .num{ font-size: 18px !important; }
  .program-phase .phase-content h4{ font-size: 16px !important; }
  .program-phase .phase-content .desc{ font-size: 13px !important; }

  /* Inclusos */
  .incluso-card{ padding: 14px !important; }
  .incluso-card .incluso-icon{ width: 38px !important; height: 38px !important; }
  .incluso-card .incluso-titulo{ font-size: 14px !important; }
  .incluso-card .incluso-desc{ font-size: 12px !important; }

  /* CTA */
  .cta-frame{ padding: 14px 16px !important; max-width: 100% !important; }
  .cta-frame-text{ font-size: 14px !important; line-height: 1.45 !important; }
  .cta-card{ padding: 18px !important; }
  .cta-card h3{ font-size: 18px !important; }
  .cta-card .desc{ font-size: 13px !important; }
  .cta-card .button{ padding: 14px !important; font-size: 12px !important; }
  .cta-signature .name{ font-size: 18px !important; }
  .cta-signature .meta{ font-size: 10px !important; }

  /* Checklist */
  .checklist-card{ padding: 18px !important; }
  .checklist-item{ gap: 12px !important; padding: 12px 0 !important; }
  .checklist-item .check{ width: 24px; height: 24px; flex-basis: 24px; }
  .checklist-item .text{ font-size: 13px !important; line-height: 1.4 !important; }
  .checklist-progress{ flex-direction: column; align-items: stretch !important; gap: 8px; }

  /* Apêndice exames */
  .technical-appendix .appendix-controls{ flex-direction: column; align-items: stretch; gap: 10px; }
  .technical-appendix .appendix-controls .lead{ font-size: 12px !important; }
  .appendix-toggle-all{ align-self: flex-start; font-size: 9px !important; padding: 6px 10px !important; }
  .exam-group-header{ padding: 12px 14px !important; }
  .exam-group-header h4{ font-size: 14px !important; }
  .exam-group-header .meta{ font-size: 10px !important; gap: 8px; }
  .exam-group-body{ padding: 0 14px !important; }
  .exam-row{
    display: block !important;
    padding: 10px 0 !important;
    font-size: 12px !important;
  }
  .exam-row .e-nome{ font-weight: 600; font-size: 13px !important; }
  .exam-row .e-valor{ font-size: 13px !important; }
  .exam-row .e-status{ font-size: 9px !important; text-align: left !important; }
  .exam-row .e-ref{ font-size: 10px !important; color: var(--muted); margin-top: 2px; }

  /* Doctor objections — uso médico */
  .obj-toolbar{ position: static !important; padding: 12px 0 !important; margin-bottom: 14px; }
  .obj-search{ font-size: 14px !important; padding: 12px 12px 12px 40px !important; }
  .obj-search-icon{ left: 12px; width: 18px; height: 18px; }
  .obj-shortcut{ display: none !important; }
  .obj-cats{ overflow-x: auto; flex-wrap: nowrap; padding-bottom: 4px; gap: 4px; }
  .obj-cat-chip{ flex-shrink: 0; font-size: 10px !important; padding: 4px 10px !important; }
  .doctor-obj-card{ padding: 0 !important; }
  .doctor-obj-card .obj-header{ padding: 12px 14px !important; gap: 10px !important; }
  .doctor-obj-card .obj-cat-tag{ display: none !important; }
  .doctor-obj-card .obj-header h3{ font-size: 14px !important; line-height: 1.3 !important; }
  .doctor-obj-card .obj-toggle{ width: 22px; height: 22px; font-size: 12px; }
  .doctor-obj-card .obj-body{ padding: 0 14px 14px !important; font-size: 12px; }

  /* Modal */
  .send-modal-card{ padding: 20px !important; max-height: 90vh; overflow-y: auto; }
  .send-modal-card h3{ font-size: 17px !important; padding-right: 28px !important; }
  .send-modal-sub{ font-size: 12px !important; }
  .send-field span{ font-size: 10px !important; }
  .send-field input, .send-field textarea{ font-size: 13px !important; padding: 10px 12px !important; }
  .send-actions{ flex-direction: column !important; gap: 8px !important; margin-top: 16px !important; }
  .send-btn-primary, .send-btn-secondary{
    width: 100%; min-width: 0 !important; padding: 12px !important; font-size: 12px !important;
  }
  .send-hint{ font-size: 10px !important; line-height: 1.5 !important; padding-top: 12px !important; }
}

/* Mobile pequeno (≤480px) */
@media(max-width: 480px){
  .progress-step{ font-size: 8px !important; padding: 3px 6px !important; }
  .mode-btn{ font-size: 8px !important; padding: 3px 6px !important; }
  .topbar .logo{ height: 38px; max-width: 130px; }
  .hero-meta-item{ flex: 1 1 100%; }
  h1, .hero-clinical-h1{ font-size: 20px !important; }
  h2{ font-size: 19px !important; }
  .lever-numeric .value{ font-size: 24px !important; }
  .program-phase{ grid-template-columns: 60px 1fr !important; gap: 10px !important; }
  .program-phase .phase-marker{ width: 60px !important; padding: 6px !important; }
  .proof-imgs{ grid-template-columns: 1fr !important; }
}

/* Preferência por reduzir movimento (acessibilidade) */
@media (prefers-reduced-motion: reduce){
  *, *::before, *::after{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  .fade-up{ opacity: 1 !important; transform: none !important; }
}

"""


# ---------------------------------------------------------------------------
# JS — progress nav scroll-spy, accordion, decision checklist, modo apresentação
# ---------------------------------------------------------------------------
JS = r"""
(function(){
  document.body.classList.add('js-enabled');

  // === Progress nav scroll spy ===
  const allSections = document.querySelectorAll('main > section[id]');
  const steps = document.querySelectorAll('.progress-step[data-target]');
  // Só considera seções que estão no progress nav
  const navTargets = new Set(Array.from(steps).map(s => s.dataset.target));
  const trackedSections = Array.from(allSections).filter(s => navTargets.has(s.id));
  function updateActive(){
    if(!trackedSections.length) return;
    const trigger = window.innerHeight * 0.30;  // 30% do viewport
    let active = trackedSections[0].id;
    // Encontra a última seção cujo top já passou do trigger
    for(const sec of trackedSections){
      const r = sec.getBoundingClientRect();
      if(r.top - trigger <= 0) active = sec.id;
      else break;
    }
    steps.forEach(s => {
      s.classList.toggle('active', s.dataset.target === active);
    });
  }
  window.addEventListener('scroll', updateActive, { passive: true });
  updateActive();
  steps.forEach(s => {
    s.addEventListener('click', () => {
      const t = document.getElementById(s.dataset.target);
      if(t) t.scrollIntoView({behavior:'smooth', block:'start'});
    });
  });

  // === Mode switcher (3 modos exclusivos) ===
  const modeButtons = document.querySelectorAll('.mode-btn[data-mode]');
  const modes = ['apresentacao', 'exames', 'objecoes'];
  function setMode(mode){
    modes.forEach(m => document.body.classList.toggle('modo-' + m, m === mode));
    modeButtons.forEach(b => {
      const active = b.dataset.mode === mode;
      b.classList.toggle('active', active);
      b.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    // Scroll suave para topo da seção do modo
    if(mode === 'exames'){
      const t = document.querySelector('#technical-appendix');
      if(t) t.scrollIntoView({behavior:'smooth', block:'start'});
    } else if(mode === 'objecoes'){
      const t = document.querySelector('#doctor-objections');
      if(t) t.scrollIntoView({behavior:'smooth', block:'start'});
    } else {
      window.scrollTo({top:0, behavior:'smooth'});
    }
  }
  modeButtons.forEach(b => b.addEventListener('click', (e) => {
    e.preventDefault();
    setMode(b.dataset.mode);
  }));
  // Default: apresentação
  document.body.classList.add('modo-apresentacao');

  // === Accordion exames ===
  document.querySelectorAll('.exam-group-header').forEach(h => {
    h.addEventListener('click', () => {
      h.parentElement.classList.toggle('open');
    });
  });
  const openAll = document.querySelector('.appendix-toggle-all');
  if(openAll){
    openAll.addEventListener('click', () => {
      const groups = document.querySelectorAll('.exam-group');
      const allOpen = Array.from(groups).every(g => g.classList.contains('open'));
      groups.forEach(g => g.classList.toggle('open', !allOpen));
      openAll.textContent = allOpen ? 'Expandir todos' : 'Recolher todos';
    });
  }

  // === Decision checklist ===
  document.querySelectorAll('.checklist-item').forEach(item => {
    item.addEventListener('click', () => item.classList.toggle('checked'));
  });

  // === Scroll-triggered fade-up ===
  if('IntersectionObserver' in window){
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if(e.isIntersecting){
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    document.querySelectorAll('.fade-up').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.fade-up').forEach(el => el.classList.add('in'));
  }

  // === Severity rings (donut) ===
  document.querySelectorAll('.sev-ring').forEach(ring => {
    const pct = parseFloat(ring.dataset.pct || '0');
    const r = 22, c = 2 * Math.PI * r;
    const offset = c - (Math.min(pct, 100) / 100) * c;
    const fill = ring.querySelector('.ring-fill');
    if(fill){
      fill.setAttribute('stroke-dasharray', c.toFixed(2));
      fill.setAttribute('stroke-dashoffset', c.toFixed(2));
      // Animate after a tick
      requestAnimationFrame(() => {
        fill.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1)';
        fill.setAttribute('stroke-dashoffset', offset.toFixed(2));
      });
    }
  });


  // === Modal "Enviar ao paciente" V2.8 ===
  // Gera HTML versão paciente in-page (clona DOM, limpa) + share/download/WhatsApp
  const sendBtn = document.getElementById('btn-send-paciente');
  const sendModal = document.getElementById('send-modal');
  if(sendBtn && sendModal){
    const sendTel = document.getElementById('send-tel');
    const sendMsg = document.getElementById('send-msg');
    const sendShare = document.getElementById('send-share');
    const sendDownload = document.getElementById('send-download');
    const sendWa = document.getElementById('send-whatsapp');
    const sendCopy = document.getElementById('send-copy');
    const sendClose = sendModal.querySelector('.send-modal-close');
    const sendBackdrop = sendModal.querySelector('.send-modal-backdrop');
    const openModal = () => {
      sendModal.classList.add('is-open');
      sendModal.removeAttribute('hidden');
      document.body.classList.add('modal-locked');
      if(sendTel) setTimeout(() => sendTel.focus(), 100);
    };
    const closeModal = () => {
      sendModal.classList.remove('is-open');
      sendModal.setAttribute('hidden', '');
      document.body.classList.remove('modal-locked');
    };
    sendBtn.addEventListener('click', openModal);
    if(sendClose) sendClose.addEventListener('click', closeModal);
    if(sendBackdrop) sendBackdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
      if(e.key === 'Escape' && sendModal.classList.contains('is-open')) closeModal();
    });

    // Detecta mobile pra escolher fluxo padrão
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if(isMobile && navigator.canShare){
      // No mobile, mostra botão Compartilhar (Web Share API)
      if(sendShare) sendShare.style.display = '';
      if(sendDownload) sendDownload.style.display = 'none';
    } else {
      // Desktop: mostra Download + WhatsApp Web
      if(sendShare) sendShare.style.display = 'none';
      if(sendDownload) sendDownload.style.display = '';
    }

    // Gera HTML versão paciente clonando DOM atual e removendo seções internas
    function buildPacienteHtml(){
      const clone = document.documentElement.cloneNode(true);
      // Remove médica/objeções
      const docObjs = clone.querySelector('#doctor-objections');
      if(docObjs) docObjs.remove();
      // Remove botão Médica do mode-switcher
      const btnMed = clone.querySelector('.mode-btn[data-mode="objecoes"]');
      if(btnMed) btnMed.remove();
      // Remove botão de envio + modal
      const btnSend = clone.querySelector('.topbar-send-btn');
      if(btnSend) btnSend.remove();
      const modal = clone.querySelector('#send-modal');
      if(modal) modal.remove();
      // Reset modo para apresentação
      const body = clone.querySelector('body');
      if(body){
        body.className = 'versao-paciente modo-apresentacao';
      }
      // Marca todos os mode-btn corretamente
      clone.querySelectorAll('.mode-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.mode === 'apresentacao');
        b.setAttribute('aria-selected', b.dataset.mode === 'apresentacao' ? 'true' : 'false');
      });
      return '<!DOCTYPE html>\n' + clone.outerHTML;
    }

    function buildBlob(){
      const html = buildPacienteHtml();
      return new Blob([html], { type: 'text/html;charset=utf-8' });
    }

    function pacienteFilename(){
      // Tenta extrair nome do paciente do title
      const t = document.title || 'apresentacao';
      const slug = t.split('·')[0].trim().toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      return 'apresentacao-' + (slug || 'paciente') + '.html';
    }

    // Botão: Compartilhar (mobile, Web Share API com arquivo)
    if(sendShare){
      sendShare.addEventListener('click', async () => {
        try {
          const blob = buildBlob();
          const file = new File([blob], pacienteFilename(), { type: 'text/html' });
          const msg = sendMsg.value || '';
          if(navigator.canShare && navigator.canShare({ files: [file] })){
            await navigator.share({
              files: [file], text: msg, title: 'Apresentação clínica'
            });
            sendShare.textContent = 'Enviado!';
            setTimeout(() => closeModal(), 800);
          } else {
            alert('Seu navegador não suporta compartilhamento de arquivo. Use Baixar HTML e anexe manualmente.');
          }
        } catch (e) {
          if(e.name !== 'AbortError') alert('Não foi possível compartilhar: ' + e.message);
        }
      });
    }

    // Botão: Baixar HTML (desktop)
    if(sendDownload){
      sendDownload.addEventListener('click', () => {
        const blob = buildBlob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = pacienteFilename();
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1500);
        const original = sendDownload.textContent;
        sendDownload.textContent = 'Baixado ✓';
        setTimeout(() => { sendDownload.textContent = original; }, 1500);
      });
    }

    // Botão: Abrir WhatsApp (com mensagem pré-formatada)
    if(sendWa){
      sendWa.addEventListener('click', () => {
        const tel = (sendTel.value || '').replace(/[^0-9]/g, '');
        const msg = encodeURIComponent(sendMsg.value || '');
        const url = tel ? ('https://wa.me/' + tel + '?text=' + msg) : ('https://wa.me/?text=' + msg);
        window.open(url, '_blank', 'noopener');
      });
    }

    // Botão: Copiar mensagem
    if(sendCopy){
      sendCopy.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(sendMsg.value || '');
          const original = sendCopy.textContent;
          sendCopy.textContent = 'Copiado!';
          setTimeout(() => { sendCopy.textContent = original; }, 1500);
        } catch (e) { alert('Não foi possível copiar. Selecione o texto manualmente.'); }
      });
    }
  }

  // === Painel de objeções: busca + filtro por categoria + accordion ===
  const objSearch = document.querySelector('.obj-search');
  const objSearchClear = document.querySelector('.obj-search-clear');
  const objChips = document.querySelectorAll('.obj-cat-chip');
  const objCards = document.querySelectorAll('.doctor-obj-card');
  const objCounter = document.querySelector('.obj-counter-num');
  const objEmpty = document.querySelector('.obj-empty');
  let activeCat = 'todas';
  let activeQuery = '';

  function applyObjFilter(){
    const q = activeQuery.toLowerCase().trim();
    let visible = 0;
    objCards.forEach(card => {
      const matchCat = activeCat === 'todas' || card.dataset.cat === activeCat;
      const matchQuery = !q || card.dataset.search.includes(q);
      const show = matchCat && matchQuery;
      card.classList.toggle('hidden', !show);
      if(show) visible++;
    });
    if(objCounter) objCounter.textContent = visible;
    if(objEmpty) objEmpty.hidden = visible > 0;
    if(objSearchClear) objSearchClear.classList.toggle('visible', !!q);
  }

  if(objSearch){
    objSearch.addEventListener('input', (e) => {
      activeQuery = e.target.value;
      applyObjFilter();
    });
  }
  if(objSearchClear){
    objSearchClear.addEventListener('click', () => {
      objSearch.value = ''; activeQuery = ''; applyObjFilter(); objSearch.focus();
    });
  }
  objChips.forEach(chip => {
    chip.addEventListener('click', () => {
      objChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeCat = chip.dataset.cat;
      applyObjFilter();
    });
  });

  // Accordion individual
  objCards.forEach(card => {
    const header = card.querySelector('.obj-header');
    if(header){
      header.addEventListener('click', () => card.classList.toggle('open'));
    }
  });

  // Atalhos de teclado
  document.addEventListener('keydown', (e) => {
    if(!document.body.classList.contains('modo-objecoes')) return;
    if(e.key === '/' && document.activeElement !== objSearch){
      e.preventDefault();
      if(objSearch) objSearch.focus();
    } else if(e.key === 'Escape' && document.activeElement === objSearch){
      objSearch.value = ''; activeQuery = ''; applyObjFilter(); objSearch.blur();
    }
  });

  // === Decision checklist progress bar ===
  const checklistItems = document.querySelectorAll('.checklist-item');
  const progressFill = document.querySelector('.checklist-progress-fill');
  const progressText = document.querySelector('.checklist-progress-text');
  function updateProgress(){
    const total = checklistItems.length;
    const checked = document.querySelectorAll('.checklist-item.checked').length;
    const pct = total ? (checked / total) * 100 : 0;
    if(progressFill) progressFill.style.width = pct + '%';
    if(progressText) progressText.textContent = checked + ' de ' + total + ' confirmados';
  }
  checklistItems.forEach(it => it.addEventListener('click', updateProgress));
  updateProgress();

})();
"""


# ---------------------------------------------------------------------------
# Helpers — interpretação clínica para Critical Levers
# ---------------------------------------------------------------------------

# Conexão exame → sintoma sentido pelo paciente (clinical bridge)
EXAM_SYMPTOM_MAP = {
    "HOMA-IR": "fome súbita após refeições, sonolência depois do almoço, dificuldade de manter peso",
    "HOMA-Beta": "oscilação de energia ao longo do dia, vontade frequente de doce",
    "HbA1c": "energia inconsistente, fadiga sem causa aparente, dificuldade de concentração",
    "Glicemia Média": "energia inconsistente, fadiga após carboidratos, dificuldade de manter peso",
    "PCR-us": "recuperação lenta de exercícios, dores articulares difusas, sensação de inflamação",
    "Vitamina D": "imunidade baixa, força reduzida, humor variável, recuperação lenta",
    "Vitamina B12": "cansaço persistente, dificuldade de concentração, energia matinal baixa",
    "Prolactina": "libido reduzida, fadiga, alteração de sono",
    "Testosterona Total": "libido baixa, perda de massa muscular, disposição reduzida",
    "Testosterona Livre": "libido, força e disposição em queda mesmo com testo total normal",
    "Cortisol Basal": "cansaço matinal, dificuldade de relaxar à noite, peso central",
    "Ferritina": "sobrecarga de ferro/inflamação, fadiga, alteração hepática e necessidade de correlação com saturação de transferrina",
    "Ferro": "quando vem alto junto com ferritina e saturação elevadas, reforça hipótese de sobrecarga de ferro a ser revisada pela médica",
    "Índice de Saturação da Transferrina": "saturação elevada fortalece a suspeita de excesso de ferro circulante, especialmente quando ferritina também está alta",
    "Capacidade de Fixação Latente do Ferro": "capacidade baixa sugere menor espaço livre para ligação do ferro, compondo padrão de sobrecarga quando associada a saturação alta",
    "Progesterona": "em homem, valor acima da referência deve ser lido junto ao eixo hormonal completo, uso de medicações/suplementos e marcadores hepáticos/adrenais",
    "Hemácias": "pode se relacionar com capacidade de transporte e disposição.",
    "Hemoglobina": "pode se relacionar com cansaço, recuperação e desempenho.",
    "Hematócrito": "ajuda a compor a leitura do padrão hematológico junto aos demais marcadores.",
    "VCM": "compõe a leitura do padrão hematológico — perfil das hemácias.",
    "HCM": "compõe a leitura do conteúdo de hemoglobina por hemácia.",
    "CHCM": "compõe a leitura da concentração de hemoglobina nas hemácias.",
    "RDW": "indica variabilidade no tamanho das hemácias — pista para o tipo de anemia quando há.",
    "Leucócitos": "termômetro de defesa imune e inflamação aguda quando alterado.",
    "Plaquetas": "marcador de hemostasia e, indiretamente, de inflamação sistêmica.",
}


def _conexao_sintoma(nome_exame):
    return EXAM_SYMPTOM_MAP.get(nome_exame, "compõe o quadro funcional integrado — sua relevância depende da leitura conjunta com os demais marcadores.")


def _questionario_contexto_risco(questionario, nome_exame):
    """Gera uma ponte curta entre exame alterado e respostas do questionário."""
    dados = (questionario or {}).get("pre-consulta", {}).get("dados", {}) if isinstance(questionario, dict) else {}
    if not dados and isinstance(questionario, dict) and "dados" in questionario:
        dados = questionario.get("dados", {})

    def v(k):
        x = dados.get(k)
        return "" if x in (None, "", [], {}) else str(x)

    sono = v("qualidadeSono")
    energia = v("nivelEnergia")
    cansaco = v("cansacoDurante")
    ansiedade = v("spin_p_desafios") or v("spin_s_tempoLutaDetalhe")
    doce = v("consumoDoces")
    med = v("medicamentosAtuais")
    cron = v("doencasCronicas")
    treino = v("atividadeFisica")
    objetivo = v("tresObjetivos")
    alimentacao = " / ".join([x for x in [v("almoco"), v("jantar"), v("alimentacaoFimSemana")] if x])

    eixo_ferro = {"Ferritina", "Ferro", "Índice de Saturação da Transferrina", "Capacidade de Fixação Latente do Ferro"}
    eixo_tireoide = {"TSH", "T3 Livre", "T4 Livre"}
    eixo_hormonal = {"SHBG", "Progesterona", "Testosterona Total", "Testosterona Livre", "Estradiol"}

    if nome_exame in eixo_ferro:
        partes = []
        if cron or med:
            partes.append(f"histórico de {cron or 'condição crônica'} e uso de {med or 'medicação'}")
        if energia or sono or cansaco:
            partes.append(f"energia {energia or 'baixa'}, sono {sono or 'ruim'} e {cansaco or 'cansaço relatado'}")
        if partes:
            return "No seu questionário, " + "; ".join(partes) + ". Nesse contexto, excesso de ferro pode aumentar estresse oxidativo, inflamação e sobrecarga hepático-metabólica, dificultando disposição, emagrecimento seguro e redução de risco cardiovascular."
        return "No seu caso, esse padrão aumenta risco de estresse oxidativo, inflamação e sobrecarga hepático-metabólica se for ignorado ou suplementado no escuro."

    if nome_exame in eixo_tireoide:
        partes = []
        if ansiedade:
            partes.append(f"ansiedade/instabilidade alimentar relatada ({ansiedade})")
        if sono or energia:
            partes.append(f"sono {sono or 'alterado'} e energia {energia or 'baixa'}")
        if treino or objetivo:
            partes.append(f"objetivo de composição corporal com {treino or 'treino'}")
        if partes:
            return "No seu questionário aparecem " + "; ".join(partes) + ". Com tireoide acelerada, o risco é piorar ansiedade, sono, perda de massa magra e carga cardiovascular, mesmo quando a balança parece responder."
        return "Com esse padrão tireoidiano, o risco é acelerar coração, ansiedade, insônia e perda de massa magra se o plano avançar sem investigação médica."

    if nome_exame in eixo_hormonal:
        partes = []
        if energia or sono:
            partes.append(f"energia {energia or 'baixa'} e sono {sono or 'alterado'}")
        if treino or objetivo:
            partes.append(f"meta de força/composição corporal ({objetivo or treino})")
        if partes:
            return "No seu questionário aparecem " + "; ".join(partes) + ". Se esse eixo for ignorado, o risco é manter baixa disposição, pior recuperação, dificuldade de ganhar massa magra e menor adesão ao plano."
        return "Se esse eixo for tratado como número isolado, o risco é corrigir o marcador errado e manter sintomas, baixa recuperação e dificuldade de composição corporal."

    if nome_exame in {"Vitamina B12", "Vitamina D", "Homocisteína", "PCR-us", "Zinco"}:
        partes = []
        if energia or cansaco:
            partes.append(f"energia {energia or 'baixa'} e {cansaco or 'cansaço'}")
        if doce or alimentacao:
            partes.append(f"padrão alimentar com {doce or alimentacao}")
        if partes:
            return "No seu questionário aparecem " + "; ".join(partes) + ". Ignorar esse ponto pode manter inflamação funcional, pior recuperação e mais dificuldade de sustentar rotina alimentar e treino."
        return "Ignorar esse ponto pode manter inflamação funcional, pior recuperação e dificuldade de resposta ao acompanhamento."

    if energia or sono or ansiedade:
        return f"Cruzando com o questionário — energia {energia or 'não informada'}, sono {sono or 'não informado'} e desafio relatado de {ansiedade or 'adesão'} — o risco é manter o ciclo de sintomas e baixa adesão se o ajuste não for acompanhado."
    return "Cruzando com o questionário, o risco é tratar o exame como número isolado e perder a causa prática que mantém o problema ativo."


def _decision_copy(nome_exame, sev="alert", questionario=None):
    """Copy curta: significado, importância e risco contextualizado pelo questionário."""
    mapa = {
        "SHBG": (
            "Sua testosterona total pode parecer boa, mas o SHBG alto prende parte dela.",
            "Menos testosterona livre atuando: energia, força, libido e recuperação podem ficar abaixo do esperado.",
            ""
        ),
        "Progesterona": (
            "Em homem, progesterona acima da referência exige leitura do eixo hormonal completo.",
            "Pode indicar desbalanço hormonal, interferência de medicação/suplemento ou contexto hepático/metabólico.",
            ""
        ),
        "Ferritina": (
            "Ferritina muito alta não é detalhe: pode sinalizar sobrecarga de ferro ou inflamação.",
            "Com ferro e saturação altos, aumenta a suspeita de hemocromatose/sobrecarga de ferro.",
            ""
        ),
        "Ferro": (
            "Ferro alto junto com ferritina alta muda o peso da análise.",
            "Esse padrão pode apontar excesso de ferro circulante, não apenas variação alimentar.",
            ""
        ),
        "Índice de Saturação da Transferrina": (
            "Saturação alta mostra que há muito ferro ocupando a transferrina.",
            "Quando passa de 50% junto com ferritina alta, a suspeita de sobrecarga aumenta.",
            ""
        ),
        "Capacidade de Fixação Latente do Ferro": (
            "Capacidade baixa sugere pouco espaço livre para carregar mais ferro.",
            "Junto com ferro/ferritina altos, reforça padrão de sobrecarga.",
            ""
        ),
        "Vitamina B12": (
            "B12 baixa reduz eficiência neurológica e metabólica.",
            "Pode pesar em cansaço, foco, disposição e resposta ao treino.",
            ""
        ),
        "Vitamina D": (
            "Vitamina D abaixo do alvo funcional reduz margem de saúde.",
            "Pode impactar imunidade, força, humor e recuperação.",
            ""
        ),
        "TSH": (
            "TSH suprimido é sinal de tireoide hiperestimulada ou excesso de hormônio tireoidiano.",
            "Com T3 Livre e T4 Livre altos, o padrão aponta para hipertireoidismo/tireotoxicose até prova em contrário.",
            ""
        ),
        "T4 Livre": (
            "T4 Livre alto confirma excesso de hormônio tireoidiano circulante.",
            "Junto com TSH 0,01 e T3 Livre alto, fecha padrão laboratorial de hipertireoidismo/tireotoxicose.",
            ""
        ),
        "T3 Livre": (
            "T3 Livre muito alto é sinal forte de tireotoxicose ativa.",
            "Pode acelerar coração, ansiedade, perda de massa, tremor, insônia e risco cardiovascular.",
            ""
        ),
    }
    if nome_exame in mapa:
        leitura, impacto, _ = mapa[nome_exame]
        return leitura, impacto, _questionario_contexto_risco(questionario, nome_exame)
    if sev == "crit":
        return (
            "Esse marcador saiu da zona segura e precisa de prioridade.",
            "Ignorar agora pode manter sintomas e tornar a correção mais difícil depois.",
            _questionario_contexto_risco(questionario, nome_exame)
        )
    return (
        "Esse marcador mostra um ponto de ajuste do seu metabolismo.",
        "Ainda dá para corrigir antes que vire um problema maior.",
        _questionario_contexto_risco(questionario, nome_exame)
    )


def _necessidade_solucao(nome_exame, sev="alert", perfil_disc="default"):
    especificas = {
        "Progesterona": "Não é um marcador para tratar isoladamente. Precisa ser conferido pela médica junto com testosterona total/livre, estradiol, SHBG, LH, FSH, prolactina, função hepática e histórico de medicações ou suplementos antes de qualquer conduta.",
        "Ferritina": "Pela elevação importante, precisa entrar como prioridade médica: correlacionar com ferro sérico, saturação de transferrina, capacidade de fixação, TGO/TGP/GGT e histórico familiar para afastar sobrecarga de ferro/hemocromatose.",
        "Ferro": "Como está alto em conjunto com ferritina e saturação de transferrina, não deve ser tratado como achado isolado; precisa de revisão médica dirigida para sobrecarga de ferro.",
        "Índice de Saturação da Transferrina": "Saturação elevada com ferritina alta é um sinal operacional forte para investigação médica de sobrecarga de ferro, não apenas ajuste nutricional genérico.",
        "Capacidade de Fixação Latente do Ferro": "Quando baixa junto com ferro/ferritina altos, reforça a necessidade de leitura médica do metabolismo do ferro como conjunto.",
    }
    if nome_exame in especificas:
        return especificas[nome_exame]
    if perfil_disc == "S":
        mapa = {
            "crit": "Isso pede cuidado estruturado agora, com prioridade clínica e acompanhamento contínuo, para evitar progressão silenciosa e correções mais difíceis depois.",
            "alert": "Isso merece ajuste guiado e acompanhamento em fases, para não ganhar peso clínico com o passar dos meses.",
            "low": "Isso merece ajuste guiado e acompanhamento em fases, para não ganhar peso clínico com o passar dos meses.",
            "attn": "Isso merece ajuste guiado e acompanhamento em fases, para não ganhar peso clínico com o passar dos meses.",
            "ok": "Mesmo adequado hoje, esse marcador precisa ser monitorado para sustentar estabilidade e confirmar resposta ao plano.",
            "normal": "Mesmo adequado hoje, esse marcador precisa ser monitorado para sustentar estabilidade e confirmar resposta ao plano.",
        }
    else:
        mapa = {
            "crit": "Isso pede intervenção acompanhada agora, para reduzir risco de progressão e evitar um plano mais complexo depois.",
            "alert": "Isso justifica correção guiada e monitoramento, antes que o quadro deixe de ser sutil e passe a cobrar mais do organismo.",
            "low": "Isso justifica correção guiada e monitoramento, antes que o quadro deixe de ser sutil e passe a cobrar mais do organismo.",
            "attn": "Isso justifica correção guiada e monitoramento, antes que o quadro deixe de ser sutil e passe a cobrar mais do organismo.",
            "ok": "Mesmo estável, esse ponto serve como base de comparação para medir resposta clínica e preservar resultado.",
            "normal": "Mesmo estável, esse ponto serve como base de comparação para medir resposta clínica e preservar resultado.",
        }
    return mapa.get(sev, mapa.get("alert"))


INTERPRETACAO_LEVERS = {
    # === Glicídico ===
    "Glicose": {
        "interpretacao": "Glicemia de jejum no limite ou acima do alvo funcional.",
        "impacto": "Sinal precoce de desregulação do metabolismo de carboidratos, mesmo antes de sintomas claros.",
        "spin": "Você prefere agir enquanto o quadro ainda é silencioso ou esperar até virar sintoma?",
    },
    "Insulina": {
        "interpretacao": "Hormônio que precisa ser lido em conjunto com glicemia (HOMA-IR) e clínica.",
        "impacto": "Insulina alta com glicemia normal já indica que o pâncreas está trabalhando mais para compensar.",
        "spin": "Faz sentido olhar o esforço do pâncreas, e não só o resultado final no sangue?",
    },
    "HOMA-IR": {
        "interpretacao": "Índice clínico de resistência à insulina.",
        "impacto": "Pode dificultar perda de gordura, favorecer fome e sonolência pós-refeição.",
        "spin": "Isso conversa com a dificuldade que você descreveu de sustentar resultado?",
    },
    "HOMA-Beta": {
        "interpretacao": "Função pancreática em compensação ativa.",
        "impacto": "Indica que o corpo está trabalhando mais para manter a glicemia — janela de intervenção precoce.",
        "spin": "Vale agir nessa janela em que o pâncreas ainda compensa bem?",
    },
    "HbA1c": {
        "interpretacao": "Tendência glicêmica média dos últimos 3 meses, acima do alvo funcional.",
        "impacto": "Sinaliza necessidade de agir antes da progressão metabólica se firmar.",
        "spin": "Quando você imagina esse número 6 meses adiante sem mudança, o que sente?",
    },
    "Glicemia Média": {
        "interpretacao": "Glicose média do trimestre acima do alvo conservador da clínica.",
        "impacto": "Pré-diabetes silenciosa: pode evoluir sem sintomas claros perceptíveis.",
        "spin": "O que costuma te fazer agir: o número, ou só quando o sintoma aparece?",
    },
    "Frutosamina": {
        "interpretacao": "Marcador glicêmico de prazo curto (2-3 semanas).",
        "impacto": "Útil para acompanhar resposta a ajustes recentes no plano.",
        "spin": "Quer um marcador que mostre resposta rápida aos ajustes que faremos?",
    },
    # === Lipídico ===
    "Colesterol Total": {
        "interpretacao": "Carga lipídica total acima da faixa funcional.",
        "impacto": "Compõe a leitura do risco cardiovascular junto a HDL, LDL e ApoB.",
        "spin": "Quer entender o seu colesterol como contexto, e não como número solto?",
    },
    "LDL": {
        "interpretacao": "Fração lipídica diretamente associada a risco cardiovascular.",
        "impacto": "Acima do alvo, contribui silenciosamente para placas vasculares ao longo dos anos.",
        "spin": "Você prefere agir quando o número aponta, ou esperar evento clínico?",
    },
    "HDL": {
        "interpretacao": "Fração protetora do colesterol abaixo do alvo masculino/feminino.",
        "impacto": "HDL baixo reduz a 'capacidade de limpeza' do sistema vascular.",
        "spin": "Faz sentido tratar HDL baixo como sinal funcional, não como detalhe?",
    },
    "VLDL": {
        "interpretacao": "Fração lipídica relacionada a triglicérides e gordura hepática.",
        "impacto": "Quando elevada, sugere alteração metabólica do fígado e do açúcar.",
        "spin": "Você notou peso na digestão, sonolência ou ganho central recente?",
    },
    "Triglicérides": {
        "interpretacao": "Tipicamente sobe com excesso de carboidrato refinado e álcool.",
        "impacto": "Está ligada à resistência à insulina e à gordura hepática.",
        "spin": "Esse número faz sentido com sua rotina alimentar das últimas semanas?",
    },
    "Não-HDL": {
        "interpretacao": "Soma de todas as frações aterogênicas — leitura mais ampla que LDL isolado.",
        "impacto": "Hoje é considerado mais preditivo de risco cardiovascular do que LDL solo.",
        "spin": "Quer trabalhar com o indicador mais preditivo, e não só com o tradicional?",
    },
    "ApoB": {
        "interpretacao": "Conta direta das partículas aterogênicas circulantes.",
        "impacto": "Refina o risco quando LDL e Triglicérides dão leituras divergentes.",
        "spin": "Faz sentido refinar o quadro com ApoB antes de decidir intensidade do plano?",
    },
    "ApoA": {
        "interpretacao": "Apoproteína protetora associada à HDL.",
        "impacto": "Mesmo com HDL aceitável, ApoA baixa reduz a função protetora real.",
        "spin": "Quer enxergar HDL pelo seu efeito funcional, e não só pela quantidade?",
    },
    "Lp(a)": {
        "interpretacao": "Fator genético independente de risco cardiovascular.",
        "impacto": "Mesmo com colesterol controlado, valores altos pedem estratégia diferenciada.",
        "spin": "Faz sentido considerar fatores genéticos no desenho do plano?",
    },
    # === Hepático ===
    "TGO": {
        "interpretacao": "Enzima hepática que também aparece em músculo.",
        "impacto": "Sozinha diz pouco — interpretada com TGP e GGT mostra sobrecarga hepática.",
        "spin": "Quer ler TGO no contexto, e não como número avulso?",
    },
    "TGP": {
        "interpretacao": "Enzima mais específica de fígado.",
        "impacto": "Elevações sugerem sobrecarga hepática gordurosa, medicamentosa ou alimentar.",
        "spin": "Você associa esse número a algum hábito atual que podemos rever?",
    },
    "GGT": {
        "interpretacao": "Marcador sensível de sobrecarga hepática (álcool, gordura, medicamentos).",
        "impacto": "Sobe antes do TGP — sinal precoce de fígado pedindo alívio.",
        "spin": "GGT alta combina com cansaço pela manhã ou má digestão que você sente?",
    },
    "Fosfatase Alcalina": {
        "interpretacao": "Enzima hepática/óssea — leitura depende do contexto clínico.",
        "impacto": "Útil quando há suspeita de colestase ou metabolismo ósseo alterado.",
        "spin": "Vale interpretar essa enzima junto com cálcio, PTH e vit. D?",
    },
    "Bilirrubina": {
        "interpretacao": "Resíduo da degradação da hemoglobina.",
        "impacto": "Discretos aumentos pedem leitura com TGO/TGP/GGT antes de qualquer conclusão.",
        "spin": "Quer ler bilirrubina dentro do quadro hepático completo?",
    },
    # === Renal ===
    "Ureia": {
        "interpretacao": "Indicador de função renal e de ingestão proteica.",
        "impacto": "Pode oscilar com hidratação e dieta — leitura conjunta evita conclusão precipitada.",
        "spin": "Sua hidratação dos últimos dias confere com esse valor?",
    },
    "Creatinina": {
        "interpretacao": "Reflete filtração glomerular e massa muscular.",
        "impacto": "Em homens treinados pode estar discretamente elevada sem patologia.",
        "spin": "Vale calcular sua taxa de filtração ajustada antes de qualquer alarme?",
    },
    "Ácido Úrico": {
        "interpretacao": "Associado a metabolismo de purinas e função renal.",
        "impacto": "Valores altos pedem atenção a dor articular, álcool e função renal.",
        "spin": "Você notou episódios de dor articular ou inchaço em pés/joelhos?",
    },
    # === Tireoide ===
    "TSH": {
        "interpretacao": "TSH suprimido: a hipófise está freando a tireoide porque há excesso de sinal tireoidiano circulante.",
        "impacto": "Com T3 Livre e T4 Livre altos, o padrão laboratorial aponta para hipertireoidismo/tireotoxicose até prova em contrário.",
        "spin": "Decisão: prioridade médica para investigar a causa e o risco cardiovascular.",
    },
    "T4 Livre": {
        "interpretacao": "T4 Livre alto: excesso de hormônio tireoidiano circulante.",
        "impacto": "Junto com TSH 0,01 e T3 Livre alto, reforça hipertireoidismo/tireotoxicose.",
        "spin": "Decisão: não avançar como se fosse apenas metabolismo acelerado; precisa investigação médica.",
    },
    "T3 Livre": {
        "interpretacao": "T3 Livre muito alto: excesso da forma ativa do hormônio tireoidiano.",
        "impacto": "Pode aumentar risco de taquicardia, ansiedade, tremor, insônia, perda de massa e sobrecarga cardiovascular.",
        "spin": "Decisão: avaliação médica dirigida com prioridade.",
    },
    "Anti-TPO": {
        "interpretacao": "Anticorpo que indica processo autoimune da tireoide.",
        "impacto": "Quando positivo, muda a estratégia de acompanhamento mesmo sem hipotireoidismo.",
        "spin": "Quer ajustar o plano considerando autoimunidade tireoidiana?",
    },
    # === Hormonal ===
    "Testosterona Total": {
        "interpretacao": "Andrógeno principal abaixo do alvo funcional masculino.",
        "impacto": "Pode afetar libido, composição corporal, disposição e recuperação.",
        "spin": "Quais desses sintomas você reconhece no seu dia a dia?",
    },
    "Testosterona Livre": {
        "interpretacao": "Fração biodisponível — a que de fato age nos tecidos.",
        "impacto": "Pode estar baixa mesmo com testo total normal, explicando sintomas reais.",
        "spin": "Faz sentido olhar o quadro hormonal completo, e não um número isolado?",
    },
    "Testo Biodisponível": {
        "interpretacao": "Soma da testo livre + ligada à albumina (a que de fato circula útil).",
        "impacto": "Cruzar com SHBG e clínica refina muito a leitura andrógena.",
        "spin": "Vale refinar a leitura andrógena com biodisponível e SHBG?",
    },
    "Estradiol": {
        "interpretacao": "Estrogênio principal — em homens entra na leitura junto com testo.",
        "impacto": "Equilíbrio testo↔estradiol importa para libido, gordura central e humor.",
        "spin": "Quer trabalhar o eixo hormonal como conjunto, não como hormônios isolados?",
    },
    "Progesterona": {
        "interpretacao": "Em homem, progesterona acima da referência não fecha diagnóstico sozinha, mas é um achado que merece leitura dirigida do eixo hormonal.",
        "impacto": "O valor precisa ser correlacionado com testosterona total/livre, estradiol, SHBG, LH/FSH, prolactina, fígado e uso de medicações ou suplementos; pode representar desbalanço do eixo esteroidogênico, interferência laboratorial ou contexto metabólico específico.",
        "spin": "Esse ponto conversa com sua energia baixa, sono ruim ou uso atual de medicamentos/suplementos?",
    },
    "FSH": {
        "interpretacao": "Hormônio do eixo central reprodutivo.",
        "impacto": "Quando alto, sinaliza compensação para baixa produção gonadal.",
        "spin": "Faz sentido investigar se há sinal de compensação central?",
    },
    "LH": {
        "interpretacao": "Hormônio do eixo central que comanda produção de testo.",
        "impacto": "Junto com FSH, distingue causa central de causa periférica.",
        "spin": "Quer entender a origem do quadro hormonal antes de tratar?",
    },
    "Prolactina": {
        "interpretacao": "Hormônio cuja elevação merece interpretação clínica cuidadosa.",
        "impacto": "Pode demandar investigação adicional, correlação com sintomas e monitoramento.",
        "spin": "Você associa libido reduzida ou cansaço aos últimos meses?",
    },
    "SHBG": {
        "interpretacao": "Proteína que carrega hormônios sexuais — afeta a fração 'livre' real.",
        "impacto": "SHBG alta reduz testo livre, mesmo com testo total normal.",
        "spin": "Quer enxergar SHBG como parte da leitura hormonal, e não como detalhe?",
    },
    "DHEA-S": {
        "interpretacao": "Andrógeno adrenal que cai naturalmente com a idade.",
        "impacto": "Niveis baixos podem se associar a fadiga, libido e perda de força.",
        "spin": "Esses sintomas combinam com o que você tem sentido?",
    },
    # === Inflamatórios ===
    "PCR-us": {
        "interpretacao": "Marcador sensível de inflamação de baixo grau.",
        "impacto": "Pode interferir em recuperação, dores difusas, energia e risco cardiometabólico.",
        "spin": "Você percebe recuperação lenta de exercícios ou dores fora do esperado?",
    },
    "Homocisteína": {
        "interpretacao": "Aminoácido associado a risco cardiovascular e neurológico quando alto.",
        "impacto": "Costuma responder a B12, B6, B9 e estilo de vida — pede leitura conjunta.",
        "spin": "Vale corrigir esse marcador antes que ele se torne fator de risco maduro?",
    },
    "VHS": {
        "interpretacao": "Marcador inespecífico de inflamação sistêmica.",
        "impacto": "Lido junto a PCR-us para ampliar a leitura inflamatória.",
        "spin": "Quer ler inflamação por mais de uma janela, não só por PCR?",
    },
    # === Vitaminas / Minerais ===
    "Vitamina D": {
        "interpretacao": "Hormônio-vitamina abaixo do alvo funcional adotado pela clínica.",
        "impacto": "Pode impactar imunidade, força, humor, recuperação e saúde óssea.",
        "spin": "Você reconhece imunidade mais frágil ou recuperação devagar nos últimos meses?",
    },
    "Vitamina B12": {
        "interpretacao": "Cofator essencial para função neurológica, energia e produção de neurotransmissores.",
        "impacto": "Mesmo dentro da faixa laboratorial, valores baixos comprometem performance funcional.",
        "spin": "Quer corrigir essa base antes de pensar em performance ou suplementação avulsa?",
    },
    "Ácido Fólico": {
        "interpretacao": "Cofator do metabolismo da homocisteína e síntese de DNA.",
        "impacto": "Trabalha em conjunto com B12 e B6 — reposição isolada raramente resolve.",
        "spin": "Faz sentido ajustar B-vitaminas em conjunto, e não isoladamente?",
    },
    "Zinco": {
        "interpretacao": "Mineral envolvido em imunidade, testosterona e cicatrização.",
        "impacto": "Quando baixo, costuma se conectar a queda de imunidade e libido.",
        "spin": "Você notou queda de imunidade ou cicatrização lenta recentemente?",
    },
    "Ferro": {
        "interpretacao": "Ferro sérico alto; quando vem junto com ferritina e saturação elevadas, muda o nível de alerta.",
        "impacto": "O ponto não é falta de ferro — é possível excesso circulante/sobrecarga, que exige leitura médica dirigida.",
        "spin": "Antes de qualquer suplemento, precisamos entender se há sobrecarga de ferro.",
    },
    "Ferritina": {
        "interpretacao": "Ferritina muito alta não deve ser lida como 'boa reserva'. Pode sinalizar sobrecarga de ferro, inflamação ou sofrimento hepático/metabólico.",
        "impacto": "Com ferro e saturação de transferrina altos, a prioridade é afastar hemocromatose/sobrecarga de ferro — não tratar como cansaço por deficiência.",
        "spin": "Decisão: investigar a causa da ferritina alta com prioridade médica.",
    },
    "Magnésio": {
        "interpretacao": "Mineral envolvido em sono, contração muscular e produção de energia.",
        "impacto": "Discreta queda já se conecta a câimbra, sono ruim e fadiga.",
        "spin": "Você nota câimbras, sono leve ou tensão muscular sem causa clara?",
    },
    "Cálcio": {
        "interpretacao": "Mineral lido junto com PTH e vit. D para entender o eixo ósseo.",
        "impacto": "Cálcio sérico isolado diz pouco — o eixo é o que importa.",
        "spin": "Vale interpretar cálcio no eixo PTH-vit.D, não como número solto?",
    },
    "Sódio": {
        "interpretacao": "Eletrólito principal — variações tipicamente conectadas a hidratação.",
        "impacto": "Alterações pequenas raramente são clinicamente relevantes em pessoas saudáveis.",
        "spin": "Você consegue pontuar como anda sua hidratação no dia a dia?",
    },
    "Potássio": {
        "interpretacao": "Eletrólito sensível a hidratação, dieta e função renal.",
        "impacto": "Variações pequenas são comuns; alterações maiores pedem investigação.",
        "spin": "Vale revisar esse valor com hidratação e dieta da semana?",
    },
    "PTH": {
        "interpretacao": "Hormônio paratireoidiano — comandante do eixo cálcio/vit.D.",
        "impacto": "Lido com cálcio e vit.D explica saúde óssea e absorção real.",
        "spin": "Quer entender saúde óssea pelo eixo, não pelo cálcio isolado?",
    },
    # === Adrenal ===
    "Cortisol": {
        "interpretacao": "Hormônio do estresse — leitura de coleta matinal é o padrão.",
        "impacto": "Padrão alterado afeta sono, energia matinal, peso e composição corporal.",
        "spin": "Você nota cansaço logo cedo ou dificuldade de relaxar à noite?",
    },
    "Cortisol Basal": {
        "interpretacao": "Coleta padrão matinal — referência funcional do eixo adrenal.",
        "impacto": "Padrão alterado afeta sono, energia matinal, peso e composição corporal.",
        "spin": "Sua disposição matinal combina com o que esse número sugere?",
    },
    "IGF-1": {
        "interpretacao": "Marcador funcional do eixo de crescimento e recuperação.",
        "impacto": "Reflete performance anabólica geral; varia naturalmente com idade.",
        "spin": "Quer acompanhar capacidade anabólica como parte da estratégia?",
    },
    # === Hemograma ===
    "Hemácias": {
        "interpretacao": "Conta de células vermelhas circulantes.",
        "impacto": "Compõe a leitura da capacidade de transporte de oxigênio e disposição.",
        "spin": "Você nota fôlego curto ou disposição abaixo do normal em atividades simples?",
    },
    "Hemoglobina": {
        "interpretacao": "Proteína responsável pelo transporte de oxigênio.",
        "impacto": "Liga-se diretamente a cansaço, recuperação de exercícios e desempenho.",
        "spin": "Você associa cansaço atual a esforços que antes fazia sem dificuldade?",
    },
    "Hematócrito": {
        "interpretacao": "Porcentagem volumétrica das células vermelhas no sangue.",
        "impacto": "Compõe a leitura do padrão hematológico junto aos demais marcadores.",
        "spin": "Faz sentido ler o hemograma como conjunto, e não como números soltos?",
    },
    "VCM": {
        "interpretacao": "Tamanho médio das hemácias.",
        "impacto": "Pista importante quando há suspeita de deficiências (B12, ferro, fólico).",
        "spin": "Vale cruzar VCM com ferritina e B12 antes de qualquer conclusão?",
    },
    "HCM": {
        "interpretacao": "Conteúdo médio de hemoglobina por hemácia.",
        "impacto": "Compõe a leitura do tipo de eventual anemia, quando ela existe.",
        "spin": "Quer ler HCM dentro do quadro hematológico completo?",
    },
    "CHCM": {
        "interpretacao": "Concentração de hemoglobina nas hemácias.",
        "impacto": "Refina ainda mais a tipagem hematológica.",
        "spin": "Faz sentido olhar para o conjunto das frações eritrocitárias?",
    },
    "RDW": {
        "interpretacao": "Variabilidade do tamanho das hemácias.",
        "impacto": "Pista precoce para deficiências antes da anemia se estabelecer.",
        "spin": "Vale agir em sinais precoces, antes do hemograma virar anemia?",
    },
    "Leucócitos": {
        "interpretacao": "Termômetro de defesa imune e inflamação aguda.",
        "impacto": "Variações pedem leitura junto aos diferenciais e PCR-us.",
        "spin": "Você passou por infecções recentes, estresse ou alergias?",
    },
    "Plaquetas": {
        "interpretacao": "Marcador de hemostasia e, indiretamente, de inflamação sistêmica.",
        "impacto": "Variações pequenas dentro da faixa raramente alteram conduta.",
        "spin": "Quer entender plaquetas dentro do quadro inflamatório global?",
    },
}

DEFAULT_INTERP = {
    "interpretacao": "Marcador fora do alvo funcional adotado pela clínica.",
    "impacto": "Merece interpretação clínica conjunta com sintomas e demais marcadores.",
    "spin": "Vale incluir esse marcador na leitura integrada, em vez de tratar como detalhe?",
}


def _ranking_severidade(ex):
    rank = {"crit": 0, "alert": 1, "low": 1, "attn": 2, "ok": 4, "normal": 4}
    # Prioridade clínica explícita: padrões que mudam decisão não podem sumir da V10 por ordem de extração.
    prioridade_nome = {
        "TSH": -30,
        "T4 Livre": -29,
        "T3 Livre": -28,
        "Ferritina": -20,
        "Ferro": -19,
        "Índice de Saturação da Transferrina": -18,
        "Capacidade de Fixação Latente do Ferro": -17,
        "SHBG": -10,
        "Progesterona": -9,
    }
    return (rank.get(ex.get("status", "normal"), 9), prioridade_nome.get(ex.get("nome"), 0))


def _selecionar_critical_levers(exames, max_levers=7):
    """Seleciona alavancas críticas que mudam decisão clínica; não omite eixo tireoidiano/ferro."""
    ranked = sorted(exames, key=_ranking_severidade)
    levers = [e for e in ranked if e.get("status") in ("crit", "alert", "low")][:max_levers]
    return levers



# === Premium visual helpers ===

ICONS = {
    "diagnosis": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
    "mirror":    '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 9h8M8 13h6M8 17h4"/></svg>',
    "levers":    '<svg viewBox="0 0 24 24"><path d="M3 12h4l3-9 4 18 3-9h4"/></svg>',
    "spin":      '<svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 1-15 6.7L3 16m0 5v-5h5"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8m0-5v5h-5"/></svg>',
    "machine":   '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
    "proof":     '<svg viewBox="0 0 24 24"><path d="M12 2l3 7 7 .5-5.5 4.5 2 7-6.5-4-6.5 4 2-7L2 9.5 9 9z"/></svg>',
    "program":   '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    "objection": '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M12 7v5M12 16h.01"/></svg>',
    "checklist": '<svg viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    "cta":       '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
    "appendix":  '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>',
}


def _icon(key):
    """Section icon SVG."""
    svg = ICONS.get(key, "")
    if not svg:
        return ""
    return f'<span class="section-icon">{svg}</span>'


def _parse_value(s):
    """Parse string com vírgula BR → float."""
    if s is None: return None
    try:
        s = str(s).strip().replace(",", ".")
        # Remove unidades concatenadas
        m = re.match(r"^(-?\d+\.?\d*)", s)
        if m: return float(m.group(1))
    except (ValueError, TypeError): pass
    return None


def _parse_ref_range(ref_str):
    """Extrai (min, max) de string de referência. Retorna (None, None) se não conseguir."""
    if not ref_str: return None, None
    s = str(ref_str).strip().replace(",", ".")
    # Padrão "X a Y"
    m = re.search(r"(-?\d+\.?\d*)\s*[aàÀA]\s*(-?\d+\.?\d*)", s)
    if m: return float(m.group(1)), float(m.group(2))
    # Padrão "<Y" ou "≤Y"
    m = re.search(r"[<≤]\s*(-?\d+\.?\d*)", s)
    if m: return None, float(m.group(1))
    # Padrão ">X" ou "≥X"
    m = re.search(r"[>≥]\s*(-?\d+\.?\d*)", s)
    if m: return float(m.group(1)), None
    return None, None


def _severity_pct(valor_f, ref_min, ref_max):
    """Calcula % de desvio para o severity ring (0-100)."""
    if valor_f is None: return 0
    if ref_max is not None and valor_f > ref_max:
        # quanto acima
        if ref_max == 0: return 100
        return min(100, ((valor_f - ref_max) / ref_max) * 100)
    if ref_min is not None and valor_f < ref_min:
        if ref_min == 0: return 100
        return min(100, ((ref_min - valor_f) / ref_min) * 100)
    return 0


def render_sev_ring(valor, ref_str, sev):
    """Donut ring mostrando % de desvio. Retorna SVG inline."""
    valor_f = _parse_value(valor)
    rmin, rmax = _parse_ref_range(ref_str)
    pct = _severity_pct(valor_f, rmin, rmax)
    label = f"+{int(pct)}%" if pct > 5 else "—"
    return (f'<div class="sev-ring" data-pct="{pct:.0f}" title="Distância do alvo funcional">'
            f'<svg viewBox="0 0 56 56">'
            f'<circle cx="28" cy="28" r="22" class="ring-track"/>'
            f'<circle cx="28" cy="28" r="22" class="ring-fill"/>'
            f'</svg>'
            f'<span class="ring-label">{label}</span></div>')


def render_sparkline(valor, ref_str, sev):
    """Sparkline horizontal mostrando valor vs faixa de referência."""
    valor_f = _parse_value(valor)
    rmin, rmax = _parse_ref_range(ref_str)
    if valor_f is None:
        return ""
    # Define escala visual: 0 a 1.5x do max OU 0 a max+50% se só rmax, etc
    if rmin is not None and rmax is not None:
        range_min = max(0, rmin - (rmax - rmin) * 0.5)
        range_max = rmax + (rmax - rmin) * 0.5
    elif rmax is not None:
        range_min = 0
        range_max = rmax * 1.5
    elif rmin is not None:
        range_min = 0
        range_max = rmin * 2
    else:
        return ""
    range_max = max(range_max, valor_f * 1.1)
    range_min = min(range_min, valor_f * 0.9 if valor_f < range_min else range_min)
    if range_max - range_min <= 0: return ""

    def x(v):
        return ((v - range_min) / (range_max - range_min)) * 280 + 4

    # SVG: 288 wide, 36 high
    track = f'<rect x="0" y="14" width="288" height="8" rx="4" class="spark-track"/>'
    range_rect = ""
    if rmin is not None and rmax is not None:
        rx, rw = x(rmin), x(rmax) - x(rmin)
        range_rect = f'<rect x="{rx:.0f}" y="14" width="{rw:.0f}" height="8" rx="4" class="spark-range"/>'
    elif rmax is not None:
        range_rect = f'<rect x="0" y="14" width="{x(rmax):.0f}" height="8" rx="4" class="spark-range"/>'
    elif rmin is not None:
        range_rect = f'<rect x="{x(rmin):.0f}" y="14" width="{288 - x(rmin):.0f}" height="8" rx="4" class="spark-range"/>'

    # Marker
    marker_cls = sev if sev in ("crit", "alert", "low") else ""
    marker = f'<circle cx="{x(valor_f):.0f}" cy="18" r="6" class="spark-marker {marker_cls}"/>'
    # Tick labels
    label_min = f'<text x="0" y="34" class="spark-label">{_fmt_axis(range_min)}</text>'
    label_max = f'<text x="288" y="34" class="spark-label" text-anchor="end">{_fmt_axis(range_max)}</text>'
    label_val = f'<text x="{x(valor_f):.0f}" y="10" class="spark-label" text-anchor="middle" style="fill:var(--ink);font-weight:600">{valor}</text>'

    return (f'<div class="lever-sparkline">'
            f'<div class="sparkline-label">Onde seu valor está na faixa</div>'
            f'<svg viewBox="0 0 288 36" preserveAspectRatio="xMidYMid meet">'
            f'{track}{range_rect}{marker}{label_min}{label_max}{label_val}'
            f'</svg></div>')


def _fmt_axis(n):
    if n is None: return ""
    if abs(n) >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    if abs(n - int(n)) < 0.01:
        return str(int(n))
    return f"{n:.1f}"


def _normalizar_unidade(u):
    """Padroniza unidades para apresentacao premium."""
    if not u: return ""
    s = str(u).strip()
    # Substitui chars ASCII por unicode tipograficos
    s = s.replace("milhoes/mm3", "milhões/mm³")
    s = s.replace("milhoes/mm", "milhões/mm")
    s = s.replace("nanog/mL", "ng/mL")
    s = s.replace("nanog/ml", "ng/mL")
    s = s.replace("/mm3", "/mm³")
    s = s.replace("u3", "ug/dL").replace("ug/dL", "µg/dL") if "u3" in s else s
    s = s.replace("ug/dL", "µg/dL")
    s = s.replace("ug/dl", "µg/dL")
    s = s.replace("mcg/dL", "µg/dL")
    s = s.replace("uUI/mL", "µUI/mL")
    s = s.replace("uIU/mL", "µUI/mL")
    s = s.replace("umol/L", "µmol/L")
    s = s.replace("ug/mL", "µg/mL")
    return s


def _normalizar_valor(v):
    """Padroniza valor numerico com virgula decimal BR."""
    if v is None or v == "":
        return "—"
    s = str(v).strip()
    # Se eh numero com ponto decimal, troca por virgula
    import re as _re
    if _re.match(r"^-?\d+\.\d+$", s):
        s = s.replace(".", ",")
    return s


def _normalizar_ref(r):
    """Padroniza referencia com virgula decimal BR e unicode."""
    if not r:
        return "—"
    s = str(r).strip()
    # Substitui unidades dentro da ref tambem
    s = _normalizar_unidade(s)
    # Trocar pontos decimais por virgulas em padroes "X.YY a Z.WW"
    import re as _re
    s = _re.sub(r"(\d+)\.(\d+)", lambda m: f"{m.group(1)},{m.group(2)}", s)
    return s


def _process_exames(raw):
    """Normaliza lista de exames para o formato interno."""
    out = []
    for ex in (raw or []):
        if not isinstance(ex, dict):
            continue
        nome = ex.get("nome") or ex.get("name") or ""
        if not nome:
            continue
        out.append({
            "nome": nome,
            "valor": _normalizar_valor(ex.get("valor") or "—"),
            "unit": _normalizar_unidade(ex.get("unit") or ex.get("unidade") or ""),
            "ref": _normalizar_ref(ex.get("ref") or ex.get("referencia") or "—"),
            "status": (ex.get("status") or "normal").lower(),
            "grupo": ex.get("grupo") or _infer_grupo(nome),
        })
    return out


GRUPOS_DEF = [
    ("hemograma", "Hemograma e Coagulação"),
    ("glicidico", "Perfil Glicídico"),
    ("lipidico", "Perfil Lipídico"),
    ("hepatico", "Função Hepática"),
    ("renal", "Função Renal"),
    ("tireoide", "Tireoide"),
    ("hormonal", "Hormonal Sexual"),
    ("inflamatorio", "Marcadores Inflamatórios"),
    ("vitaminas", "Vitaminas e Minerais"),
    ("adrenal", "Função Adrenal e Outros"),
]

GRUPO_KEYWORDS = {
    "hemograma": ["hemácia", "hemoglobina", "hematócrito", "leucócito", "plaqueta", "vcm", "hcm", "chcm", "rdw",
                   "linfócito", "neutrófilo", "monócito", "basófilo", "eosinófilo", "bastonete", "segmentado"],
    "glicidico": ["glicose", "insulina", "homa", "hba1c", "frutosamina", "glicemia"],
    "lipidico": ["colesterol", "hdl", "ldl", "vldl", "triglicéride", "apo", "lp(a)", "não-hdl"],
    "hepatico": ["tgo", "tgp", "ggt", "fosfatase", "bilirrubina", "ast", "alt"],
    "renal": ["ureia", "creatinina", "ácido úrico"],
    "tireoide": ["tsh", "t4", "t3", "anti-tpo"],
    "hormonal": ["testosterona", "estradiol", "progesterona", "fsh", "lh", "prolactina", "shbg", "dhea"],
    "inflamatorio": ["pcr", "homocisteína", "vhs"],
    "vitaminas": ["vitamina", "ferro", "ferritina", "magnésio", "cálcio", "sódio", "potássio", "zinco", "pth", "fólico"],
    "adrenal": ["cortisol", "igf"],
}


def _infer_grupo(nome):
    n = nome.lower()
    for gid, kws in GRUPO_KEYWORDS.items():
        for kw in kws:
            if kw in n:
                return gid
    return "outros"


# ---------------------------------------------------------------------------
# Section render functions
# ---------------------------------------------------------------------------
def render_topbar(logo_b64, versao_paciente=False):
    btn_send = ""
    if not versao_paciente:
        btn_send = (
            '<button class="topbar-send-btn" id="btn-send-paciente" aria-label="Enviar ao paciente">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9'
            'L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6A8.4 8.4 0 0 1 12.5 3 '
            '8.5 8.5 0 0 1 21 11.5z"/></svg>'
            '<span class="lbl">Enviar ao paciente</span>'
            '</button>'
        )
    return f"""
<header class="topbar">
  <div class="topbar-inner">
    <a href="#hero" aria-label="Voltar ao início" style="line-height:0;"><img src="{logo_b64}" alt="Instituto Vital Slim" class="logo"></a>
    <div class="topbar-right">
      <div class="doctor-tag">
        <span class="name">Dra. Daniely Freitas</span>
        CRM-BA 27.588 · Médica do Estilo de Vida
      </div>
      {btn_send}
    </div>
  </div>
</header>
"""


def render_progress_nav(versao_paciente=False):
    steps = [
        ("executive-diagnosis", "1 · Diagnóstico"),
        ("patient-mirror", "2 · Seu caso"),
        ("critical-levers", "3 · Alavancas"),
        ("leitura-integrada", "4 · Leitura clínica"),
        ("ivs-machine", "5 · Acompanhamento"),
        ("decision-checklist", "6 · Decisão"),
    ]
    items = "".join(
        f'<a class="progress-step" data-target="{sid}" href="#{sid}">{safe_html(label)}</a>'
        for sid, label in steps
    )
    btn_medica = ""
    if not versao_paciente:
        btn_medica = (
            '<a class="mode-btn" data-mode="objecoes" href="#doctor-objections" role="tab" '
            'aria-selected="false">Médica</a>'
        )
    return f"""
<nav class="progress-nav" aria-label="Navegação da apresentação">
  <div class="progress-nav-inner">
    {items}
    <div class="mode-switcher" role="tablist" aria-label="Modo de visualização">
      <a class="mode-btn active" data-mode="apresentacao" href="#hero" role="tab" aria-selected="true">Apresentação</a>
      <a class="mode-btn" data-mode="exames" href="#technical-appendix" role="tab" aria-selected="false">Exames</a>
      {btn_medica}
    </div>
  </div>
</nav>
"""


def render_hero(paciente, dra_b64="", perfil_disc="default"):
    nome = safe_html(paciente.get("nome", "Paciente"))
    primeiro = nome.split()[0] if nome else "Paciente"
    idade = paciente.get("idade") or calcular_idade(paciente.get("dataNascimento")) or "—"
    data_consulta = paciente.get("data_consulta") or date.today().strftime("%d.%m.%Y")
    foto_html = (
        f'<div class="hero-photo fade-up">'
        f'<img src="{dra_b64}" alt="Dra. Daniely Freitas">'
        f'<div class="hero-photo-caption"><strong>Dra. Daniely Freitas</strong>CRM-BA 27.588 · Médica do Estilo de Vida</div>'
        f'</div>'
    ) if dra_b64 else ''
    return f"""
<section id="hero" class="section hero-clinical-document">
  <div class="wrap">
    <div class="hero-meta-bar">
      <div class="hero-meta-item">Paciente<strong>{nome}</strong></div>
      <div class="hero-meta-item">Idade<strong>{idade} anos</strong></div>
      <div class="hero-meta-item">Consulta<strong>{safe_html(data_consulta)}</strong></div>
      <div class="hero-meta-item">Médica<strong>Dra. Daniely Freitas</strong></div>
      <div class="hero-meta-item">CRM<strong>BA 27.588</strong></div>
    </div>
    <div class="hero-grid">
      <div class="hero-text">
        <h1 class="hero-clinical-h1">{_t_disc("hero_h1", perfil_disc, primeiro=primeiro)}</h1>
      </div>
      {foto_html}
    </div>
  </div>
</section>
"""


def render_executive_diagnosis(paciente, levers, perfil_disc="default"):
    primeiro = safe_html(paciente.get("nome", "Paciente").split()[0])
    # Gera 3 cards: o que está acontecendo / onde aparece / por que muda estratégia
    sistemas_afetados = set()
    for lv in levers:
        sistemas_afetados.add(lv.get("grupo", "outros"))
    sistemas_label = {
        "glicidico": "metabolismo glicêmico", "lipidico": "perfil lipídico",
        "hormonal": "eixo hormonal", "tireoide": "tireoide",
        "inflamatorio": "inflamação sistêmica", "vitaminas": "micronutrientes",
        "adrenal": "eixo adrenal", "hepatico": "função hepática",
        "renal": "função renal", "hemograma": "hemograma",
    }
    sistemas_str = ", ".join(sorted({sistemas_label.get(s, s) for s in sistemas_afetados})) or "múltiplos sistemas"

    # Onde aparece: lista as alavancas
    levers_html = ""
    for lv in levers:
        sev_class = "red" if lv["status"] == "crit" else "amber"
        levers_html += (
            f'<span class="tag" style="background:#f3ead1;color:var(--ink);'
            f'display:inline-block;padding:4px 10px;border-radius:6px;margin:2px 4px 2px 0;'
            f'font-size:12px;font-weight:600;">'
            f'{safe_html(lv["nome"])} {safe_html(lv["valor"])}{safe_html(lv["unit"])}</span>'
        )

    return f"""
<section id="executive-diagnosis" class="section executive-diagnosis">
  <div class="wrap">
    <h2>Diagnóstico executivo do caso</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">{_t_disc("diag_lead", perfil_disc)}</p>
    <div class="tese-clinica fade-up">
      <span class="tese-tag">Tese clínica do caso</span>
      <p class="tese-texto">{_t_disc("tese_clinica", perfil_disc)}</p>
    </div>
    <div class="diag-grid diag-grid-2col">
      <div class="diag-card fade-up">
        <h4>O que está acontecendo</h4>
        <p class="body-text">No seu caso, {primeiro}, o ponto principal não é peso ou estética. Há sinais simultâneos em <strong>{sistemas_str}</strong> — quando tratados isoladamente, tendem a produzir resultado pouco previsível.</p>
      </div>
      <div class="diag-card fade-up">
        <h4>Onde aparece nos exames</h4>
        <div style="margin-top:var(--s-3)">{levers_html}</div>
      </div>
    </div>
    <div class="diag-recomendacao">
      {_t_disc("diag_recomendacao", perfil_disc)}
    </div>
  </div>
</section>
"""


def _q_field(label, value, sub="", feature=False):
    cls = "mirror-card feature" if feature else "mirror-card"
    if not value or value == "—" or value == "":
        val_html = '<div class="value empty">não informado · preencher antes da consulta</div>'
    else:
        val_html = f'<div class="value">{safe_html(value)}</div>'
    sub_html = f'<div class="sub">{safe_html(sub)}</div>' if sub else ""
    return f'<div class="{cls}"><div class="label">{safe_html(label)}</div>{val_html}{sub_html}</div>'


def render_patient_mirror(paciente, questionario):
    dados = (questionario or {}).get("pre-consulta", {}).get("dados", {}) if questionario else {}
    if not dados and isinstance(questionario, dict) and "dados" in questionario:
        dados = questionario["dados"]

    def val(*keys):
        for k in keys:
            v = dados.get(k)
            if v not in (None, "", [], {}):
                if isinstance(v, list):
                    return "; ".join(str(x) for x in v if x not in (None, ""))
                return str(v)
        return ""

    def escala(v):
        if not v:
            return ""
        return f"{v}/10" if "/" not in str(v) else str(v)

    queixa = val("queixaPrincipal", "spin_p_principalIncomodo")
    tempo = val("spin_s_tempoLuta", "tempoLuta")
    tentativas = val("spin_s_tentativas", "tentativasAnteriores", "jaTentou")
    sono = escala(val("qualidadeSono"))
    energia = escala(val("nivelEnergia"))
    motivo = val("spin_n_vidaResolvida", "motivoIVS")
    peso = val("pesoAtual", "peso")
    altura = val("altura")

    bloco_identidade = "".join([
        _q_field("O que mais te incomoda hoje", queixa, feature=True),
        _q_field("Há quanto tempo", tempo),
        _q_field("Já tentou", tentativas),
        _q_field("Por que IVS agora", motivo),
        _q_field("Peso atual", f"{peso} kg" if peso else "", sub=f"Altura {altura.replace('.', ',')} m" if altura else ""),
        _q_field("Objetivos declarados", val("tresObjetivos")),
    ])

    bloco_saude = "".join([
        _q_field("Medicamentos atuais", val("medicamentosAtuais")),
        _q_field("Doenças crônicas", val("doencasCronicas")),
        _q_field("Alergias/intolerâncias", val("alergiasIntolerâncias", "alergiasIntolerancias")),
        _q_field("Histórico familiar de câncer", val("historicoFamiliarCancer")),
        _q_field("Reposição hormonal", val("reposicaoHormonal")),
        _q_field("Fumo / álcool", f"Fumo: {val('habitoFumar') or '—'} · Álcool: {val('consumoAlcool') or '—'}"),
    ])

    bloco_rotina = "".join([
        _q_field("Sono", sono, sub=f"Horas/noite: {val('horasSono') or '—'}"),
        _q_field("Energia", energia, sub=val("cansacoDurante")),
        _q_field("Atividade física", val("atividadeFisica"), sub=val("frequenciaAtividade")),
        _q_field("Água / intestino", f"Água: {val('consumoAgua') or '—'}", sub=f"Intestino: {val('frequenciaIntestinal') or '—'}"),
        _q_field("Trabalho", val("profissao"), sub=f"{val('tipoTrabalho') or '—'} · {val('horariosTrabalho') or '—'}"),
        _q_field("Barreira percebida", val("barreiraSaude"), sub=f"Investe em saúde: {val('investeSaude') or '—'}"),
    ])

    bloco_alimentar = "".join([
        _q_field("Compulsão/vontade de doce", val("consumoDoces"), feature=True),
        _q_field("Refeições por dia", val("refeicoesDia"), sub=val("localRefeicoes")),
        _q_field("Como adoça", val("formaAdocar")),
        _q_field("Preferências alimentares", val("alimentosGosta"), sub=f"Não gosta: {val('alimentosNaoGosta') or '—'}"),
        _q_field("Fim de semana", val("alimentacaoFimSemana"), sub=val("alimentacaoFimSemanaDetalhe")),
        _q_field("Café da manhã", val("cafeDaManha")),
        _q_field("Lanche manhã", val("lancheManha")),
        _q_field("Almoço", val("almoco")),
        _q_field("Lanche tarde", val("lancheTarde")),
        _q_field("Jantar", val("jantar")),
    ])

    bloco_spin = "".join([
        _q_field("Desafio principal", val("spin_p_desafios"), feature=True),
        _q_field("Detalhe da luta", val("spin_s_tempoLutaDetalhe")),
        _q_field("Impacto na vida", val("spin_i_impactoVida")),
        _q_field("Cenário em 1 ano se nada mudar", val("spin_i_cenario1ano")),
        _q_field("Investimento perdido", val("spin_i_investimentoPerdido")),
        _q_field("Interesse no programa", val("spin_n_interessePrograma"), sub=f"Acompanhamento desejado: {val('interesseAcompanhamento') or '—'}"),
        _q_field("Mudanças desejadas", val("tresMudancas")),
        _q_field("Perfil DISC", val("discPerfil")),
    ])

    implicacoes = []
    if val("qualidadeSono") or val("nivelEnergia") or val("cansacoDurante"):
        implicacoes.append("Sono ruim, baixa energia e cansaço à tarde reduzem adesão, aumentam fome hedônica e precisam ser tratados junto com a estratégia alimentar.")
    if val("consumoDoces") or val("spin_p_desafios"):
        implicacoes.append("Ansiedade e vontade de doce à noite mostram que a solução não pode depender apenas de força de vontade; precisa de rotina assistida e ajustes progressivos.")
    if val("doencasCronicas") or val("medicamentosAtuais"):
        implicacoes.append("Hipertensão e uso de medicação exigem acompanhamento integrado para perda de gordura com segurança clínica.")
    if val("almoco") or val("jantar") or val("atividadeFisica"):
        implicacoes.append("Treino existe, mas o padrão alimentar descrito limita composição corporal; o plano precisa preservar massa magra enquanto reduz gordura.")
    implicacoes_html = "".join(f"<li>{safe_html(x)}</li>" for x in implicacoes)

    return f"""
<section id="patient-mirror" class="section patient-mirror">
  <div class="wrap">
    <h2>O espelho do seu caso</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">O que você nos contou antes da consulta. Aqui entram os dados relevantes do questionário, cruzados depois com exames de sangue e bioimpedância.</p>

    <h3 style="margin-top:var(--s-5);">1. Identidade do problema</h3>
    <div class="mirror-grid">{bloco_identidade}</div>

    <h3 style="margin-top:var(--s-6);">2. Saúde, rotina e contexto clínico</h3>
    <div class="mirror-grid">{bloco_saude}</div>
    <div class="mirror-grid">{bloco_rotina}</div>

    <h3 style="margin-top:var(--s-6);">3. Alimentação real do dia a dia</h3>
    <div class="mirror-grid">{bloco_alimentar}</div>

    <h3 style="margin-top:var(--s-6);">4. Dor, impacto e decisão</h3>
    <div class="mirror-grid">{bloco_spin}</div>

    <div class="compact-decision" style="margin-top:var(--s-6);">
      <h4>Leitura gerencial do questionário</h4>
      <ul>{implicacoes_html}</ul>
    </div>
  </div>
</section>
"""




def _bioimped_classifica_gordura(pct, sexo):
    """Retorna (severidade, label, alvo_texto) para % gordura."""
    try:
        pct_f = float(str(pct).replace(",", "."))
    except Exception:
        return ("ok", "", "")
    if sexo == "F":
        if pct_f < 21: return ("ok", "ideal", "21-32%")
        if pct_f < 33: return ("ok", "dentro do esperado", "21-32%")
        if pct_f < 39: return ("alert", "elevado", "alvo abaixo de 32%")
        return ("crit", "muito elevado", "alvo abaixo de 32%, redução prioritária")
    else:
        if pct_f < 12: return ("ok", "ideal", "12-22%")
        if pct_f < 23: return ("ok", "dentro do esperado", "12-22%")
        if pct_f < 28: return ("alert", "elevado", "alvo abaixo de 22%")
        return ("crit", "muito elevado", "alvo abaixo de 22%, redução prioritária")


def _bioimped_classifica_razao(razao):
    """Razão músculo/gordura: ideal ≥1,2."""
    try:
        v = float(str(razao).replace(",", "."))
    except Exception:
        return ("ok", "")
    if v >= 1.2: return ("ok", "equilíbrio favorável")
    if v >= 0.9: return ("alert", "abaixo do equilíbrio (ideal ≥1,2)")
    return ("crit", "muito abaixo do equilíbrio (ideal ≥1,2)")


def _bioimped_classifica_angulo(angulo, sexo, idade):
    """Ângulo de fase: marcador de vitalidade celular. F adulto ≥6.0 ok."""
    try:
        v = float(str(angulo).replace(",", "."))
    except Exception:
        return ("ok", "")
    threshold = 6.0 if sexo == "F" else 6.5
    if v >= threshold: return ("ok", "vitalidade celular preservada")
    if v >= threshold - 1: return ("alert", f"abaixo do ideal (≥{threshold}°)")
    return ("crit", f"muito abaixo do ideal (≥{threshold}°)")


def _bioimped_classifica_idade_celular(idade_cel, idade_cron):
    """Idade celular vs cronológica."""
    try:
        cel = float(idade_cel); cron = float(idade_cron)
    except Exception:
        return ("ok", "")
    diff = cel - cron
    if diff <= -2: return ("ok", f"{abs(diff):.0f} anos abaixo da cronológica (excelente)")
    if diff <= 1: return ("ok", "próxima à cronológica")
    if diff <= 4: return ("alert", f"{diff:.0f} anos acima da cronológica")
    return ("crit", f"{diff:.0f} anos acima da cronológica (envelhecimento celular)")


def _bioimped_classifica_imc(imc):
    try:
        v = float(str(imc).replace(",", "."))
    except Exception:
        return ("ok", "")
    if v < 18.5: return ("alert", "abaixo do peso")
    if v < 25: return ("ok", "peso normal")
    if v < 30: return ("alert", "sobrepeso")
    if v < 35: return ("crit", "obesidade grau 1")
    if v < 40: return ("crit", "obesidade grau 2")
    return ("crit", "obesidade grau 3")


def _fmt_delta(d):
    if not d or str(d).strip() in ("", "—", "-"): return ""
    s = str(d).strip()
    if s.startswith(("+",)): return f'<span class="delta up">Δ {s}</span>'
    if s.startswith(("-","−")): return f'<span class="delta down">Δ {s}</span>'
    return f'<span class="delta">Δ {s}</span>'


def render_bioimpedancia(bio, paciente):
    """Renderiza a seção de bioimpedância.

    bio (dict opcional):
      data_avaliacao, data_referencia, peso, altura, imc, tmb,
      gordura: {massa, pct, delta_pct}
      hidratacao: {agua_total, agua_total_pct, indice, agua_massa_magra}
      agua_celular: {intra, intra_pct, extra, extra_pct}
      massa: {magra_kg, magra_pct, muscular_kg, muscular_pct, razao_musc_gord, razao_delta}
      celular: {angulo_fase, angulo_delta, idade_celular, idade_cronologica}
    """
    if not bio:
        return ""

    sexo = str(paciente.get("sexo", "F")).upper()[:1]
    primeiro = safe_html(paciente.get("nome", "Paciente").split()[0])

    g = bio.get("gordura", {})
    h = bio.get("hidratacao", {})
    a = bio.get("agua_celular", {})
    m = bio.get("massa", {})
    c = bio.get("celular", {})

    # Classificações
    sev_g, lbl_g, alvo_g = _bioimped_classifica_gordura(g.get("pct"), sexo)
    sev_r, lbl_r = _bioimped_classifica_razao(m.get("razao_musc_gord"))
    sev_ang, lbl_ang = _bioimped_classifica_angulo(c.get("angulo_fase"), sexo, paciente.get("idade"))
    sev_ic, lbl_ic = _bioimped_classifica_idade_celular(c.get("idade_celular"), c.get("idade_cronologica"))
    sev_imc, lbl_imc = _bioimped_classifica_imc(bio.get("imc"))

    # Análise (lista de bullets clínicos)
    bullets = []
    if lbl_imc:
        bullets.append((sev_imc, f"<b>IMC {bio.get('imc')}</b> — {lbl_imc}."))
    if lbl_g:
        bullets.append((sev_g, f"<b>% gordura corporal {g.get('pct')}%</b> — {lbl_g} ({alvo_g})."))
    if lbl_r:
        bullets.append((sev_r, f"<b>Razão músculo/gordura {m.get('razao_musc_gord')}</b> — {lbl_r}. Reforça prioridade clínica de preservar/ganhar massa muscular durante a perda de gordura."))
    if lbl_ang:
        bullets.append((sev_ang, f"<b>Ângulo de fase {c.get('angulo_fase')}°</b> — {lbl_ang}. Marcador de qualidade de membrana celular e vitalidade."))
    if lbl_ic:
        bullets.append((sev_ic, f"<b>Idade celular {c.get('idade_celular')} anos</b> — {lbl_ic}."))

    # Variação vs avaliação anterior (se houver)
    if bio.get("data_referencia") and g.get("delta_pct"):
        bullets.append(("ok", f"Comparado com {safe_html(bio.get('data_referencia'))}, houve mudança de {safe_html(g.get('delta_pct'))} pontos no % de gordura."))

    bullets_html = "".join(f'<li class="{sev}">{txt}</li>' for sev, txt in bullets)

    # Meta header
    meta_parts = []
    if bio.get("data_avaliacao"):
        meta_parts.append(f"Avaliação em <b>{safe_html(bio['data_avaliacao'])}</b>")
    if bio.get("data_referencia"):
        meta_parts.append(f"comparada com {safe_html(bio['data_referencia'])}")
    meta_html = " · ".join(meta_parts) if meta_parts else "Bioimpedância recente"

    # KPI helpers
    def kpi(label, value, unit="", delta=""):
        if not value: return ""
        v_str = safe_html(value)
        u_str = f'<span class="unit">{safe_html(unit)}</span>' if unit else ""
        return f'<div class="bio-kpi"><span class="label">{safe_html(label)}</span><span class="value">{v_str}{u_str}{_fmt_delta(delta)}</span></div>'

    card_composicao = f"""
    <div class="bio-card">
      <h4>Composição corporal</h4>
      <div class="kpis">
        {kpi("Peso", bio.get("peso"), "kg")}
        {kpi("IMC", bio.get("imc"), "kg/m²")}
        {kpi("Massa gorda", g.get("massa"), "kg")}
        {kpi("% Gordura", g.get("pct"), "%", g.get("delta_pct"))}
        {kpi("Massa magra", m.get("magra_kg"), "kg")}
        {kpi("Massa muscular", m.get("muscular_kg"), f"kg ({m.get('muscular_pct','')}%)" if m.get("muscular_pct") else "kg")}
        {kpi("Razão músc/gord", m.get("razao_musc_gord"), "", m.get("razao_delta"))}
        {kpi("TMB", bio.get("tmb"), "kcal/24h")}
      </div>
    </div>
    """

    card_hidratacao = f"""
    <div class="bio-card">
      <h4>Hidratação</h4>
      <div class="kpis">
        {kpi("Água corporal total", h.get("agua_total"), "L")}
        {kpi("Água corporal total", h.get("agua_total_pct"), "% do peso")}
        {kpi("Índice de hidratação", h.get("indice"), "cm/ohms")}
        {kpi("Água na massa magra", h.get("agua_massa_magra"), "%")}
        {kpi("Água intracelular", a.get("intra"), "L")}
        {kpi("% Intracelular", a.get("intra_pct"), "%")}
        {kpi("Água extracelular", a.get("extra"), "L")}
        {kpi("% Extracelular", a.get("extra_pct"), "%")}
      </div>
    </div>
    """

    card_celular = f"""
    <div class="bio-card">
      <h4>Análise celular</h4>
      <div class="kpis">
        {kpi("Ângulo de fase", c.get("angulo_fase"), "graus", c.get("angulo_delta"))}
        {kpi("Idade celular", c.get("idade_celular"), "anos")}
        {kpi("Idade cronológica", c.get("idade_cronologica"), "anos")}
      </div>
      <p style="font-size:12px;color:var(--muted);margin:var(--s-3) 0 0;line-height:1.5">
        O ângulo de fase reflete a integridade da membrana celular. Valores mais altos indicam células com melhor sinalização e vitalidade. A idade celular é estimada a partir da bioimpedância e pode estar acima ou abaixo da idade real.
      </p>
    </div>
    """

    # Imagem original do laudo (se extractor anexou)
    imagem_b64 = bio.get("_imagem_b64") or ""
    if imagem_b64:
        bio_image_html = (
            '<div class="bio-image-wrap">'
            '<h4>Laudo original</h4>'
            f'<img src="data:image/jpeg;base64,{imagem_b64}" alt="Laudo de bioimpedância" loading="lazy"/>'
            '<span class="caption">Imagem extraída do PDF original — referência visual da avaliação.</span>'
            '</div>'
        )
    else:
        bio_image_html = ""

    return f"""
<section id="bioimpedancia" class="section bioimped-section">
  <div class="wrap">
    <h2>Bioimpedância — composição corporal</h2>
    <p class="bioimped-meta">{meta_html}</p>
    <div class="bio-grid">
      {card_composicao}
      {card_hidratacao}
      {card_celular}
    </div>
    <div class="bio-highlight">
      <h4>Leitura clínica para {primeiro}</h4>
      <ul>{bullets_html}</ul>
    </div>
    {bio_image_html}
  </div>
</section>
"""

def render_critical_levers(levers, perfil_disc="default", questionario=None):
    if not levers:
        return ""
    cards = []
    for lv in levers:
        nome = lv["nome"]
        sev = lv.get("status", "alert")
        sev_label = "Crítico" if sev == "crit" else ("Normal" if sev in ("ok", "normal") else "Atenção")
        leitura, impacto, decisao = _decision_copy(nome, sev=sev, questionario=questionario)
        cards.append(f"""
<div class="lever-card fade-up" data-sev="{sev}">
  <div class="lever-numeric">
    <div class="name">{render_sev_ring(lv["valor"], lv.get("ref","—"), sev)}<span>{safe_html(nome)}</span></div>
    <div class="value tabular">{safe_html(lv["valor"])}<span class="unit">{safe_html(lv.get("unit",""))}</span></div>
    <div class="ref">Referência IVS: {safe_html(lv.get("ref","—"))}</div>
    <span class="badge">{sev_label}</span>
    {render_sparkline(lv["valor"], lv.get("ref","—"), sev)}
  </div>
  <div class="lever-narrative compact-decision">
    <div class="impact"><strong>O que significa:</strong> {safe_html(leitura)}</div>
    <div class="impact"><strong>Por que importa:</strong> {safe_html(impacto)}</div>
    <div class="spin-q"><strong>Risco no seu caso:</strong> {safe_html(decisao)}</div>
  </div>
</div>
""")
    return f"""
<section id="critical-levers" class="section critical-levers">
  <div class="wrap">
    <h2>Mapa de alavancas críticas</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">As {len(levers)} alavancas que mais influenciam o seu plano. Cada uma mostra o que o exame significa, o que isso implica na prática e por que vale resolver com acompanhamento estruturado.</p>
    <div class="lever-list">{"".join(cards)}</div>
  </div>
</section>
"""


def render_spin_guided(paciente, questionario, levers, perfil_disc="default"):
    """Renderiza 'Leitura integrada do caso' — sem labels de venda S/P/I/N."""
    primeiro = safe_html(paciente.get("nome", "Paciente").split()[0])
    dados_q = (questionario or {}).get("pre-consulta", {}).get("dados", {}) if isinstance(questionario, dict) else {}
    if not dados_q and isinstance(questionario, dict) and "dados" in questionario:
        dados_q = questionario.get("dados", {})

    def qv(k):
        v = dados_q.get(k)
        return "" if v in (None, "", [], {}) else str(v)

    ponto_partida_items = []
    if qv("doencasCronicas") or qv("medicamentosAtuais"):
        ponto_partida_items.append(f"Condição clínica declarada: {qv('doencasCronicas') or 'não informada'}; medicação atual: {qv('medicamentosAtuais') or 'não informada'}.")
    if qv("qualidadeSono") or qv("nivelEnergia") or qv("cansacoDurante"):
        ponto_partida_items.append(f"Sono {qv('qualidadeSono') or '—'}/10, energia {qv('nivelEnergia') or '—'}/10 e cansaço relatado: {qv('cansacoDurante') or 'não informado'}.")
    if qv("spin_p_desafios") or qv("spin_s_tempoLutaDetalhe") or qv("consumoDoces"):
        ponto_partida_items.append(f"Desafio de adesão: {qv('spin_p_desafios') or qv('spin_s_tempoLutaDetalhe')}; vontade de doce: {qv('consumoDoces') or 'não informada'}.")
    if qv("almoco") or qv("jantar") or qv("alimentacaoFimSemana"):
        ponto_partida_items.append(f"Padrão alimentar descrito: almoço — {qv('almoco') or 'não informado'}; jantar — {qv('jantar') or 'não informado'}; fim de semana — {qv('alimentacaoFimSemana') or 'não informado'}.")
    if qv("atividadeFisica") or qv("tresObjetivos"):
        ponto_partida_items.append(f"Rotina/objetivo: {qv('atividadeFisica') or 'atividade não informada'}; objetivo — {qv('tresObjetivos') or 'não informado'}.")
    if not ponto_partida_items:
        ponto_partida_items.append("Questionário pré-consulta carregado; leitura será cruzada com os marcadores laboratoriais e corporais disponíveis.")
    ponto_partida_html = "".join(f"<li>{safe_html(x)}</li>" for x in ponto_partida_items)
    ponto_partida_alerta = f"{primeiro}, este é o ponto de partida objetivo do seu caso: sintomas, rotina e exames precisam ser lidos juntos para definir o acompanhamento."

    # Tabela de marcadores: alavanca + implicação clínica + necessidade de agir
    rows_p = ""
    for lv in levers[:5]:
        interp = INTERPRETACAO_LEVERS.get(lv["nome"], DEFAULT_INTERP)
        necessidade = _necessidade_solucao(lv["nome"], sev=lv.get("status", "alert"), perfil_disc=perfil_disc)
        rows_p += (f"<tr><td><strong>{safe_html(lv['nome'])} {safe_html(lv['valor'])}"
                   f"{safe_html(lv.get('unit',''))}</strong></td>"
                   f"<td>{safe_html(interp['interpretacao'])} <strong>Implicação:</strong> {safe_html(interp['impacto'])} <strong>Necessidade:</strong> {safe_html(necessidade)}</td></tr>")

    return f"""
<section id="leitura-integrada" class="section leitura-integrada">
  <div class="wrap">
    <h2>Leitura integrada do caso</h2>
    <p style="max-width:720px;font-size:16px;color:var(--muted);">{_t_disc("leitura_lead", perfil_disc)} Aqui, a leitura cruza marcador, implicação prática e por que o acompanhamento é a forma mais segura de corrigir a causa — não só reagir ao número.</p>

    <div class="leitura-block fade-up">
      <h3>O ponto de partida</h3>
      <p class="body-text">Resumo objetivo do questionário que muda a leitura dos exames e da bioimpedância:</p>
      <ul class="body-text" style="margin:0 0 var(--s-4);padding-left:20px;">{ponto_partida_html}</ul>
      <div class="alinhamento">{ponto_partida_alerta}</div>
    </div>

    <div class="leitura-block fade-up">
      <h3>Os sinais que se conectam</h3>
      <p class="body-text">{_t_disc("leitura_b2_body", perfil_disc)}</p>
      <table class="spin-table">
        <thead><tr><th>Marcador</th><th>Leitura clínica, implicação e necessidade de agir</th></tr></thead>
        <tbody>{rows_p}</tbody>
      </table>
      <div class="alinhamento">{_t_disc("leitura_b2_alinhamento", perfil_disc)}</div>
    </div>

    <div class="leitura-block fade-up">
      <h3>Para onde a tendência aponta</h3>
      <p class="body-text">{_t_disc("leitura_b3_body", perfil_disc)}</p>
      <div class="alinhamento">{_t_disc("leitura_b3_alinhamento", perfil_disc)}</div>
    </div>

    <div class="leitura-block fade-up">
      <h3>Recomendação clínica</h3>
      <p class="body-text">{_t_disc("leitura_b4_body", perfil_disc)}</p>
      <div class="alinhamento">{_t_disc("leitura_b4_alinhamento", perfil_disc, primeiro=primeiro)}</div>
    </div>
  </div>
</section>
"""


def render_ivs_machine():
    steps = [
        ("01", "Diagnóstico", "Bateria avançada de biomarcadores + leitura clínica individualizada."),
        ("02", "Protocolo", "Plano construído para o seu perfil — hormonal, nutricional, farmacológico quando indicado."),
        ("03", "Execução", "Início assistido. Equipe completa orienta a primeira semana e o primeiro mês."),
        ("04", "Suporte", "Acompanhamento médico com suporte da equipe (nutri, preparador, enfermeira). Cadência semanal."),
        ("05", "Ajuste", "Mudanças baseadas em resposta clínica, não em calendário fixo."),
        ("06", "Reavaliação", "Reavaliação trimestral de biomarcadores. Plano de manutenção construído junto."),
    ]
    items = "".join(
        f'<div class="machine-step fade-up"><div class="num">{n}</div>'
        f'<div class="title">{safe_html(t)}</div>'
        f'<div class="desc">{safe_html(d)}</div></div>'
        for n, t, d in steps
    )
    return f"""
<section id="ivs-machine" class="section ivs-machine">
  <div class="wrap">
    <h2>O mecanismo do acompanhamento</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">Não é uma lista de benefícios — é um sistema. Cada etapa alimenta a próxima, e os ajustes feitos durante o caminho é que constroem o resultado.</p>
    <div class="machine-flow">{items}</div>
  </div>
</section>
"""


def render_proof_by_process():
    casos = [
        {
            "nome": "Tiaro Neves", "iniciais": "TN",
            "antes": "tiaro-antes.png", "depois": "tiaro-depois.png",
            "frase": "O peso era apenas o sintoma. O que mudou foi o corpo todo: pressão estabilizada, energia diferente, dores que sumiram. Hoje vivo de outra forma.",
        },
        {
            "nome": "Silvana A.", "iniciais": "SA",
            "antes": "silvana-antes.png", "depois": "silvana-depois.png",
            "frase": "O sentimento que eu tenho é felicidade. A atenção e o carinho que recebi não tiveram igual. Os meus resultados falam por si só.",
        },
        {
            "nome": "Darilene A.", "iniciais": "DA",
            "antes": "darilene-antes.png", "depois": "darilene-depois.png",
            "frase": "Quando cheguei na clínica eu estava cansada, sem esperança. Achava que nunca ia conseguir. A equipe acreditou em mim mesmo quando eu duvidava.",
        },
    ]
    cards = []
    for i, c in enumerate(casos):
        antes_b64 = img_b64(SITE_IMAGES / c["antes"])
        depois_b64 = img_b64(SITE_IMAGES / c["depois"])
        cards.append(f"""
<div class="proof-card fade-up">
  <div class="proof-imgs">
    <div class="proof-img"><span class="label">Antes</span><img src="{antes_b64}" alt="{safe_html(c['nome'])}"></div>
    <div class="proof-img"><span class="label">Depois</span><img src="{depois_b64}" alt="{safe_html(c['nome'])}"></div>
  </div>
  <div class="proof-text">
    <span class="step-eyebrow">Caso {str(i+1).zfill(2)} · {safe_html(c['iniciais'])}</span>
    <h3>{safe_html(c['nome'])}</h3>
    <blockquote>"{safe_html(c['frase'])}"</blockquote>
  </div>
</div>
""")
    return f"""
<section id="proof-by-process" class="section proof-by-process">
  <div class="wrap">
    <h2>Prova pelo processo</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">Três pacientes acompanhados por meses ou anos. Casos reais, não promessa. O método é o mesmo — o caminho de cada um foi construído individualmente.</p>
    <div class="proof-thesis fade-up">
      <p>Não mostramos esses casos como promessa. Mostramos para <strong>provar o processo</strong>: acompanhamento, ajustes e continuidade são o que constrói o resultado.</p>
    </div>
    <div class="proof-list">{"".join(cards)}</div>
    <div class="proof-disclaimer">Resultados individuais variam e dependem de avaliação clínica, adesão ao plano e acompanhamento contínuo. As imagens ilustram acompanhamento clínico real e não constituem promessa de resultado.</div>
  </div>
</section>
"""


def render_program_180():
    """V2.3 — programa enxuto, 4 marcos simples, sem detalhamento operacional."""
    fases = [
        ("Início assistido",
         "Avaliação aprofundada, definição do mapa metabólico individualizado e onboarding com a equipe."),
        ("Acompanhamento",
         "Cadência semanal entre consultas, suporte ativo da equipe, leitura contínua de sintomas e resposta clínica."),
        ("Ajustes",
         "Mudanças de protocolo guiadas por resposta clínica do seu corpo — não por calendário fixo."),
        ("Reavaliação",
         "Painel laboratorial recorrente. Construção do plano de manutenção ao final do ciclo."),
    ]
    fases_html = "".join(
        f'<div class="program-phase fade-up">'
        f'<div class="phase-marker"><div class="num">{i+1:02d}</div></div>'
        f'<div class="phase-content"><h4>{safe_html(t)}</h4>'
        f'<p class="desc">{safe_html(d)}</p></div>'
        f'</div>'
        for i, (t, d) in enumerate(fases)
    )
    return f"""
<section id="program-180-days" class="section program-180-days">
  <div class="wrap">
    <h2>Os próximos 180 dias</h2>
    <p style="max-width:680px;font-size:16px;color:var(--muted);">Quatro movimentos clínicos. O que importa não é o cronograma — é a continuidade dos ajustes feitos durante o caminho.</p>
    <div class="program-timeline">{fases_html}</div>
  </div>
</section>
"""


def render_doctor_objections():
    """V2.5 — Apêndice da médica com busca, categorias e cards collapsable.
    Otimizado para consulta rápida durante a consulta clínica."""
    # (categoria, objeção, o que revela, resposta, pergunta de condução)
    objs = [
        ("Hesitação", "Quero pensar.",
         "Costuma ser sinal de que ainda falta clareza sobre o que está em jogo, ou tempo para processar a recomendação.",
         "Faz total sentido pensar com calma. Posso te enviar um resumo dessa consulta com os pontos clínicos principais para revisitar quando precisar.",
         "O que ainda falta ficar claro para você se sentir confortável com a próxima decisão?"),
        ("Família", "Preciso conversar com minha família primeiro.",
         "Sinaliza um espaço de validação importante — paciente quer dividir a decisão com alguém de confiança.",
         "Faz total sentido. Posso preparar um resumo da consulta com os pontos clínicos principais, para você apresentar em casa com base nos exames, não em uma proposta comercial.",
         "Quem normalmente conversa com você sobre esse tipo de decisão?"),
        ("Financeiro", "Achei o investimento alto.",
         "O paciente ainda está comparando com consulta avulsa, dieta isolada ou tentativa anterior — não com um sistema clínico contínuo.",
         "Faz sentido olhar com cuidado. A diferença aqui é que não estamos falando de intervenção isolada, mas de acompanhamento com leitura clínica, equipe, ajustes e reavaliações ao longo do processo.",
         "Quando você compara com o custo somado das tentativas que não sustentaram resultado, faz sentido olhar para isso como acompanhamento e não como uma consulta?"),
        ("Autonomia", "Vou tentar sozinho primeiro.",
         "Reflete confiança na própria disciplina e desconfiança quanto à necessidade real de acompanhamento.",
         "Tentar sozinho não é falta de disciplina — é falta de leitura clínica em tempo real. Se você já tentou antes, provavelmente já sentiu o que falta: alguém ajustando rota com você.",
         "O que costuma fazer você desistir quando tenta sozinho?"),
        ("Medicação", "Tenho medo de medicação.",
         "Geralmente vem de experiência negativa anterior ou da preocupação com efeitos colaterais e dependência.",
         "Medicação só entra quando há indicação clínica clara e revisão periódica. Não é regra do programa — é ferramenta usada quando o caso pede. E o objetivo é sempre função, não dependência.",
         "Que experiência prévia com medicação fez você desenvolver esse cuidado?"),
        ("Medicação", "Não quero ficar dependente.",
         "Próxima do medo de medicação, mas costuma envolver também receio de virar paciente crônico ou de perder autonomia.",
         "Acompanhar permite usar medicação só quando faz diferença real — e suspender quando não precisa mais. O que se busca é função, não dependência.",
         "O que você considera 'estar bem sem precisar de nada'?"),
        ("Tempo", "Não tenho tempo agora.",
         "Pode refletir agenda real ou ansiedade sobre o compromisso operacional do programa.",
         "O programa foi desenhado para integrar à rotina, não substituí-la. A maior parte dos ajustes é remota; as consultas presenciais são pontuais e planejadas.",
         "Como ficaria se a parte mais demandante fosse na primeira semana, e depois ficasse mais leve?"),
        ("Histórico", "Já tentei muitas vezes e não funcionou.",
         "Há cansaço acumulado e proteção emocional contra mais uma frustração.",
         "Tentativas frustradas costumam ter um padrão em comum: faltou leitura clínica e correção de rota. Não foi falta de esforço seu.",
         "Se a gente conseguisse identificar o que realmente derruba sua adesão, valeria tentar de um jeito diferente?"),
        ("Manutenção", "Tenho medo de não conseguir manter.",
         "Reflete autoavaliação realista, mas também a expectativa de que manter dependa só de força de vontade.",
         "Manter raramente é questão de disciplina pessoal. É ter quem leia sua resposta e ajuste a rota. É exatamente para isso que existe a equipe.",
         "Se tivesse alguém olhando o seu caso a cada duas semanas, mudaria a sua percepção sobre conseguir manter?"),
        ("Resultado", "E se eu pagar e não tiver resultado?",
         "Pede transparência sobre o que é prometido e como o resultado é construído.",
         "Não prometo resultado fechado — isso seria desonesto. O que ofereço é leitura clínica contínua, ajustes baseados em resposta e reavaliações com biomarcadores. Resultado depende de adesão, indicação e seu organismo.",
         "Para você, como ficaria a percepção de valor se a gente combinasse marcos de reavaliação claros desde o início?"),
        ("Autonomia", "Prefiro começar só com dieta e treino.",
         "Subestima a complexidade do caso ou tenta minimizar a entrada no programa.",
         "Dieta e treino isolados resolvem alguns casos. O seu, pelos exames, mostra sinais que pedem leitura conjunta — hormônio, inflamação e metabolismo. Tratar isolado tende a frustrar.",
         "Você já tentou só dieta e treino antes? O que aconteceu depois de algumas semanas?"),
        ("Compromisso", "Quero fazer só os exames e depois vejo.",
         "Quer reduzir compromisso inicial; pode ser legítimo ou pode ser fuga da decisão.",
         "Exames sem leitura clínica acompanhada raramente mudam o cenário. O número sozinho não muda nada — o que muda é a interpretação e a estratégia construída em cima.",
         "Se eu lesse seus exames hoje e te entregasse a interpretação, qual seria o próximo passo lógico para você?"),
        ("Autonomia", "Não gosto de acompanhamento muito próximo.",
         "Reflete preferência por autonomia ou desconforto com proximidade clínica.",
         "Acompanhar não significa controlar. Significa ter alguém disponível quando você precisa, sem exigir contato constante. A cadência é planejada, não invasiva.",
         "Como seria, para você, um acompanhamento que respeitasse mais sua autonomia?"),
        ("Hormônios", "Tenho receio de hormônios.",
         "Costuma vir de informação assimétrica — mídia, casos isolados, falta de explicação clínica.",
         "Reposição hormonal só entra com indicação clínica precisa, monitoramento de biomarcadores e revisão periódica. Não é regra do programa — é ferramenta para casos específicos.",
         "Se hormônio entrasse no plano só após reavaliação clínica e exames específicos, mudaria sua percepção?"),
        ("Hesitação", "Não estou pronto para começar agora.",
         "Sinal de que ainda falta um gatilho emocional ou clínico para a decisão.",
         "Faz sentido. Não há urgência artificial. Mas vale registrar a recomendação clínica e o quadro atual, para que possamos retomar quando você decidir.",
         "O que precisaria mudar — clinicamente ou na sua vida — para você se sentir pronto?"),
    ]

    # Categorias únicas em ordem de aparição
    cats_seen = []
    for cat, *_ in objs:
        if cat not in cats_seen:
            cats_seen.append(cat)

    cards = ""
    for cat, q, reveals, resp, cond in objs:
        # data attributes para busca e filtro
        searchtext = f"{cat} {q} {reveals} {resp} {cond}".lower()
        cards += (
            f'<div class="doctor-obj-card" data-cat="{safe_html(cat)}" data-search="{safe_html(searchtext)}">'
            f'<div class="obj-header">'
            f'<span class="obj-cat-tag">{safe_html(cat)}</span>'
            f'<h3>"{safe_html(q)}"</h3>'
            f'<span class="obj-toggle">▾</span>'
            f'</div>'
            f'<div class="obj-body">'
            f'<p><strong>O que revela</strong>{safe_html(reveals)}</p>'
            f'<p><strong>Resposta sugerida</strong>{safe_html(resp)}</p>'
            f'<p class="cond"><strong>Pergunta de condução</strong>{safe_html(cond)}</p>'
            f'</div>'
            f'</div>'
        )

    chips = '<button class="obj-cat-chip active" data-cat="todas">Todas</button>'
    chips += "".join(
        f'<button class="obj-cat-chip" data-cat="{safe_html(cat)}">{safe_html(cat)}</button>'
        for cat in cats_seen
    )

    return f"""
<section id="doctor-objections" class="section doctor-objections">
  <div class="wrap">
    <span class="doctor-tag">Apêndice da médica · Uso interno</span>
    <h2>Objeções e condução da conversa</h2>
    <p class="lead">Material interno para apoio da Dra. Daniely durante a consulta. Busque por palavra-chave ou filtre por categoria. Clique no card para expandir resposta e pergunta de condução.</p>

    <div class="obj-toolbar">
      <div class="obj-search-wrap">
        <svg class="obj-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/></svg>
        <input type="text" class="obj-search" placeholder="Buscar objeção, palavra-chave ou categoria..." autocomplete="off">
        <span class="obj-shortcut">/</span>
        <button class="obj-search-clear" aria-label="Limpar busca">×</button>
      </div>
      <div class="obj-cats" role="tablist">{chips}</div>
      <div class="obj-counter"><span class="obj-counter-num">{len(objs)}</span> objeções disponíveis</div>
    </div>

    <div class="doctor-obj-list">
      {cards}
      <div class="obj-empty" hidden>Nenhuma objeção encontrada com este filtro.</div>
    </div>
  </div>
</section>
"""



def render_decision_checklist(paciente):
    primeiro = safe_html(paciente.get("nome", "Paciente").split()[0])
    items = [
        "Reconheço que existe um problema funcional no meu caso, não apenas estético.",
        "Entendo que adiar pode manter o quadro sem uma leitura clínica mais acompanhada.",
        "Concordo que minha situação pede acompanhamento, não orientação isolada.",
        "Estou pronto para discutir o início assistido com a equipe da Dra. Daniely Freitas.",
    ]
    items_html = "".join(
        f'<div class="checklist-item"><div class="check"></div>'
        f'<div class="text">{safe_html(it)}</div></div>'
        for it in items
    )
    return f"""
<section id="decision-checklist" class="section decision-checklist">
  <div class="wrap">
    <h2>Antes da decisão, {primeiro}</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);text-align:center;margin:0 auto;">Marque cada item com o qual você concorda. Não é vinculante — é uma forma de tornar a decisão mais clara para você.</p>
    <div class="checklist-card">
      {items_html}
      <div class="checklist-progress">
        <div class="checklist-progress-bar"><div class="checklist-progress-fill"></div></div>
        <div class="checklist-progress-text">0 de 4 confirmados</div>
      </div>
    </div>
  </div>
</section>
"""



def render_inclusos():
    """V2.6 — 8 inclusos específicos do programa com ícones SVG temáticos premium."""
    # Cada SVG é desenhado para conectar visualmente com o conteúdo do card
    items = [
        ("Equipe Multidisciplinar",
         "Médica, Nutricionista, Preparador Físico e Enfermeira acompanhando biomarcadores e com leitura clínica individualizada.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<circle cx="11" cy="11" r="3.5"/>'
         '<circle cx="21" cy="11" r="3"/>'
         '<circle cx="6.5" cy="20" r="2.8"/>'
         '<circle cx="25.5" cy="20" r="2.8"/>'
         '<path d="M3 28v-1.5c0-2.2 1.7-4 3.8-4h0"/>'
         '<path d="M16 28v-1.5c0-2.5-2-4.5-4.5-4.5h-1c-2.5 0-4.5 2-4.5 4.5"/>'
         '<path d="M29 28v-1.5c0-2.2-1.7-4-3.8-4h0"/>'
         '<path d="M27 14.5c-1.5 0-2.8 1-3 2.5"/>'
         '</svg>'),
        ("Terapias Nutricionais Injetáveis",
         "Soroterapia e aplicações intramusculares de suplementação nutricional para suprir deficiências e potencializar a resposta do tratamento.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<path d="M19 5l8 8"/>'
         '<path d="M22 8l-1.5-1.5"/>'
         '<path d="M22 8l3-3"/>'
         '<path d="M5 27l13.5-13.5 3 3L8 30"/>'
         '<path d="M9 23l3 3"/>'
         '<path d="M13 19l3 3"/>'
         '<circle cx="6" cy="11" r="0.8" fill="currentColor"/>'
         '<circle cx="3" cy="14" r="0.8" fill="currentColor"/>'
         '<circle cx="6" cy="17" r="0.8" fill="currentColor"/>'
         '</svg>'),
        ("Exames Genéticos",
         "Microbiota Intestinal ou Lifecode para avaliar mais de 275 variantes associadas à saúde, nutrição e bem-estar — informações sobre riscos e potenciais genéticos.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<path d="M9 4c0 4 6 6 6 12s-6 8-6 12"/>'
         '<path d="M23 4c0 4-6 6-6 12s6 8 6 12"/>'
         '<path d="M10 8h12"/>'
         '<path d="M10 24h12"/>'
         '<path d="M11.5 11h9"/>'
         '<path d="M11.5 21h9"/>'
         '<path d="M13 14h6"/>'
         '<path d="M13 18h6"/>'
         '</svg>'),
        ("Medicações GLP-1/GIP",
         "Uso de Tirzepatida (Mounjaro) para emagrecimento, resistência insulínica e inflamação sistêmica de forma assistida e com doses ideais ao tratamento.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<rect x="6" y="13" width="20" height="6" rx="3" transform="rotate(-30 16 16)"/>'
         '<path d="M11.5 18.5l9-5.2" stroke-dasharray="0.5 1.8"/>'
         '<circle cx="9" cy="9" r="1" fill="currentColor"/>'
         '<circle cx="6" cy="11.5" r="0.7" fill="currentColor"/>'
         '<circle cx="11.5" cy="6" r="0.7" fill="currentColor"/>'
         '</svg>'),
        ("Reposição Hormonal",
         "Quando necessário, reposição via implantes hormonais e não hormonais como terapia complementar — sempre com indicação clínica e monitoramento.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<rect x="9" y="6" width="14" height="20" rx="7"/>'
         '<path d="M9 16h14"/>'
         '<circle cx="13.5" cy="11" r="0.9" fill="currentColor"/>'
         '<circle cx="18.5" cy="11" r="0.9" fill="currentColor"/>'
         '<circle cx="13.5" cy="21" r="0.9" fill="currentColor"/>'
         '<circle cx="18.5" cy="21" r="0.9" fill="currentColor"/>'
         '<path d="M9 16c-2 0-3 1-3 2.5"/>'
         '<path d="M23 16c2 0 3 1 3 2.5"/>'
         '</svg>'),
        ("Fórmulas Orais",
         "Fórmulas de farmácias de manipulação para uso oral, individualizadas para potencializar o resultado do tratamento.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<path d="M11 4h10"/>'
         '<path d="M13 4v4l-3.5 5.5c-1 1.5-1.5 3-1.5 4.5v8c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-8c0-1.5-.5-3-1.5-4.5L19 8V4"/>'
         '<path d="M9 18h14"/>'
         '<circle cx="13" cy="22" r="0.9" fill="currentColor"/>'
         '<circle cx="17" cy="24" r="0.9" fill="currentColor"/>'
         '<circle cx="20" cy="21" r="0.9" fill="currentColor"/>'
         '</svg>'),
        ("Reavaliação Semanal",
         "Acompanhamento semanal para revisão de resultados e ajuste fino da condução do tratamento, de forma totalmente personalizada.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<rect x="5" y="7" width="22" height="20" rx="2.5"/>'
         '<path d="M5 13h22"/>'
         '<path d="M11 4v6"/>'
         '<path d="M21 4v6"/>'
         '<path d="M11 18l3 3 5-6"/>'
         '<circle cx="9" cy="22" r="0.7" fill="currentColor"/>'
         '<circle cx="23" cy="22" r="0.7" fill="currentColor"/>'
         '</svg>'),
        ("Médica Exclusiva",
         "Atendimento médico exclusivo e prioritário 24/7 — canal direto para o que você precisar durante o programa.",
         '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         '<circle cx="16" cy="16" r="11"/>'
         '<path d="M16 9v7l4 3"/>'
         '<path d="M5.5 16h2"/>'
         '<path d="M24.5 16h2"/>'
         '<path d="M16 5.5v2"/>'
         '<path d="M16 24.5v2"/>'
         '<circle cx="16" cy="16" r="1.2" fill="currentColor"/>'
         '</svg>'),
    ]
    cards = "".join(
        f'<div class="incluso-card fade-up">'
        f'<div class="incluso-icon">{svg}</div>'
        f'<h4 class="incluso-titulo">{safe_html(t)}</h4>'
        f'<p class="incluso-desc">{safe_html(d)}</p></div>'
        for t, d, svg in items
    )
    return f"""
<section id="inclusos" class="section inclusos">
  <div class="wrap">
    <h2>O que está incluído no acompanhamento</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);">Antes de pensar em decisão, vale entender o que compõe o programa. Não é uma consulta avulsa — é uma estrutura completa de cuidado clínico.</p>
    <div class="inclusos-grid">{cards}</div>
  </div>
</section>
"""


def render_final_cta(paciente, perfil_disc="default"):
    primeiro = safe_html(paciente.get("nome", "Paciente").split()[0])
    return f"""
<section id="final-cta" class="section final-cta">
  <div class="wrap">
    <div class="cta-frame fade-up">
      <p class="cta-frame-text">{_t_disc("cta_frame", perfil_disc)}</p>
    </div>
    <h2 style="text-align:center;">A recomendação clínica é começar de forma assistida</h2>
    <p style="max-width:780px;font-size:16px;color:var(--muted);text-align:center;margin:0 auto var(--s-7);">Se fizer sentido para você, o próximo passo é organizarmos juntos a sua linha de acompanhamento e colocarmos a equipe para caminhar contigo nos próximos 180 dias.</p>
    <div class="cta-decision">
      <div class="cta-card recommended fade-up">
        <div class="label">Recomendação clínica</div>
        <h3>{_t_disc("cta_recomendado_h3", perfil_disc)}</h3>
        <p class="desc">{_t_disc("cta_recomendado_desc", perfil_disc, primeiro=primeiro)}</p>
        <span class="button">Quero iniciar o acompanhamento</span>
      </div>
    </div>
    <div class="cta-signature">
      <div class="name">Dra. Daniely Freitas</div>
      <div class="meta">CRM-BA 27.588 · Médica do Estilo de Vida · Instituto Vital Slim</div>
    </div>
  </div>
</section>
"""


def render_questionnaire_appendix(questionario):
    dados = (questionario or {}).get("pre-consulta", {}).get("dados", {}) if isinstance(questionario, dict) else {}
    if not dados and isinstance(questionario, dict) and "dados" in questionario:
        dados = questionario.get("dados", {})
    label_map = {
        "spin_s_tempoLuta": "Tempo convivendo com o problema",
        "spin_s_tempoLutaDetalhe": "Contexto da dificuldade",
        "spin_s_tentativas": "O que já tentou antes",
        "spin_p_principalIncomodo": "Principal incômodo hoje",
        "spin_p_desafios": "Principal desafio percebido",
        "spin_i_impactoVida": "Impacto na vida",
        "spin_i_cenario1ano": "Como se vê em 1 ano se nada mudar",
        "spin_i_investimentoPerdido": "Percepção de investimento já perdido",
        "spin_i_oportunidadesPerdidas": "Oportunidades perdidas percebidas",
        "spin_n_vidaResolvida": "Como deseja estar com a vida resolvida",
        "spin_n_interessePrograma": "Interesse no acompanhamento",
    }
    rows = []
    for key in sorted(dados.keys()):
        if str(key).startswith("draft") or key in {"draftSessionId", "updatedAt"}:
            continue
        value = dados.get(key)
        if value in (None, "", [], {}):
            continue
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(v) for v in value if v not in (None, ""))
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        label = label_map.get(key) or re.sub(r"([a-z])([A-Z])", r"\1 \2", str(key)).replace("_", " ").strip().capitalize()
        rows.append(
            f'<div class="exam-row questionnaire-row">'
            f'<div class="e-nome">{safe_html(label)}</div>'
            f'<div class="e-valor">{safe_html(value)}</div>'
            f'<div class="e-ref">Questionário pré-consulta</div>'
            f'<div class="e-status">levantado</div></div>'
        )
    if not rows:
        return ""
    return f"""
<section id="questionnaire-appendix" class="section technical-appendix">
  <div class="wrap">
    <h2>Apêndice técnico — questionário completo</h2>
    <div class="appendix-controls">
      <p class="lead">Registro de cobertura das respostas usadas como primeiro pilar da apresentação. A análise clínica cruza essas respostas com todos os exames disponíveis.</p>
    </div>
    <div class="exam-group fade-up open">
      <div class="exam-group-header"><h4>Respostas pré-consulta levantadas</h4><div class="meta"><span>{len(rows)} respostas</span><span class="toggle">▾</span></div></div>
      <div class="exam-group-body">{"".join(rows)}</div>
    </div>
  </div>
</section>
"""


def render_technical_appendix(exames):
    by_g = {}
    for ex in exames:
        gid = ex.get("grupo", "outros") or "outros"
        by_g.setdefault(gid, []).append(ex)

    grupos_html = []
    grupos_renderizados = set()
    for gid, gnome in GRUPOS_DEF:
        items = by_g.get(gid, [])
        if not items:
            continue
        grupos_renderizados.add(gid)
        rows = []
        alterados = 0
        for ex in items:
            sev = ex.get("status", "ok")
            if sev in ("crit", "alert", "low"):
                alterados += 1
            rows.append(
                f'<div class="exam-row" data-sev="{sev}">'
                f'<div class="e-nome">{safe_html(ex["nome"])}</div>'
                f'<div class="e-valor">{safe_html(ex["valor"])} '
                f'<span class="e-unit">{safe_html(ex.get("unit",""))}</span></div>'
                f'<div class="e-ref">{safe_html(ex.get("ref","—"))}</div>'
                f'<div class="e-status">{sev}</div></div>'
            )
        grupos_html.append(
            f'<div class="exam-group fade-up open">'
            f'<div class="exam-group-header"><h4>{safe_html(gnome)}</h4>'
            f'<div class="meta"><span>{alterados}/{len(items)} alterados</span>'
            f'<span class="toggle">▾</span></div></div>'
            f'<div class="exam-group-body"><div class="exam-table-head"><span>Exame</span><span>Valor</span><span>Referência</span><span>Status</span></div>{"".join(rows)}</div></div>'
        )
    # Segurança de cobertura: qualquer grupo não mapeado também entra no apêndice.
    for gid in sorted(set(by_g.keys()) - grupos_renderizados):
        items = by_g.get(gid, [])
        if not items:
            continue
        rows = []
        alterados = 0
        for ex in items:
            sev = ex.get("status", "ok")
            if sev in ("crit", "alert", "low"):
                alterados += 1
            rows.append(
                f'<div class="exam-row" data-sev="{sev}">'
                f'<div class="e-nome">{safe_html(ex["nome"])}</div>'
                f'<div class="e-valor">{safe_html(ex["valor"])} '
                f'<span class="e-unit">{safe_html(ex.get("unit", ""))}</span></div>'
                f'<div class="e-ref">{safe_html(ex.get("ref", "—"))}</div>'
                f'<div class="e-status">{sev}</div></div>'
            )
        grupos_html.append(
            f'<div class="exam-group fade-up open">'
            f'<div class="exam-group-header"><h4>{safe_html(gid.title())}</h4>'
            f'<div class="meta"><span>{alterados}/{len(items)} alterados</span>'
            f'<span class="toggle">▾</span></div></div>'
            f'<div class="exam-group-body"><div class="exam-table-head"><span>Exame</span><span>Valor</span><span>Referência</span><span>Status</span></div>{"".join(rows)}</div></div>'
        )

    return f"""
<section id="technical-appendix" class="section technical-appendix">
  <div class="wrap">
    <h2>Apêndice técnico — painel completo</h2>
    <div class="appendix-controls">
      <p class="lead">Painel laboratorial completo organizado por sistema. Disponível para argumentação médica detalhada e auditoria clínica. Os grupos já abrem por padrão para evitar falha de interação no visualizador.</p>
      <button class="appendix-toggle-all">Recolher todos</button>
    </div>
    {"".join(grupos_html)}
  </div>
</section>
"""


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

# ==========================================================================
# DISC — Variações de copy por perfil do paciente (V2.10)
# ==========================================================================
DISC_TEXTOS = {
    "hero_h1": {
        "default": '{primeiro}, seus exames e seu questionário contam a mesma história: <span style="color:var(--gold-dark)">o problema não parece ser falta de esforço</span>, mas falta de acompanhamento integrado.',
        "D": '{primeiro}, seus exames mostram exatamente onde está o problema. <span style="color:var(--gold-dark)">A decisão certa precisa ser objetiva</span> — vamos direto ao caminho mais previsível.',
        "I": '{primeiro}, antes dos números, vamos olhar pra você. <span style="color:var(--gold-dark)">A boa notícia é que o problema não é falta de esforço seu</span> — só faltou alguém caminhar junto.',
        "S": '{primeiro}, vamos olhar com calma para o seu caso. <span style="color:var(--gold-dark)">Seus exames mostram pontos que pedem cuidado contínuo</span> — sem pressa, mas com atenção planejada.',
        "C": '{primeiro}, seu painel laboratorial e seu questionário convergem. <span style="color:var(--gold-dark)">Os dados sugerem a estratégia clínica mais previsível</span> para o seu perfil funcional.',
    },
    "diag_lead": {
        "default": "Antes de mostrar todos os exames, este é o resumo clínico do seu caso — o que decide o plano.",
        "D": "Resumo clínico direto. O que decide o plano em uma página.",
        "I": "Antes dos detalhes, vamos olhar para o quadro do seu caso — o que importa entender juntos.",
        "S": "Um retrato calmo do seu momento, antes de entrarmos nos detalhes.",
        "C": "Síntese clínica do caso integrando questionário, exames e correlação funcional.",
    },
    "tese_clinica": {
        "default": "Quando sintomas e marcadores apontam na mesma direção, o plano precisa ser <strong>acompanhado, medido e ajustado</strong>.",
        "D": "Sinais simultâneos no quadro. <strong>Acompanhamento estruturado é a recomendação clínica direta</strong> — métricas claras, ajustes guiados por dados.",
        "I": "Quando o que você sente e o que os exames mostram apontam pra mesma direção, fica claro que <strong>o cuidado precisa ser conjunto</strong> — você caminhando com a gente.",
        "S": "Os sinais nos exames pedem <strong>leitura conjunta e acompanhamento contínuo</strong>. Não é urgência — é prevenção atenta, no seu ritmo.",
        "C": "Biomarcadores e clínica convergem. A literatura e a experiência clínica recomendam <strong>acompanhamento estruturado com reavaliações periódicas</strong> baseadas em dados.",
    },
    "diag_recomendacao": {
        "default": "Minha recomendação para o seu caso é <strong>acompanhamento estruturado</strong>. A previsibilidade do resultado depende dos ajustes que faremos juntos durante o processo.",
        "D": "Recomendação direta: <strong>acompanhamento estruturado</strong>, com métricas trimestrais e ajustes baseados em resposta clínica. Resultado mais previsível para o seu perfil.",
        "I": "Minha recomendação é <strong>caminharmos juntos</strong> nos próximos 180 dias. Você não vai estar sozinho — equipe completa, ajustes feitos com você, sem pular etapas.",
        "S": "A recomendação é <strong>caminharmos com calma, em fases</strong>. Acompanhamento estruturado, equipe ao seu lado, mudanças graduais e planejadas.",
        "C": "Recomendação clínica: <strong>acompanhamento estruturado</strong> em 180 dias com 4 reavaliações laboratoriais. Decisões guiadas por dados objetivos e evidências.",
    },
    "leitura_lead": {
        "default": "Como seu quadro clínico se conecta — questionário, exames e o que isso significa para a estratégia de acompanhamento.",
        "D": "Como o quadro se conecta. Quatro blocos diretos antes da recomendação.",
        "I": "Vamos olhar juntos como tudo se conecta — o que você sente, o que os exames mostram, e o que faz sentido fazer.",
        "S": "Vamos com calma pelo seu quadro: o que ele mostra e como podemos cuidar disso de forma planejada.",
        "C": "Análise integrada do caso — quatro blocos correlacionando dados clínicos, biomarcadores e trajetória esperada.",
    },
    "leitura_b1_body": {
        "default": "Questionário e exames formam o retrato funcional do seu momento. É a partir desse retrato — não de um protocolo padrão — que se constrói o plano.",
        "D": "Questionário e exames = retrato funcional do momento. O plano sai daqui — sem protocolo de prateleira.",
        "I": "Tudo o que você nos contou e tudo o que os exames mostram formam o seu retrato. É a partir dele — do seu, único — que vamos cuidar juntos.",
        "S": "Seu questionário e seus exames juntos mostram onde você está hoje. É calmo, é claro — é o ponto de partida planejado.",
        "C": "Integração de dados clínicos (questionário) e laboratoriais (exames) compõe o estado funcional atual. O plano deriva diretamente desse perfil individualizado.",
    },
    "leitura_b1_alinhamento": {
        "default": "{primeiro}, esse resumo descreve bem o ciclo que você vem vivendo?",
        "D": "{primeiro}, esse resumo descreve o seu caso?",
        "I": "{primeiro}, esse resumo conta o ciclo que você vem vivendo? Faz sentido pra você?",
        "S": "{primeiro}, esse retrato faz sentido com o que você está vivendo?",
        "C": "{primeiro}, esse resumo está alinhado com a sua percepção do quadro?",
    },
    "leitura_b2_body": {
        "default": "Cada marcador abaixo carrega uma leitura clínica e se conecta a sintomas relatados — peças do mesmo quadro funcional.",
        "D": "Cada marcador conecta exame e sintoma. Peças do mesmo quadro — sem dispersão.",
        "I": "Cada um desses marcadores conta uma parte da história — não são números soltos, são pistas do que você sente.",
        "S": "Vamos com calma: cada marcador abaixo se relaciona com algo que você sente. Tudo conectado, sem complicar.",
        "C": "Cada biomarcador apresenta correlação clínica documentada com sintomas funcionais — leitura sistêmica integrada.",
    },
    "leitura_b2_alinhamento": {
        "default": "Você enxerga esses pontos como peças do mesmo quadro?",
        "D": "Faz sentido tratar tudo junto, ou ainda enxerga separado?",
        "I": "Você consegue ver como esses pontos conversam entre si?",
        "S": "Faz sentido pra você esses pontos como parte de um mesmo conjunto?",
        "C": "Os marcadores podem ser interpretados como peças de um mesmo quadro funcional. Concorda?",
    },
    "leitura_b3_body": {
        "default": "Sem ação clínica integrada, o cenário tende a <strong>menor previsibilidade e mais ajustes necessários</strong> ao longo do tempo.",
        "D": "Sem ação integrada: <strong>menor previsibilidade e mais ajustes ao longo do tempo</strong>. É a tendência fisiológica conhecida.",
        "I": "Imaginando como você pode se sentir daqui a alguns meses sem mudar nada — o cenário tende a continuar igual ou se complicar um pouco.",
        "S": "Sem ação, o quadro tende a se manter ou pedir mais cuidado lá na frente. Calmamente — mas vale considerar.",
        "C": "Trajetória sem intervenção: <strong>redução de previsibilidade clínica e necessidade de ajustes mais complexos</strong> em horizonte de 6-12 meses.",
    },
    "leitura_b3_alinhamento": {
        "default": "Olhar 6 meses adiante sem mudança te preocupa o suficiente para agir agora?",
        "D": "Olhando 6 meses adiante sem mudança, vale agir agora?",
        "I": "Imaginando os próximos 6 meses, isso te incomoda o suficiente pra começarmos juntos?",
        "S": "Olhando alguns meses adiante, prefere agirmos com calma ou esperar mais?",
        "C": "Considerando a trajetória esperada nos próximos 6 meses, justifica intervenção clínica antecipada?",
    },
    "leitura_b4_body": {
        "default": "A diferença mora nos ajustes — o que muda na segunda, quarta, oitava semana conforme seu corpo responde. Por isso, a recomendação para o seu caso é <strong>acompanhamento médico estruturado</strong>, não orientação isolada.",
        "D": "A diferença mora nos <strong>ajustes baseados em resposta clínica</strong>. Por isso a recomendação é acompanhamento — não prescrição avulsa.",
        "I": "A diferença está nos ajustes feitos junto com você ao longo do caminho. Por isso minha recomendação é <strong>acompanhamento</strong> — pra você não se sentir sozinho na jornada.",
        "S": "O segredo está nos pequenos ajustes feitos com calma ao longo das semanas. Por isso a recomendação é <strong>acompanhamento estruturado</strong>, em fases planejadas.",
        "C": "Resultado clínico depende de ajustes iterativos baseados em resposta individual. Por isso a recomendação é <strong>acompanhamento estruturado</strong> com cadência definida.",
    },
    "leitura_b4_alinhamento": {
        "default": "{primeiro}, você concorda que esse caminho exige acompanhamento e não apenas uma prescrição?",
        "D": "{primeiro}, aceita que a recomendação é acompanhamento, não prescrição?",
        "I": "{primeiro}, faz sentido pra você termos esse caminho juntos, com acompanhamento?",
        "S": "{primeiro}, se sente confortável com essa ideia de acompanhamento gradual?",
        "C": "{primeiro}, a recomendação clínica é acompanhamento estruturado — concorda com essa estratégia?",
    },
    "cta_frame": {
        "default": "O próximo passo é escolher se faz sentido iniciar agora um <strong>acompanhamento estruturado</strong>, com leitura clínica, equipe e ajustes ao longo do caminho.",
        "D": "Próximo passo objetivo: iniciar agora <strong>acompanhamento estruturado</strong> — leitura clínica, equipe, ajustes guiados por dados.",
        "I": "O próximo passo é decidir se vamos <strong>caminhar juntos</strong> a partir de agora — você não vai estar sozinho na jornada.",
        "S": "Sem pressa pra decidir. Quando fizer sentido, podemos começar com <strong>calma e em fases</strong>, com a equipe sempre por perto.",
        "C": "Próximo passo informado: iniciar <strong>acompanhamento estruturado de 180 dias</strong> com 4 reavaliações laboratoriais e ajustes evidence-based.",
    },
    "cta_recomendado_h3": {
        "default": "Começar assistido",
        "D": "Iniciar acompanhamento agora",
        "I": "Caminhar junto com a equipe",
        "S": "Começar com calma, em fases",
        "C": "Acompanhamento clínico estruturado",
    },
    "cta_recomendado_desc": {
        "default": "180 dias com diagnóstico, protocolo individualizado, equipe completa, ajustes baseados em resposta clínica e reavaliações trimestrais. {primeiro}, é o caminho mais previsível para o seu caso.",
        "D": "180 dias: diagnóstico, protocolo individualizado, equipe, ajustes guiados por dados, reavaliações trimestrais. {primeiro}, caminho mais previsível para o seu perfil.",
        "I": "{primeiro}, vamos juntos por 180 dias — protocolo feito pra você, equipe acolhendo cada passo, ajustes feitos com cuidado conforme você responde. Você não estará sozinho.",
        "S": "{primeiro}, 180 dias planejados em fases — diagnóstico, protocolo individualizado, equipe ao seu lado, ajustes graduais, reavaliações trimestrais. Sem pressa, com cuidado.",
        "C": "{primeiro}, 180 dias com diagnóstico funcional, protocolo individualizado evidence-based, equipe multidisciplinar, ajustes guiados por resposta clínica e 4 reavaliações laboratoriais. Estratégia previsível e rastreável.",
    },
    "msg_whatsapp": {
        "default": "{primeiro}, segue a sua apresentação clínica individual com os principais pontos da nossa consulta. Qualquer dúvida, estamos à disposição.\n\n— Equipe Instituto Vital Slim",
        "D": "{primeiro}, segue a sua apresentação clínica. Caso queira avançar, podemos alinhar o próximo passo.\n\n— Equipe Instituto Vital Slim",
        "I": "{primeiro}, que bom poder cuidar de você! Segue a apresentação com tudo o que conversamos hoje. Qualquer coisa, estamos por aqui — não fique sozinho.\n\n— Equipe Instituto Vital Slim",
        "S": "{primeiro}, segue com calma a sua apresentação. Não há pressa para decidir — leia quando puder e qualquer dúvida, estamos por aqui.\n\n— Equipe Instituto Vital Slim",
        "C": "{primeiro}, segue a apresentação clínica completa, com painel laboratorial e leitura integrada do caso. Disponível para esclarecer qualquer dado técnico.\n\n— Equipe Instituto Vital Slim",
    },
}


def _detectar_perfil_disc(paciente, questionario):
    """Detecta perfil DISC primário (D/I/S/C) do paciente.

    Procura nos campos: paciente.disc, paciente.discPerfil, questionario.dados.disc,
    questionario.dados.discPerfil, questionario.dados.perfilDisc.
    Aceita formas: 'D', 'Dominante', 'Dominante / Influente' (usa primeiro).
    Retorna 'default' se não detectar.
    """
    raw = ""
    for source in (paciente, (questionario or {}).get("pre-consulta", {}).get("dados", {}),
                   (questionario or {}).get("dados", {}) if isinstance(questionario, dict) else {}):
        if not isinstance(source, dict):
            continue
        for key in ("discPerfil", "perfilDisc", "disc_perfil", "disc"):
            if key in source and source[key]:
                v = source[key]
                # Pula se nao for string (ex: 'disc' eh dict com 20 respostas {q1, q2, ...})
                if not isinstance(v, str):
                    continue
                raw = v.strip()
                if raw:
                    break
        if raw:
            break
    if not raw:
        return "default"
    raw_upper = raw.upper()
    # Direta
    if raw_upper[0] in ("D", "I", "S", "C") and (len(raw_upper) == 1 or raw_upper[1] in (" ", "/", "-", ",", ":")):
        return raw_upper[0]
    # Por palavra-chave
    mapa = {
        "DOMINANT": "D", "DOMINANTE": "D",
        "INFLU": "I", "INFLUEN": "I", "INFLUENT": "I",
        "ESTAVEL": "S", "ESTÁVEL": "S", "STABLE": "S", "STEADY": "S",
        "CONSCIENC": "C", "CAUTELOSO": "C", "CAUTIOUS": "C",
        "ANALITIC": "C", "ANALÍTIC": "C", "CONFORM": "C",
    }
    for kw, letra in mapa.items():
        if kw in raw_upper:
            return letra
    return "default"


def _t_disc(chave, perfil, **kwargs):
    """Lookup de texto DISC. Fallback pra 'default' se chave/perfil não existirem."""
    bloco = DISC_TEXTOS.get(chave, {})
    texto = bloco.get(perfil) or bloco.get("default", "")
    if kwargs:
        try:
            texto = texto.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return texto



def render_apresentacao_v10(paciente, questionario=None, exames=None, output_dir=None, versao_paciente=False, perfil_disc=None, bioimpedancia=None):
    """Renderiza a V2 da apresentação conforme briefing do Conselho Growth (2026-05-05)."""
    output_dir = Path(output_dir) if output_dir else Path("/root/cerebro-vital-slim/deliverables")
    output_dir.mkdir(parents=True, exist_ok=True)

    logo_b64 = img_b64(SITE_IMAGES / "logo-ivs-correta.png")
    if not logo_b64:
        logo_b64 = img_b64(SITE_IMAGES / "logo-ivs-transparente.png")
    dra_b64 = img_b64(SITE_IMAGES / "dra-daniely-hero.png")

    nome_completo = paciente.get("nome", "Paciente")
    paciente_full = {**paciente,
                     "idade": paciente.get("idade") or calcular_idade(paciente.get("dataNascimento"))}

    # === V2.7 — Versão paciente vs versão interna ===
    body_class = "versao-paciente" if versao_paciente else "versao-interna"
    doctor_objections_html = "" if versao_paciente else render_doctor_objections()
    # === V2.10 — Detectar perfil DISC (override manual ou auto do questionário) ===
    if perfil_disc not in ("D", "I", "S", "C", "default", None):
        perfil_disc = "default"
    if not perfil_disc:
        perfil_disc = _detectar_perfil_disc(paciente, questionario)

    # Telefone do paciente (se presente no questionário)
    paciente_tel = ""
    if questionario:
        _dados_q = questionario.get("pre-consulta", {}).get("dados", {}) if isinstance(questionario, dict) else {}
        if not _dados_q and isinstance(questionario, dict) and "dados" in questionario:
            _dados_q = questionario["dados"]
        paciente_tel = (paciente.get("telefone") or paciente.get("phone")
                        or _dados_q.get("telefone") or _dados_q.get("whatsapp") or "")
    paciente_tel = "".join(_c for _c in str(paciente_tel) if _c.isdigit())
    _primeiro = nome_completo.split()[0] if nome_completo else "Paciente"

    # Modal de envio (só na versão interna)
    modal_html = ""
    if not versao_paciente:
        _msg_default = _t_disc("msg_whatsapp", perfil_disc, primeiro=_primeiro)
        modal_html = (
            '<div class="send-modal" id="send-modal" hidden>'
            '<div class="send-modal-backdrop"></div>'
            '<div class="send-modal-card" role="dialog" aria-modal="true" aria-labelledby="send-modal-title">'
            '<button class="send-modal-close" aria-label="Fechar">&times;</button>'
            '<h3 id="send-modal-title">Enviar apresentação ao paciente</h3>'
            '<p class="send-modal-sub">A versão enviada não inclui o apêndice da médica.</p>'
            '<label class="send-field"><span>WhatsApp do paciente</span>'
            f'<input type="tel" id="send-tel" placeholder="55 71 99999-9999" value="{paciente_tel}" autocomplete="off"></label>'
            '<label class="send-field"><span>Mensagem</span>'
            f'<textarea id="send-msg" rows="5">{safe_html(_msg_default)}</textarea></label>'
            '<div class="send-actions">'
            '<button class="send-btn-primary" id="send-share" style="display:none;">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>'
            '<polyline points="16 6 12 2 8 6"/>'
            '<line x1="12" y1="2" x2="12" y2="15"/></svg>'
            'Compartilhar apresentação</button>'
            '<button class="send-btn-primary" id="send-download" style="display:none;">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
            '<polyline points="7 10 12 15 17 10"/>'
            '<line x1="12" y1="15" x2="12" y2="3"/></svg>'
            'Baixar HTML</button>'
            '<button class="send-btn-secondary" id="send-whatsapp">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6A8.4 8.4 0 0 1 12.5 3 8.5 8.5 0 0 1 21 11.5z"/></svg>'
            'WhatsApp</button>'
            '<button class="send-btn-secondary" id="send-copy">Copiar mensagem</button>'
            '</div>'
            '<p class="send-hint"><strong>Mobile:</strong> use <em>Compartilhar</em> para enviar a apresentação direto pelo WhatsApp do seu celular.<br><strong>Desktop:</strong> use <em>Baixar HTML</em> + <em>WhatsApp</em> e anexe o arquivo baixado na conversa.</p>'
            '</div></div>'
        )

    exames_proc = _process_exames(exames or [])
    levers = _selecionar_critical_levers(exames_proc, max_levers=5)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_html(nome_completo)} · Apresentação V2 · Instituto Vital Slim</title>
<meta name="description" content="Documento clínico individual — Dra. Daniely Freitas, CRM-BA 27.588">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body class="{body_class}">
{render_topbar(logo_b64, versao_paciente=versao_paciente)}
{render_progress_nav(versao_paciente=versao_paciente)}
<main>
{render_hero(paciente_full, dra_b64=dra_b64, perfil_disc=perfil_disc)}
{render_executive_diagnosis(paciente_full, levers, perfil_disc=perfil_disc)}
{render_patient_mirror(paciente_full, questionario)}
{render_bioimpedancia(bioimpedancia, paciente_full)}
{render_critical_levers(levers, perfil_disc=perfil_disc, questionario=questionario)}
{render_spin_guided(paciente_full, questionario, levers, perfil_disc=perfil_disc)}
{render_ivs_machine()}
{render_proof_by_process()}
{render_program_180()}
{render_inclusos()}
{render_decision_checklist(paciente_full)}
{render_final_cta(paciente_full, perfil_disc=perfil_disc)}
{render_technical_appendix(exames_proc)}
{render_questionnaire_appendix(questionario)}
{doctor_objections_html}
</main>
{modal_html}
<script>
{JS}
</script>
</body>
</html>
"""
    nome_slug = re.sub(r"[^a-z0-9-]", "", nome_completo.lower().replace(" ", "-").replace(".", ""))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = '-paciente-v10-' if versao_paciente else '-v10-'
    output_path = output_dir / f"apresentacao-{nome_slug}{suffix}{ts}.html"
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


if __name__ == "__main__":
    # Smoke test
    paciente = {
        "nome": "Erick Magalhaes Santos",
        "dataNascimento": int(datetime(1990, 9, 25).timestamp() * 1000),
        "sexo": "M",
        "idade": 35,
        "data_consulta": "05.05.2026",
    }
    exames = [
        {"nome": "HOMA-IR", "valor": "3,8", "unit": "", "ref": "<2.7", "status": "alert", "grupo": "glicidico"},
        {"nome": "HbA1c", "valor": "5,5", "unit": "%", "ref": "<5.4", "status": "alert", "grupo": "glicidico"},
        {"nome": "Vitamina D", "valor": "31", "unit": "ng/mL", "ref": "80 a 100", "status": "crit", "grupo": "vitaminas"},
        {"nome": "Prolactina", "valor": "24,7", "unit": "ng/mL", "ref": "4.04 a 15.2", "status": "crit", "grupo": "hormonal"},
        {"nome": "PCR-us", "valor": "3,49", "unit": "mg/L", "ref": "<3.0", "status": "alert", "grupo": "inflamatorio"},
    ]
    out = render_apresentacao_v10(paciente, {}, exames)
    print(f"OK {out}")
