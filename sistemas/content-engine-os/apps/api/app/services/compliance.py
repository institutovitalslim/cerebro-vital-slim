from __future__ import annotations

import json
import re
from typing import Any

CAPTION_FOOTER = "Dra Daniely Freitas\nMédica, Farmacêutica e Professora de Medicina\nCRM-BA 27.588\n(Este conteúdo tem caráter meramente educativo e não substitui uma consulta médica.)"

CLINICAL_TOPICS = {
    "hormonios": ["hormônio", "hormônios", "menopausa", "libido", "testosterona", "estradiol", "progesterona", "tireoide", "trh"],
    "metabolismo": ["metabolismo", "resistência insulínica", "insulina", "glicemia", "inflamação", "gordura abdominal"],
    "emagrecimento": ["emagrecer", "emagrecimento", "perder peso", "obesidade", "glp-1", "tirzepatida", "semaglutida"],
    "tricologia": ["queda de cabelo", "tricologia", "cabelo", "alopecia", "ferritina"],
    "suplementos": ["creatina", "magnésio", "vitamina d", "suplemento", "glicina", "nattokinase"],
}

RED_FLAGS = [
    ("promise_result", r"\b(garant\w*|resultado garantido|vai perder|perca \d+|emagre[çc]a \d+|cura\w*|milagre|revolucion[aá]rio|definitivo)\b", "Remover promessa/garantia/cura. Trocar por linguagem educativa e acompanhamento individual."),
    ("diagnosis", r"\b(voc[eê] tem|isso [ée]|sinal claro de|diagn[oó]stico de)\b", "Não diagnosticar em conteúdo público. Usar 'pode estar associado' e orientar avaliação médica."),
    ("prescription", r"\b(tome|use|dose de|mg por dia|prescrev\w*|protocolo para todos)\b", "Não prescrever dose/tratamento em conteúdo público. Direcionar para consulta."),
    ("before_after", r"\b(antes e depois|antes/depois|transforma[çc][aã]o)\b", "Antes/depois exige autorização, contexto e cuidado com promessa de resultado."),
    ("price_pressure", r"\b(s[oó] hoje|vagas? acabando|garanta agora|promo[çc][aã]o)\b", "Evitar urgência comercial agressiva em publicidade médica."),
]

REFERENCE_BANK = [
    {
        "topic": "hormonios",
        "title": "Menopause hormone therapy position statement",
        "authors": "The Menopause Society",
        "year": 2022,
        "evidence_level": "guideline",
        "link": "https://pubmed.ncbi.nlm.nih.gov/35797481/",
        "main_claim": "Sintomas e riscos da menopausa exigem avaliação individual; terapia hormonal depende de indicação, janela, risco e acompanhamento.",
    },
    {
        "topic": "metabolismo",
        "title": "Standards of Care in Diabetes",
        "authors": "American Diabetes Association",
        "year": 2024,
        "evidence_level": "guideline",
        "link": "https://diabetesjournals.org/care/issue/47/Supplement_1",
        "main_claim": "Resistência insulínica, glicemia e risco cardiometabólico devem ser avaliados com critérios clínicos e laboratoriais.",
    },
    {
        "topic": "emagrecimento",
        "title": "Pharmacologic Treatment of Overweight and Obesity in Adults",
        "authors": "Endocrine Society",
        "year": 2015,
        "evidence_level": "guideline",
        "link": "https://pubmed.ncbi.nlm.nih.gov/25590212/",
        "main_claim": "Tratamento de obesidade deve combinar avaliação clínica, acompanhamento e decisão individual sobre terapias.",
    },
    {
        "topic": "tricologia",
        "title": "Female pattern hair loss: clinical and pathophysiological review",
        "authors": "Review literature",
        "year": 2023,
        "evidence_level": "review",
        "link": "https://pubmed.ncbi.nlm.nih.gov/?term=female+pattern+hair+loss+review",
        "main_claim": "Queda capilar em mulheres pode ter múltiplos fatores e requer avaliação clínica/laboratorial individual.",
    },
    {
        "topic": "suplementos",
        "title": "International Society of Sports Nutrition position stand: creatine supplementation",
        "authors": "Kreider et al.",
        "year": 2017,
        "evidence_level": "position_stand",
        "link": "https://pubmed.ncbi.nlm.nih.gov/28615996/",
        "main_claim": "Creatina tem evidência para desempenho muscular; usos fora desse contexto exigem cuidado com extrapolação.",
    },
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def extract_content_blob(creative: dict[str, Any]) -> str:
    return "\n".join(
        normalize_text(creative.get(k))
        for k in ("title", "description", "caption", "script", "hashtags")
        if creative.get(k) is not None
    )


def detect_claims(text: str) -> list[dict[str, Any]]:
    low = text.lower()
    claims: list[dict[str, Any]] = []
    for topic, terms in CLINICAL_TOPICS.items():
        matched = [t for t in terms if t in low]
        if matched:
            claims.append({
                "topic": topic,
                "type": "clinical_claim",
                "matched_terms": matched[:6],
                "requires_source": True,
                "excerpt": _excerpt(text, matched[0]),
            })
    return claims


def _excerpt(text: str, term: str) -> str:
    low = text.lower()
    idx = low.find(term.lower())
    if idx < 0:
        return text[:180]
    start = max(0, idx - 80)
    end = min(len(text), idx + 160)
    return text[start:end].strip()


def detect_red_flags(text: str) -> list[dict[str, str]]:
    out = []
    low = text.lower()
    for code, pattern, suggestion in RED_FLAGS:
        if re.search(pattern, low, flags=re.I):
            out.append({"code": code, "severity": "high", "suggestion": suggestion})
    return out


def evidence_for_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topics = {c.get("topic") for c in claims}
    return [r for r in REFERENCE_BANK if r["topic"] in topics]


def assess_text(text: str) -> dict[str, Any]:
    claims = detect_claims(text)
    red_flags = detect_red_flags(text)
    references = evidence_for_claims(claims)
    missing_sources = [c for c in claims if c.get("requires_source") and not any(r["topic"] == c.get("topic") for r in references)]
    has_footer = "crm-ba 27.588" in text.lower() and "não substitui uma consulta médica" in text.lower()
    score = 100
    score -= 25 * len(red_flags)
    score -= 12 * len(missing_sources)
    if claims and not has_footer:
        score -= 10
    score = max(0, min(100, score))
    if red_flags:
        status = "blocked_until_revision"
        risk = "high"
    elif missing_sources:
        status = "needs_sources"
        risk = "medium"
    elif claims and not has_footer:
        status = "needs_disclaimer"
        risk = "medium"
    else:
        status = "approved_with_care"
        risk = "low"
    fixes = [f["suggestion"] for f in red_flags]
    if missing_sources:
        fixes.append("Adicionar fonte/evidência para claims clínicos antes de publicar.")
    if claims and not has_footer:
        fixes.append("Adicionar assinatura e disclaimer médico obrigatório na legenda.")
    if not fixes:
        fixes.append("Manter linguagem educativa e validar claims sensíveis antes de publicação.")
    return {
        "status": status,
        "risk_level": risk,
        "score": score,
        "claims": claims,
        "red_flags": red_flags,
        "missing_sources": missing_sources,
        "evidence": references,
        "has_required_footer": has_footer,
        "required_footer": CAPTION_FOOTER,
        "fixes": fixes,
        "governance": {
            "auto_publish": False,
            "auto_dm": False,
            "zapi_write": False,
            "clinical_claims_need_source": True,
            "human_review_required_for_medium_high": True,
        },
    }


def ensure_compliance_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("alter table scientific_sources add column if not exists topic text")
        cur.execute("alter table scientific_sources add column if not exists doi text")
        cur.execute("alter table scientific_sources add column if not exists pmid text")
        cur.execute(
            """
            create table if not exists compliance_assessments (
              id uuid primary key default gen_random_uuid(),
              tenant_id uuid not null references tenants(id) on delete cascade,
              creative_id uuid references creatives(id) on delete cascade,
              content_hash text not null,
              status text not null,
              risk_level text not null,
              score numeric(5,2) not null default 0,
              claims jsonb not null default '[]'::jsonb,
              red_flags jsonb not null default '[]'::jsonb,
              evidence jsonb not null default '[]'::jsonb,
              missing_sources jsonb not null default '[]'::jsonb,
              fixes jsonb not null default '[]'::jsonb,
              required_footer text,
              created_at timestamptz not null default now()
            )
            """
        )
        cur.execute("create index if not exists idx_compliance_assessments_creative on compliance_assessments(creative_id, created_at desc)")
        cur.execute("create index if not exists idx_compliance_assessments_status on compliance_assessments(tenant_id, status, risk_level)")
        for ref in REFERENCE_BANK:
            cur.execute(
                """
                insert into scientific_sources (tenant_id, title, authors, year, summary, link, main_claim, evidence_level, topic)
                select t.id, %s, %s, %s, %s, %s, %s, %s, %s
                from tenants t
                where t.slug='demo'
                  and not exists (
                    select 1 from scientific_sources s
                    where s.tenant_id=t.id and s.title=%s and coalesce(s.topic,'')=%s
                  )
                """,
                (ref["title"], ref["authors"], ref["year"], ref["main_claim"], ref["link"], ref["main_claim"], ref["evidence_level"], ref["topic"], ref["title"], ref["topic"]),
            )


def assess_creative(conn, creative_id: str) -> dict[str, Any] | None:
    ensure_compliance_schema(conn)
    with conn.cursor() as cur:
        cur.execute("select * from creatives where id=%s", (creative_id,))
        creative = cur.fetchone()
        if not creative:
            return None
        text = extract_content_blob(dict(creative))
        result = assess_text(text)
        cur.execute(
            """
            insert into compliance_assessments (
              tenant_id, creative_id, content_hash, status, risk_level, score, claims,
              red_flags, evidence, missing_sources, fixes, required_footer
            ) values (%s,%s,md5(%s),%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s::jsonb,%s::jsonb,%s)
            returning id::text as assessment_id, created_at
            """,
            (
                creative["tenant_id"], creative_id, text, result["status"], result["risk_level"], result["score"],
                json.dumps(result["claims"], ensure_ascii=False),
                json.dumps(result["red_flags"], ensure_ascii=False),
                json.dumps(result["evidence"], ensure_ascii=False),
                json.dumps(result["missing_sources"], ensure_ascii=False),
                json.dumps(result["fixes"], ensure_ascii=False),
                result["required_footer"],
            ),
        )
        row = cur.fetchone()
    return {**result, **dict(row), "creative_id": creative_id}
