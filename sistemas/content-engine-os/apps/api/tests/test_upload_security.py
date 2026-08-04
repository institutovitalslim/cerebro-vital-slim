from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.services.upload_security import save_upload_limited


def test_upload_stream_is_saved_within_limit(tmp_path: Path) -> None:
    upload = UploadFile(filename="safe.bin", file=BytesIO(b"12345"))
    target = tmp_path / "safe.bin"

    size = __import__("asyncio").run(
        save_upload_limited(upload, target, max_bytes=5)
    )

    assert size == 5
    assert target.read_bytes() == b"12345"


def test_oversized_upload_is_rejected_and_partial_file_removed(tmp_path: Path) -> None:
    upload = UploadFile(filename="large.bin", file=BytesIO(b"123456"))
    target = tmp_path / "large.bin"

    with pytest.raises(HTTPException) as error:
        __import__("asyncio").run(
            save_upload_limited(upload, target, max_bytes=5, chunk_bytes=2)
        )

    assert error.value.status_code == 413
    assert not target.exists()
    assert not list(tmp_path.glob("*.part"))
