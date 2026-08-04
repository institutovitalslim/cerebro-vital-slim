import json
import mimetypes
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.db import get_conn
from app.services.upload_security import MAX_ASSET_BYTES, save_upload_limited

router = APIRouter(prefix="/assets", tags=["assets"])

STORAGE_ROOT = Path("/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets")
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)


def _tenant_id(conn, tenant_slug: str) -> str:
    with conn.cursor() as cur:
        cur.execute("select id from tenants where slug = %s", (tenant_slug,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"tenant '{tenant_slug}' not found")
    return row["id"]


@router.get("")
def list_assets(tenant_slug: str = "demo") -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, title, original_filename, mime_type, storage_path, file_size_bytes, asset_kind, tags, created_at
                from content_assets
                where tenant_id = %s
                order by created_at desc
                limit 100
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    return {"items": rows}


@router.post("/upload")
async def upload_asset(
    tenant_slug: str = Form("demo"),
    title: str = Form(...),
    asset_kind: str = Form("reference"),
    tags: str = Form(""),
    file: UploadFile = File(...),
) -> dict:
    with get_conn() as conn:
        tenant_id = _tenant_id(conn, tenant_slug)

        safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'asset.bin')}"
        tenant_dir = STORAGE_ROOT / tenant_slug
        tenant_dir.mkdir(parents=True, exist_ok=True)
        storage_path = tenant_dir / safe_name

        file_size = await save_upload_limited(
            file, storage_path, max_bytes=MAX_ASSET_BYTES
        )

        mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        tags_list = [v.strip() for v in tags.split(",") if v.strip()]

        with conn.cursor() as cur:
            cur.execute(
                """
                insert into content_assets (
                    tenant_id, title, original_filename, mime_type, storage_path, file_size_bytes, asset_kind, tags
                ) values (%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                returning id, created_at
                """,
                (
                    tenant_id,
                    title,
                    file.filename or safe_name,
                    mime_type,
                    str(storage_path),
                    file_size,
                    asset_kind,
                    json.dumps(tags_list),
                ),
            )
            row = cur.fetchone()

    return {
        "status": "uploaded",
        "id": row["id"],
        "created_at": row["created_at"],
        "title": title,
        "mime_type": mime_type,
        "file_size_bytes": file_size,
    }


@router.get("/{asset_id}/download")
def download_asset(asset_id: str) -> FileResponse:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select title, original_filename, mime_type, storage_path
                from content_assets
                where id = %s
                """,
                (asset_id,),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="asset not found")
    path = Path(row["storage_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="asset file missing")
    return FileResponse(path=str(path), media_type=row["mime_type"], filename=row["original_filename"])
