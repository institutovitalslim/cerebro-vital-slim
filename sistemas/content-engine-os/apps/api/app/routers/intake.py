import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import get_conn

router = APIRouter(prefix="/intake", tags=["intake"])


class StrategyIntakeRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    clinic_name: str
    specialty: str
    city: str
    audience: str
    main_offer: str
    primary_pain: str
    desired_outcome: str
    authority_assets: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.post("/strategy")
def create_strategy_intake(payload: StrategyIntakeRequest) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, payload.tenant_slug)
        output = {
            "brand_core": {
                "clinic_name": payload.clinic_name,
                "specialty": payload.specialty,
                "city": payload.city,
                "offer": payload.main_offer,
            },
            "messaging_pillars": [
                f"Dor central: {payload.primary_pain}",
                f"Resultado desejado: {payload.desired_outcome}",
                f"Autoridade ativável: {', '.join(payload.authority_assets) if payload.authority_assets else 'prova clínica e educativa'}",
            ],
            "objections": [
                "isso já não funcionou para mim antes",
                "deve ser caro demais para minha realidade",
                "não tenho tempo para seguir um processo complexo",
            ],
            "first_actions": [
                "definir 3 temas principais de atração",
                "subir 1 peça de quebra de objeção",
                "criar 1 reel de mecanismo clínico",
                "derivar 1 carrossel e 3 stories do mesmo núcleo",
            ],
        }

        with conn.cursor() as cur:
            cur.execute(
                """
                insert into strategy_intakes (
                    tenant_id, clinic_name, specialty, city, audience, main_offer,
                    primary_pain, desired_outcome, authority_assets, constraints, output_payload
                ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)
                returning id, created_at
                """,
                (
                    tenant_id,
                    payload.clinic_name,
                    payload.specialty,
                    payload.city,
                    payload.audience,
                    payload.main_offer,
                    payload.primary_pain,
                    payload.desired_outcome,
                    json.dumps(payload.authority_assets),
                    json.dumps(payload.constraints),
                    json.dumps(output),
                ),
            )
            row = cur.fetchone()

    return {
        "status": "captured",
        "id": row["id"],
        "created_at": row["created_at"],
        "tenant_slug": payload.tenant_slug,
        "payload": output,
    }
