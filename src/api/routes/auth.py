"""Authentication endpoints — register, login, profile."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, limiter  # type: ignore[attr-defined]
from src.auth.dependencies import get_current_user
from src.auth.jwt import create_access_token, create_refresh_token, revoke_token_jti, verify_token
from src.models.user_account import UserAccount

router = APIRouter()

# Top 20 most common passwords — rejected at registration
_COMMON_PASSWORDS = {
    "password", "12345678", "123456789", "qwerty123", "password123",
    "admin123", "letmein", "welcome1", "monkey", "dragon",
    "abc123", "11111111", "123123123", "football", "iloveyou",
    "trustno1", "master", "sunshine", "shadow", "123qwe",
}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.lower() in _COMMON_PASSWORDS:
            raise ValueError("Password is too common — please choose a stronger one")
        # Require at least two character classes
        classes = 0
        if any(c.isupper() for c in v):
            classes += 1
        if any(c.islower() for c in v):
            classes += 1
        if any(c.isdigit() for c in v):
            classes += 1
        if any(not c.isalnum() for c in v):
            classes += 1
        if classes < 2:
            raise ValueError(
                "Password must include at least two of: uppercase, lowercase, digits, symbols"
            )
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, req: RegisterRequest, db: AsyncSession = Depends(get_db)):  # noqa: B008
    existing = await db.execute(
        text("SELECT id FROM user_accounts WHERE email = :email"),
        {"email": req.email},
    )
    if existing.fetchone():
        # Generic response — prevents email enumeration
        return {"message": "If this email is not registered, an account has been created"}

    password_hash, salt = UserAccount.hash_password(req.password)
    await db.execute(
        text("""INSERT INTO user_accounts (id, email, password_hash, password_salt)
                VALUES (gen_random_uuid(), :email, :hash, :salt)"""),
        {"email": req.email, "hash": password_hash, "salt": salt},
    )
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(500, "Registration failed, please try again")  # noqa: B904
    return {"message": "Account created"}


@router.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):  # noqa: B008
    result = await db.execute(
        text("SELECT id, email, password_hash, password_salt, role, failed_login_attempts, locked_until FROM user_accounts WHERE email = :email"),  # noqa: E501
        {"email": req.email},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(401, "Invalid credentials")

    # Account lockout: 5 failed attempts → 15-minute lock
    failed = int(row.failed_login_attempts or "0")
    if row.locked_until and row.locked_until > datetime.now(UTC):
        raise HTTPException(429, "Account temporarily locked. Try again later.")
    # Auto-unlock after lockout period expires
    if row.locked_until and row.locked_until <= datetime.now(UTC) and failed >= 5:
        failed = 0
        await db.execute(
            text("UPDATE user_accounts SET failed_login_attempts = '0', locked_until = NULL WHERE id = :id"),
            {"id": str(row.id)},
        )

    # verify_password is an instance method — reconstruct for check
    h, _ = UserAccount.hash_password(req.password, row.password_salt)
    if h != row.password_hash:
        new_failed = failed + 1
        locked = datetime.now(UTC) + timedelta(minutes=15) if new_failed >= 5 else None
        await db.execute(
            text("UPDATE user_accounts SET failed_login_attempts = :n, locked_until = :lu WHERE id = :id"),
            {"n": str(new_failed), "lu": locked, "id": str(row.id)},
        )
        await db.commit()
        if new_failed >= 5:
            raise HTTPException(429, "Account temporarily locked. Try again in 15 minutes.")
        raise HTTPException(401, "Invalid credentials")

    # Successful login — reset counter
    if failed > 0:
        await db.execute(
            text("UPDATE user_accounts SET failed_login_attempts = '0', locked_until = NULL WHERE id = :id"),
            {"id": str(row.id)},
        )
        await db.commit()

    access_token = create_access_token(str(row.id), role=row.role or "consumer")
    refresh_token = create_refresh_token(str(row.id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "email": row.email,
        "role": row.role or "consumer",
    }


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/auth/refresh")
@limiter.limit("5/minute")
async def refresh(request: Request, req: RefreshRequest, db: AsyncSession = Depends(get_db)):  # noqa: B008
    payload = await verify_token(req.refresh_token, check_revoked=True)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token")

    # Revoke the used refresh token (rotation)
    jti = payload.get("jti")
    if jti:
        await revoke_token_jti(jti)

    # Issue new tokens — look up current role from DB for freshness
    from sqlalchemy import text as sql_text
    result = await db.execute(
        sql_text("SELECT role FROM user_accounts WHERE id = :id"),
        {"id": payload["sub"]}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(401, "User not found")

    return {
        "access_token": create_access_token(payload["sub"], role=row.role),
        "refresh_token": create_refresh_token(payload["sub"]),
    }


@router.post("/auth/logout")
@limiter.limit("10/minute")
async def logout(
    request: Request,
    user: dict = Depends(get_current_user),  # noqa: B008
):
    """Revoke the current access token. The refresh token is revoked on next refresh."""
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if token:
        payload = await verify_token(token, check_revoked=False)
        if payload and payload.get("jti"):
            await revoke_token_jti(payload["jti"])
    return {"message": "Logged out"}


@router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):  # noqa: B008
    if user is None:
        raise HTTPException(401, "Authentication required")
    return {"id": user["id"], "email": user.get("email"), "role": user["role"]}
