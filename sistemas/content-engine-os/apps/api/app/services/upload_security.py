import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

MIB = 1024 * 1024
MAX_ASSET_BYTES = 50 * MIB
MAX_IMAGE_BYTES = 20 * MIB
MAX_BROLL_VIDEO_BYTES = 250 * MIB
MAX_DRA_VIDEO_BYTES = 500 * MIB


async def save_upload_limited(
    upload: UploadFile,
    destination: str | Path,
    *,
    max_bytes: int,
    chunk_bytes: int = MIB,
) -> int:
    if max_bytes < 1 or chunk_bytes < 1:
        raise ValueError("upload limits must be positive")

    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.part")
    total = 0

    try:
        with temporary.open("xb") as output:
            while True:
                chunk = await upload.read(chunk_bytes)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"arquivo excede o limite de {max_bytes} bytes",
                    )
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        return total
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
