from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_vision_model: str = "gpt-4o-mini"
    openai_embedding_model: str = (
        "text-embedding-3-small"
    )

    # AWS S3
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: str = "ysz0612-s3-pipeline"
    s3_image_prefix: str = "images/"
    s3_presigned_url_expires: int = 900

    # RDS PostgreSQL
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_host: str = "image-rag-redis"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()