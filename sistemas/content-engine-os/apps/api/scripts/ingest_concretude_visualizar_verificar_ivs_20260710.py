import sys
sys.path.insert(0, '/app')
from app.db import get_conn
from app.routers.external_learning import ensure_phase4_schema, _tenant_id, _upsert_items, ExternalContentIn

TRANSCRIPT = """Estava assistindo um podcast de um gringo aqui, e os caras falaram sobre escrever, né?
E ele falou que tem três perguntas que ele se faz para descobrir se ele está escrevendo um bom anúncio.
Se a comunicação está boa, achei muito foda.
A primeira pergunta é possível visualizar, a segunda é possível verificar, a terceira só eu posso falar isso.
Ele viu um anúncio que era: não consiga apenas um emprego, transforme a indústria.
Transforme a indústria: você consegue visualizar? Não. Você consegue verificar? Não. Só você pode falar isso? Não. Então qualquer outra pessoa pode falar.
Agora pega um anúncio bom: modelos de Londres e papais de Oregon usam New Balance. Você consegue visualizar? Consegue. É possível verificar? Sim. Só a New Balance pode falar das modelos de Londres usando New Balance.
Concretude na parada: quanto mais elementos concretos você coloca na sua comunicação e no seu anúncio, mais confiável você fica."""

item = ExternalContentIn(
    source_network="instagram",
    source_profile="@leonciox",
    external_id="instagram_reel_DZ-K5RhORxJ_concretude_exclusiva",
    url="https://www.instagram.com/reel/DZ-K5RhORxJ/",
    format="reels",
    caption=TRANSCRIPT,
    metrics={"likes": 7440, "comments": 98},
    raw_payload={
        "source_url": "https://www.instagram.com/reel/DZ-K5RhORxJ/?igsh=YW41YTBmZDgyOWx2",
        "caption_publica": "O podcast chama How I Write e a entrevista é com o Harry Dry.",
        "public_metrics_visible": {"likes": 7440, "comments": 98},
        "video_duration_s": 85.891995,
        "video_file": "/root/.hermes/profiles/joao/workspace/instagram_learning_DZ-K5RhORxJ_20260710/reel_DZ-K5RhORxJ_full.mp4",
        "intake_report": "/root/.openclaw/reports/ivs-video-intake/20260710-211545-reel_DZ-K5RhORxJ_full.mp4/relatorio.html",
        "learning_classification": "aplicar_amanha_testar_3_dias",
        "framework": ["visualizar", "verificar", "so_instituto_vital_slim"],
    },
)

with get_conn() as conn:
    ensure_phase4_schema(conn)
    tenant_id = _tenant_id(conn, "demo")
    rows = _upsert_items(conn, tenant_id, [item], "manual_instagram_reel_intake_joao")
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into opportunities (tenant_id, title, thesis, angle, score, source_type, status)
            select %s,%s,%s,%s,%s,'external_learning','new'
            where not exists (
              select 1 from opportunities where tenant_id=%s and source_type='external_learning' and title=%s
            )
            """,
            (
                tenant_id,
                "Checklist Visualizar-Verificar-Só Instituto Vital Slim",
                "Antes de aprovar um anúncio, ele precisa ser visualizável, verificável e proprietário do Instituto Vital Slim.",
                "Transformar hooks genéricos em cenas concretas + prova verificável + especificidade do método/cuidado IVS.",
                82,
                tenant_id,
                "Checklist Visualizar-Verificar-Só Instituto Vital Slim",
            ),
        )
print({"status":"ingested","rows":rows})
