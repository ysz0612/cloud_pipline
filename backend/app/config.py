from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


# 로컬:
# project/backend/app/config.py
# parents[2] = project
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
    db_host: str = ""
    db_port: int = 5432
    db_name: str = "image_rag_db"
    db_user: str = "postgres"
    db_password: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.db_name}"
        )


settings = Settings()