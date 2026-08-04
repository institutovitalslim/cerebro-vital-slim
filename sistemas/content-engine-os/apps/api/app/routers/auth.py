from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel

from app.db import get_conn
from app.auth_core import verify_password, hash_password, make_token, read_token

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE = "cos_session"
_MAXAGE = 7 * 24 * 3600


class LoginReq(BaseModel):
    email: str
    password: str


class ChangePwReq(BaseModel):
    current_password: str
    new_password: str


def _user_payload(u: dict) -> dict:
    return {
        "authenticated": True,
        "user": {"name": u.get("full_name"), "email": u.get("email"), "role": u.get("role")},
        "workspace": {"slug": u.get("slug"), "name": u.get("tname")},
    }


@router.post("/login")
def login(req: LoginReq, response: Response) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "select u.id::text as id, u.tenant_id::text as tenant_id, u.email, u.full_name, u.role, "
            "u.password_hash, t.slug, t.name as tname "
            "from users u join tenants t on t.id = u.tenant_id where lower(u.email)=lower(%s)",
            (req.email.strip(),),
        )
        u = cur.fetchone()
    if not u or not verify_password(req.password, u.get("password_hash")):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    token = make_token(u["id"], u["tenant_id"], u["email"], _MAXAGE)
    response.set_cookie(COOKIE, token, max_age=_MAXAGE, httponly=True, secure=True,
                        samesite="lax", path="/")
    return _user_payload(u)


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.post("/change-password")
def change_password(req: ChangePwReq, request: Request) -> dict:
    payload = read_token(request.cookies.get(COOKIE))
    if not payload:
        raise HTTPException(status_code=401, detail="não autenticado")
    if len((req.new_password or "")) < 8:
        raise HTTPException(status_code=400, detail="A nova senha precisa ter ao menos 8 caracteres.")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("select password_hash from users where id=%s", (payload.get("uid"),))
        u = cur.fetchone()
        if not u or not verify_password(req.current_password, u.get("password_hash")):
            raise HTTPException(status_code=400, detail="Senha atual incorreta.")
        cur.execute("update users set password_hash=%s where id=%s",
                    (hash_password(req.new_password), payload.get("uid")))
    return {"ok": True}


@router.get("/session")
def session(request: Request) -> dict:
    payload = read_token(request.cookies.get(COOKIE))
    if not payload:
        return {"authenticated": False}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "select u.full_name, u.email, u.role, t.slug, t.name as tname "
            "from users u join tenants t on t.id = u.tenant_id where u.id=%s",
            (payload.get("uid"),),
        )
        u = cur.fetchone()
    if not u:
        return {"authenticated": False}
    return _user_payload(u)
