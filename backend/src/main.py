from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.auth.router import router as auth_router
from src.comments.router import router as comments_router
from src.core.config import get_settings
from src.core.database import load_dummy_data
from src.posts.router import router as posts_router
from src.subreddits.router import router as subreddits_router
from src.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dummy_data()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Limit", "X-Offset", "X-Next-Offset", "X-Has-More"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(comments_router)
    app.include_router(subreddits_router)

    return app


app = create_app()
