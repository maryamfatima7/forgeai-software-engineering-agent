import base64
import hashlib
import hmac
import os
import re
import secrets
from datetime import UTC, datetime

from fastapi import Request, Response
from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.config import settings
from app.core.errors import ForgeAIError


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "forgeai_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


def _database_url() -> str:
    if (os.getenv("VERCEL") or os.getenv("RAILWAY_ENVIRONMENT")) and not os.getenv("AUTH_DATABASE_URL"):
        raise RuntimeError("AUTH_DATABASE_URL must be configured in production.")
    url = settings.auth_database_url or "sqlite:///./.forgeai_auth.db"
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


engine = create_engine(
    _database_url(),
    connect_args={"check_same_thread": False} if _database_url().startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
_local_session_secret = secrets.token_urlsafe(32)


def init_auth_db() -> None:
    Base.metadata.create_all(engine)


def normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
        raise ForgeAIError("invalid_email", "Enter a valid email address.")
    return normalized


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return "scrypt$16384$8$1${}${}".format(base64.urlsafe_b64encode(salt).decode(), base64.urlsafe_b64encode(digest).decode())


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_value, digest_value = encoded.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode())
        expected = base64.urlsafe_b64decode(digest_value.encode())
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError):
        return False


def _session_secret() -> bytes:
    if not settings.auth_session_secret and os.getenv("VERCEL"):
        raise ForgeAIError("auth_not_configured", "Authentication is not configured for this deployment.", 500)
    return (settings.auth_session_secret or _local_session_secret).encode("utf-8")


def _session_value(user_id: int) -> str:
    payload = str(user_id).encode("ascii")
    signature = hmac.new(_session_secret(), payload, hashlib.sha256).hexdigest()
    return f"{user_id}.{signature}"


def _session_user_id(value: str | None) -> int | None:
    if not value or "." not in value:
        return None
    user_value, signature = value.split(".", 1)
    if not user_value.isdigit():
        return None
    expected = hmac.new(_session_secret(), user_value.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    return int(user_value)


def set_session_cookie(response: Response, request: Request, user_id: int) -> None:
    secure = settings.auth_cookie_secure or request.url.scheme == "https"
    response.set_cookie(
        settings.auth_cookie_name,
        _session_value(user_id),
        max_age=settings.auth_session_max_age_seconds,
        httponly=True,
        secure=secure,
        samesite="none" if secure else "lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(settings.auth_cookie_name, path="/")


def user_response(user: User) -> dict[str, object]:
    return {"id": user.id, "full_name": user.full_name, "email": user.email}


def current_user(request: Request) -> User:
    user_id = _session_user_id(request.cookies.get(settings.auth_cookie_name))
    if user_id is None:
        raise ForgeAIError("authentication_required", "Please log in to use ForgeAI.", 401)
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            raise ForgeAIError("authentication_required", "Please log in to use ForgeAI.", 401)
        return user
