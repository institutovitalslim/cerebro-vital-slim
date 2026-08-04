#!/usr/bin/env python3
"""Extrator de bioimpedância via LLM (OpenAI gpt-4o + Vision + Structured Outputs).

O PDF de bioimpedância (modelo Omie/InBody) é um dashboard visual com gauges,
gráficos e valores — pdftotext não preserva semântica. Solução: converter pra
imagem (pdftoppm) e mandar pra gpt-4o-vision com schema strict.

Uso:
    extrair_bioimpedancia(pdf_path, paciente_meta={"sexo": "F", "idade": 49})
    extrair_bioimpedancia_drive(pdf_id, paciente_meta)

Retorna dict no formato consumido por render_bioimpedancia() em gerar_apresentacao_v10.py.
"""
import os
import json
import base64
import subprocess
import tempfile
from openai import OpenAI


def _load_api_key():
    for p in ["/root/.openclaw/secure/openai.env", "/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val.startswith("sk-"):
                        return val
    return os.environ.get("OPENAI_API_KEY", "")


_API_KEY = _load_api_key()
MODEL = "gpt-4o"  # Vision necessário

# Schema do dict retornado — bate com o que render_bioimpedancia() espera
BIO_SCHEMA = {
    "type": "object",
    "properties": {
        "data_avaliacao": {"type": ["string", "null"], "description": "Data e hora da avaliação atual (ex: '15/05/2025 às 15:10')"},
        "data_referencia": {"type": ["string", "null"], "description": "Data e hora da avaliação anterior se houver comparativo, senão null"},
        "peso": {"type": ["string", "null"], "description": "Peso atual em kg, formato com vírgula (ex: '68,5')"},
        "altura": {"type": ["string", "null"], "description": "Altura em cm (ex: '154')"},
        "imc": {"type": ["string", "null"], "description": "IMC com vírgula (ex: '28,9')"},
        "tmb": {"type": ["string", "null"], "description": "Taxa Metabólica Basal em kcal/24h (ex: '1.181' ou '1181')"},
        "gordura": {
            "type": "object",
            "properties": {
                "massa": {"type": ["string", "null"], "description": "Massa gorda em kg"},
                "pct": {"type": ["string", "null"], "description": "% Gordura corporal"},
                "delta_pct": {"type": ["string", "null"], "description": "Variação em pontos percentuais vs avaliação anterior, com sinal (ex: '-6,5' ou '+1,2'). Null se sem comparativo."}
            },
            "required": ["massa", "pct", "delta_pct"],
            "additionalProperties": False
        },
        "hidratacao": {
            "type": "object",
            "properties": {
                "agua_total": {"type": ["string", "null"], "description": "Água Corporal Total em litros"},
                "agua_total_pct": {"type": ["string", "null"], "description": "Água corporal total em % do peso"},
                "indice": {"type": ["string", "null"], "description": "Índice de hidratação (cm/ohms × 10)"},
                "agua_massa_magra": {"type": ["string", "null"], "description": "% Água na massa magra"}
            },
            "required": ["agua_total", "agua_total_pct", "indice", "agua_massa_magra"],
            "additionalProperties": False
        },
        "agua_celular": {
            "type": "object",
            "properties": {
                "intra": {"type": ["string", "null"], "description": "Água intracelular em litros"},
                "intra_pct": {"type": ["string", "null"], "description": "% Água intracelular"},
                "extra": {"type": ["string", "null"], "description": "Água extracelular em litros"},
                "extra_pct": {"type": ["string", "null"], "description": "% Água extracelular"}
            },
            "required": ["intra", "intra_pct", "extra", "extra_pct"],
            "additionalProperties": False
        },
        "massa": {
            "type": "object",
            "properties": {
                "magra_kg": {"type": ["string", "null"], "description": "Massa magra em kg"},
                "magra_pct": {"type": ["string", "null"], "description": "% Massa magra"},
                "muscular_kg": {"type": ["string", "null"], "description": "Massa muscular em kg"},
                "muscular_pct": {"type": ["string", "null"], "description": "% Massa muscular"},
                "razao_musc_gord": {"type": ["string", "null"], "description": "Razão músculo/gordura (kg músculo / kg gordura)"},
                "razao_delta": {"type": ["string", "null"], "description": "Variação da razão vs avaliação anterior com sinal (ex: '+0,2'). Null se sem comparativo."}
            },
            "required": ["magra_kg", "magra_pct", "muscular_kg", "muscular_pct", "razao_musc_gord", "razao_delta"],
            "additionalProperties": False
        },
        "celular": {
            "type": "object",
            "properties": {
                "angulo_fase": {"type": ["string", "null"], "description": "Ângulo de fase em graus"},
                "angulo_delta": {"type": ["string", "null"], "description": "Variação do ângulo de fase vs avaliação anterior com sinal. Null se sem comparativo."},
                "idade_celular": {"type": ["string", "null"], "description": "Idade celular estimada em anos"},
                "idade_cronologica": {"type": ["string", "null"], "description": "Idade cronológica em anos (idade real)"}
            },
            "required": ["angulo_fase", "angulo_delta", "idade_celular", "idade_cronologica"],
            "additionalProperties": False
        }
    },
    "required": ["data_avaliacao", "data_referencia", "peso", "altura", "imc", "tmb",
                 "gordura", "hidratacao", "agua_celular", "massa", "celular"],
    "additionalProperties": False
}


SYSTEM_PROMPT = """Você é um extrator estruturado de dados de bioimpedância elétrica do Instituto Vital Slim.

O laudo é um dashboard com 6 quadrantes (Gordura, Hidratação, Água Intra/Extra Celular, Massa Magra/Muscular, Peso/Altura/TMB, Análise celular) e gauges visuais.

Regras de extração:
- Mantenha valores no formato brasileiro com VÍRGULA decimal (ex: "27,0", "39,4").
- Se houver comparativo (texto "comparado com" + data), preencha data_referencia e os campos delta (delta_pct, razao_delta, angulo_delta) com sinal (+ ou -).
- Se NÃO houver comparativo, todos os campos delta_* e data_referencia devem ser null.
- TMB sempre em kcal/24h.
- Use null quando o campo estiver ausente ou ilegível — não invente valores.
- Razão músculo/gordura é o número grande na seção "Massa Magra e Muscular" (ex: 0,7 ou 1,8).
- Idade celular fica na seção "Análise celular" — pode ser maior que a cronológica.

Responda APENAS em JSON válido conforme o schema."""


def _pdf_to_image_b64(pdf_path: str, dpi: int = 150) -> str:
    """Converte primeira página do PDF em JPEG base64."""
    with tempfile.TemporaryDirectory() as tmp:
        out_prefix = os.path.join(tmp, "page")
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-jpeg", "-f", "1", "-l", "1", pdf_path, out_prefix],
            check=True, capture_output=True
        )
        # pdftoppm gera page-1.jpg
        img_path = out_prefix + "-1.jpg"
        if not os.path.exists(img_path):
            raise RuntimeError(f"pdftoppm não gerou {img_path}")
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")


def extrair_bioimpedancia(pdf_path: str, paciente_meta: dict = None, model: str = MODEL) -> dict:
    """Extrai bioimpedância via gpt-4o vision.

    Args:
        pdf_path: caminho local do PDF de bioimpedância
        paciente_meta: dict com 'sexo' (M|F) e 'idade' — usado pra contexto

    Returns:
        dict no formato consumido por render_bioimpedancia()
    """
    if not _API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada")

    img_b64 = _pdf_to_image_b64(pdf_path)

    sexo = (paciente_meta or {}).get("sexo", "")
    idade = (paciente_meta or {}).get("idade", "")
    user_msg = f"Extraia os dados desta bioimpedância. Paciente: sexo={sexo}, idade={idade}."

    client = OpenAI(api_key=_API_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": user_msg},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}", "detail": "high"}}
            ]}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "bioimpedancia", "schema": BIO_SCHEMA, "strict": True}
        },
        temperature=0.0,
    )
    out = json.loads(resp.choices[0].message.content)
    # Anexa a imagem (base64 JPEG) pra renderer embedar no HTML
    out["_imagem_b64"] = img_b64
    return out


def baixar_pdf_drive(pdf_id: str, dest: str) -> bool:
    """Baixa PDF do Drive via gog CLI."""
    env = {
        **os.environ,
        "GOG_ACCOUNT": "medicalcontabilidade@gmail.com",
        "GOG_KEYRING_PASSWORD": os.environ.get("GOG_KEYRING_PASSWORD", "Tf100314@!"),
    }
    r = subprocess.run(
        ["/usr/local/bin/gog", "drive", "download", pdf_id],
        env=env, capture_output=True, text=True
    )
    if r.returncode != 0:
        return False
    # Localiza arquivo baixado
    cache = "/root/.config/gogcli/drive-downloads"
    for fn in os.listdir(cache):
        if fn.startswith(pdf_id):
            src = os.path.join(cache, fn)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            subprocess.run(["cp", src, dest], check=True)
            return True
    return False


def extrair_bioimpedancia_drive(pdf_id: str, paciente_meta: dict = None) -> dict:
    """Baixa do Drive e extrai. Lida com cleanup do arquivo temporário."""
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "bio.pdf")
        if not baixar_pdf_drive(pdf_id, pdf_path):
            raise RuntimeError(f"Falha ao baixar PDF {pdf_id}")
        return extrair_bioimpedancia(pdf_path, paciente_meta)


def detectar_pdf_bioimpedancia(lista_pdfs: list) -> dict:
    """Encontra o PDF de bioimpedância mais recente na lista do Drive.

    Estratégia: nome contém 'bio' (case insensitive). Retorna o mais recente
    pela ordem do `modifiedTime`.
    """
    candidatos = [
        p for p in lista_pdfs
        if "bio" in str(p.get("nome", "")).lower()
        and "nf" not in str(p.get("nome", "")).lower()  # exclui Notas Fiscais
    ]
    if not candidatos:
        return None
    # Já vem ordenado por modifiedTime DESC (buscar_exames_drive.py faz isso)
    return candidatos[0]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: extrair_bioimpedancia_llm.py <pdf_path> [sexo] [idade]")
        sys.exit(1)
    pdf = sys.argv[1]
    meta = {}
    if len(sys.argv) > 2:
        meta["sexo"] = sys.argv[2]
    if len(sys.argv) > 3:
        meta["idade"] = sys.argv[3]
    print(json.dumps(extrair_bioimpedancia(pdf, meta), indent=2, ensure_ascii=False))
