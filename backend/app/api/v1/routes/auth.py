from fastapi import APIRouter, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.auth import SessionLocal, User, clear_session_cookie, current_user, hash_password, normalize_email, set_session_cookie, user_response, verify_password
from app.core.errors import ForgeAIError
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(request: RegisterRequest, http_request: Request, response: Response) -> AuthResponse:
    if request.password != request.confirm_password:
        raise ForgeAIError("password_mismatch", "Passwords do not match.")
    email = normalize_email(request.email)
    with SessionLocal() as session:
        if session.scalar(select(User).where(User.email == email)) is not None:
            raise ForgeAIError("account_exists", "An account with this email already exists.", 409)
        user = User(full_name=request.full_name.strip(), email=email, password_hash=hash_password(request.password))
        session.add(user)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ForgeAIError("account_exists", "An account with this email already exists.", 409) from error
        session.refresh(user)
        set_session_cookie(response, http_request, user.id)
        return AuthResponse(user=UserResponse(**user_response(user)))


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, http_request: Request, response: Response) -> AuthResponse:
    email = normalize_email(request.email)
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(request.password, user.password_hash):
            raise ForgeAIError("invalid_credentials", "Invalid email or password.", 401)
        set_session_cookie(response, http_request, user.id)
        return AuthResponse(user=UserResponse(**user_response(user)))


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    clear_session_cookie(response)


@router.get("/me", response_model=AuthResponse)
def me(request: Request) -> AuthResponse:
    return AuthResponse(user=UserResponse(**user_response(current_user(request))))
