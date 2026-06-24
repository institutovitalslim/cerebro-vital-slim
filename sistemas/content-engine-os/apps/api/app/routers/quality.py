from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.compliance import assess_text

router = APIRouter(prefix="/quality", tags=["quality"])


class QualityReviewRequest(BaseModel):
    content_type: str = Field(default="reel")
    niche: str = Field(default="medical")
    objective: str
    content_body: str
    cta: str | None = None


@router.post("/review")
def review(payload: QualityReviewRequest) -> dict:
    text = f"{payload.content_body} {payload.cta or ''}".lower()
    alerts: list[str] = []
    fixes: list[str] = []
    score = 92

    risky_patterns = [
        ("garant", "Remover promessa de garantia ou certeza de resultado."),
        ("cura", "Evitar claim de cura; trocar por melhora, investigação ou acompanhamento."),
        ("resultado em", "Remover promessa temporal rígida."),
        ("antes e depois", "Validar uso sensível de antes/depois e considerar prova alternativa."),
        ("sem esforço", "Evitar promessa irreal de facilidade total."),
    ]

    for pattern, suggestion in risky_patterns:
        if pattern in text:
            alerts.append(f"Risco detectado: {pattern}")
            fixes.append(suggestion)
            score -= 14

    if "médic" in payload.niche.lower() or payload.niche.lower() == "medical":
        fixes.append("Manter linguagem educativa, explicar mecanismo e usar CTA sem promessa agressiva.")

    status = "approved_with_care" if not alerts else "needs_revision"
    compliance = assess_text(f"{payload.content_body}\n{payload.cta or ''}")
    if compliance["risk_level"] == "high":
        status = "blocked_until_revision"
        score = min(score, compliance["score"])
    elif compliance["risk_level"] == "medium" and status == "approved_with_care":
        status = compliance["status"]
        score = min(score, compliance["score"])
    safer_cta = payload.cta or "Comente uma palavra-chave para receber o próximo passo."
    if "consulta" in safer_cta.lower() and "agora" in safer_cta.lower():
        safer_cta = "Se fizer sentido para você, comente uma palavra-chave para receber o próximo passo com mais clareza."

    return {
        "status": status,
        "score": max(score, 35),
        "alerts": alerts,
        "fixes": fixes,
        "safer_cta": safer_cta,
        "phase": "fase_5_scientific_compliance",
        "compliance": compliance,
    }
