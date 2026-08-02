import os

from ivs_pgvector_bench.pgvector_backend import PgvectorBackend


def test_pgvector_backend_installs_extension_indexes_and_retrieves_expected_document():
    dsn = os.environ["IVS_BENCH_PGVECTOR_DSN"]
    backend = PgvectorBackend(dsn=dsn, dimensions=256)
    docs = [
        {"id": "agenda", "title": "Confirmação de agenda", "body": "A Clara usa as opções Confirmo, Quero remarcar e Não vou conseguir."},
        {"id": "financeiro", "title": "Boletos Omie", "body": "O setor financeiro consulta boletos e conciliação no Omie."},
        {"id": "marketing", "title": "Reels", "body": "João coordena marketing, Reels e relatório de tráfego."},
    ]

    backend.reset_and_index(docs)
    result = backend.search("quais são as opções para confirmar a agenda", limit=3)

    assert backend.extension_version()
    assert backend.count() == 3
    assert result[0]["id"] == "agenda"
    assert result[0]["score"] > result[-1]["score"]
    plan = backend.index_plan("agenda confirmação", limit=3)
    assert plan["hnsw_index_available"] is True
    assert plan["default_plan"]
