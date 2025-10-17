from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # Database
    database_url: str = "sqlite:///./travel_crm.db"
    postgres_user: str = "dummy"
    postgres_password: str = "dummy"
    postgres_db: str = "dummy"
    
    # JWT
    secret_key: str = "fallback-secret-key-for-development-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "files"
    minio_secure: bool = False
    
    # Admin
    admin_password: str = "admin123"
    admin_email: str = "admin@test.com"
    
    # Environment
    environment: str = "development"


settings = Settings()
