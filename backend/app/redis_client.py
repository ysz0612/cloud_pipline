from redis.asyncio import Redis

from app.config import settings


redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=(
        settings.redis_password
        if settings.redis_password
        else None
    ),
    db=settings.redis_db,
    decode_responses=True,
)


async def check_redis_connection() -> bool:
    """
    Redis 연결 상태를 확인합니다.
    """
    return await redis_client.ping()


async def close_redis_connection() -> None:
    """
    FastAPI 종료 시 Redis 연결을 정리합니다.
    """
    await redis_client.aclose()