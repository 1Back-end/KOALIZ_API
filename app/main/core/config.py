import os

from pydantic import EmailStr
from pydantic_settings import BaseSettings
from typing import Optional


def get_secret(secret_name, default):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return os.getenv(secret_name, default)


class ConfigClass(BaseSettings):
    SECRET_KEY: str = get_secret("SECRET_KEY", '7FJxtvSbz8ba7YKCKCUt53M4M6PxTgxBKwQSejucZScXm8')
    ALGORITHM: str = get_secret("ALGORITHM", 'HS256')

    ADMIN_KEY: str = get_secret("ADMIN_KEY", "BdeMicroCreche24")
    ADMIN_USERNAME: str = get_secret("ADMIN_USERNAME", "bdemicrocreche")
    ADMIN_PASSWORD: str = get_secret("ADMIN_PASSWORD", "JXunRJ1r3g")

    PROJECT_NAME: str = get_secret("PROJECT_NAME", "BDE MICRO CRECHE API")
    PROJECT_VERSION: str = get_secret("PROJECT_VERSION", "0.0.1")
    PREFERRED_LANGUAGE: str = get_secret("PREFERRED_LANGUAGE", 'fr')
    API_STR: str = get_secret("API_STR", "/api/v1")

    # 60 minutes * 24 hours * 355 days = 365 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_secret("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 365))

   # Minio
    MINIO_API_URL: str = get_secret("MINIO_API_URL", "http://localhost:5300/api/v1/storages/get/")
    MINIO_URL: str = get_secret("MINIO_URL", "play.min.io")
    MINIO_ACCESS_KEY: str = get_secret("MINIO_ACCESS_KEY", "Q3AM3UQ867SPQQA43P2F")
    MINIO_SECRET_KEY: str = get_secret("MINIO_SECRET_KEY", "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG")
    MINIO_BUCKET: str = get_secret("MINIO_BUCKET", "develop")
    MINIO_SECURE: bool = get_secret("MINIO_SECURE", True)

    # Sqlalchemy
    SQLALCHEMY_DATABASE_URL: str = get_secret("SQLALCHEMY_DATABASE_URL", 'postgresql://postgres:root@localhost:5432/bde_micro_creche_dev')
    SQLALCHEMY_POOL_SIZE: int = 100
    SQLALCHEMY_MAX_OVERFLOW: int = 0
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = get_secret("SQLALCHEMY_POOL_RECYCLE", 3600)
    SQLALCHEMY_POOL_PRE_PING: bool = get_secret("SQLALCHEMY_POOL_PRE_PING", True)
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": SQLALCHEMY_POOL_RECYCLE,
    }
    
    # Redis
    REDIS_HOST: str = get_secret("REDIS_HOST", "localhost")  # redis_develop
    REDIS_PORT: int = get_secret("REDIS_PORT", 6379)
    REDIS_DB: int = get_secret("REDIS_DB", 2)
    REDIS_CHARSET: str = get_secret("REDIS_CHARSET", "UTF-8")
    REDIS_DECODE_RESPONSES: bool = get_secret("REDIS_DECODE_RESPONSES", True)

    LOCAL: bool = os.getenv("LOCAL", True)

    SMTP_TLS: bool = get_secret("SMTP_TLS", False)
    SMTP_SSL: bool = get_secret("SMTP_SSL", False)
    SMTP_PORT: Optional[int] = int(get_secret("SMTP_PORT", 1025))
    SMTP_HOST: Optional[str] = get_secret("SMTP_HOST", "localhost")
    SMTP_USER: Optional[str] = get_secret("SMTP_USER", "")
    SMTP_PASSWORD: Optional[str] = get_secret("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = get_secret("EMAILS_FROM_EMAIL", "liditieng@gmail.com")
    EMAILS_FROM_NAME: Optional[str] = get_secret("EMAILS_FROM_NAME", "BDE-CRECHE")

    EMAIL_TEMPLATES_DIR: str = "{}/app/main/templates/emails/render".format(os.getcwd())
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = int(get_secret("EMAIL_RESET_TOKEN_EXPIRE_HOURS", 48))
    EMAILS_ENABLED: bool = get_secret("EMAILS_ENABLED", True) in ["True", True]

    CELERY_BROKER_URL: str = get_secret("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = get_secret("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Default image size
    # IMAGE_MEDIUM_WIDTH: int = get_secret("IMAGE_MEDIUM_WIDTH", 600)
    # IMAGE_THUMBNAIL_WIDTH: int = get_secret("IMAGE_THUMBNAIL_WIDTH", 300)

    UPLOADED_FILE_DEST: str = get_secret("UPLOADED_FILE_DEST", "uploads")

    class Config:
        case_sensitive = True


Config = ConfigClass()