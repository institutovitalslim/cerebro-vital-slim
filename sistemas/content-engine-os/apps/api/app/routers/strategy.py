from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/strategy", tags=["strategy"])


class ReuseMapRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    core_theme: str
    core_promise: str
    audience_base: str


@router.post("/reuse-map")
def reuse_map(payload: ReuseMapRequest) -> dict:
    theme = payload.core_theme.strip()
    promise = payload.core_promise.strip()
    audience = payload.audience_base.strip()

    return {
        "status": "generated",
        "core_theme": theme,
        "angles": [
            {
                "label": "quebra_de_mito",
                "thesis": f"Desconstruir uma crença comum sobre {theme.lower()}.",
            },
            {
                "label": "reframe_de_culpa",
                "thesis": f"Mostrar que o problema de {theme.lower()} não é falta de esforço, e sim contexto e mecanismo.",
            },
            {
                "label": "mecanismo_clinico",
                "thesis": f"Explicar o mecanismo por trás de {promise.lower()} sem prometer resultado mágico.",
            },
        ],
        "hooks": [
            f"Se você é {audience.lower()}, talvez o problema não seja disciplina.",
            f"O que quase ninguém te explica sobre {theme.lower()}.",
            f"Antes de tentar mais uma vez, entenda isso sobre {promise.lower()}.",
            f"O erro de conteúdo que faz {audience.lower()} ignorar sua mensagem.",
        ],
        "audiences": [
            f"{audience}",
            f"{audience} que já tentou de tudo",
            f"{audience} com rotina intensa e pouco tempo",
            f"{audience} que quer tratamento sério e não dica solta",
        ],
        "repurposing": [
            {
                "format": "reel",
                "goal": "atração",
                "instruction": "Abrir com dor ou mito e fechar com CTA de palavra-chave.",
            },
            {
                "format": "carrossel",
                "goal": "educação",
                "instruction": "Transformar o mecanismo em sequência de slides com progressão lógica.",
            },
            {
                "format": "stories",
                "goal": "aquecimento",
                "instruction": "Quebrar em frames curtos com enquete, prova e CTA.",
            },
            {
                "format": "anúncio",
                "goal": "conversão",
                "instruction": "Usar dor, mecanismo, filtro de público e CTA direto.",
            },
        ],
    }
