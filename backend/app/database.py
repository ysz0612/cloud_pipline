from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config import settings


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)


engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI API에서 사용할 DB 세션을 생성합니다.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_tables() -> None:
    """
    등록된 SQLAlchemy 모델을 기준으로
    존재하지 않는 테이블을 생성합니다.
    """
    from app.users.model import User  # noqa: F401

    Base.metadata.create_all(
        bind=engine,
    )