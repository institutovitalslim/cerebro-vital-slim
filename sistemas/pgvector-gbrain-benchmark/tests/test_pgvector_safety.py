import pytest

from ivs_pgvector_bench.pgvector_backend import PgvectorBackend

SAFE_DSN = "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark"


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://ivs_benchmark:***@db.internal:5432/ivs_benchmark?application_name=ivs_pgvector_benchmark",
        "postgresql://postgres:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark",
        "postgresql://ivs_benchmark:***@127.0.0.1:5432/ivs_benchmark?application_name=ivs_pgvector_benchmark",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/production?application_name=ivs_pgvector_benchmark",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&hostaddr=203.0.113.10",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&options=-c%20statement_timeout%3D0",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&sslmode=disable",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&passfile=/tmp/evil",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&connect_timeout=99",
        "postgresql://ivs_benchmark:***@127.0.0.1:55432/ivs_benchmark?application_name=ivs_pgvector_benchmark&service=evil",
    ],
)
def test_backend_rejects_any_dsn_outside_the_exact_ephemeral_sandbox(dsn):
    with pytest.raises(ValueError, match="ephemeral sandbox"):
        PgvectorBackend(dsn=dsn)


@pytest.mark.parametrize("dimensions", ["384", True, 7, 4097])
def test_backend_rejects_invalid_or_injectable_dimensions(dimensions):
    with pytest.raises((TypeError, ValueError)):
        PgvectorBackend(dsn=SAFE_DSN, dimensions=dimensions)


def test_backend_accepts_only_validated_dimension_and_sandbox_marker():
    backend = PgvectorBackend(dsn=SAFE_DSN, dimensions=384)
    assert backend.dimensions == 384
