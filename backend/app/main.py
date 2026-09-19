from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.core.auth import init_auth_db
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

configure_logging(settings.log_level)
init_auth_db()

app = FastAPI(title="ForgeAI API", version="0.1.0")
register_exception_handlers(app)
app.include_router(auth_router, prefix="/api")
app.include_router(api_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.add_middleware(
	CORSMiddleware,
	allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
	allow_credentials=True,
	allow_methods=["GET", "POST", "OPTIONS"],
	allow_headers=["*"],
)
