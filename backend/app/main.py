from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.web import router as auth_router
from app.database import create_tables
from app.imageRag.web import (
    router as image_rag_router,
)
from app.redis_client import (
    check_redis_connection,
    close_redis_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 시작 시 RDS 테이블과 Redis 연결을 확인하고,
    종료 시 Redis 연결을 정리합니다.
    """

    # users 테이블이 없으면 생성합니다.
    create_tables()

    # Redis 연결 확인
    redis_connected = (
        await check_redis_connection()
    )

    if not redis_connected:
        raise RuntimeError(
            "Redis 연결에 실패했습니다."
        )

    yield

    await close_redis_connection()


app = FastAPI(
    title="Image RAG API",
    description=(
        "음식 이미지 분석 및 로그인 API"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://3.37.38.214",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router
)

app.include_router(
    image_rag_router
)


@app.get("/")
def root():
    return {
        "message": "Image RAG API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }