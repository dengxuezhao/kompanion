from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = Field("Kompanion", env="KOMPANION_APP_NAME")
    env: str = Field("development", env="KOMPANION_APP_ENV")
    url: str = Field("http://localhost:8080", env="KOMPANION_APP_URL")
    port: int = Field(8080, env="KOMPANION_APP_PORT")
    shutdown_timeout: int = Field(5, env="KOMPANION_APP_SHUTDOWN_TIMEOUT")


class AuthSettings(BaseSettings):
    jwt_secret: str = Field(..., env="KOMPANION_AUTH_JWT_SECRET")
    jwt_expires_in: int = Field(3600, env="KOMPANION_AUTH_JWT_EXPIRES_IN")
    jwt_refresh_secret: str = Field(..., env="KOMPANION_AUTH_JWT_REFRESH_SECRET")
    jwt_refresh_expires_in: int = Field(604800, env="KOMPANION_AUTH_JWT_REFRESH_EXPIRES_IN")
    koreader_sync_secret: Optional[str] = Field(None, env="KOMPANION_AUTH_KOREADER_SYNC_SECRET")


class HTTPSettings(BaseSettings):
    host: str = Field("0.0.0.0", env="KOMPANION_HTTP_HOST")
    port: int = Field(8080, env="KOMPANION_HTTP_PORT")
    trusted_proxies: Optional[list[str]] = Field(None, env="KOMPANION_HTTP_TRUSTED_PROXIES")


class LogSettings(BaseSettings):
    level: str = Field("info", env="KOMPANION_LOG_LEVEL")
    format: str = Field("text", env="KOMPANION_LOG_FORMAT")  # "text" or "json"


class PGSettings(BaseSettings):
    host: str = Field("localhost", env="KOMPANION_PG_HOST")
    port: int = Field(5432, env="KOMPANION_PG_PORT")
    user: str = Field("kompanion", env="KOMPANION_PG_USER")
    password: str = Field(..., env="KOMPANION_PG_PASSWORD")
    db_name: str = Field("kompanion", env="KOMPANION_PG_DBNAME")
    ssl_mode: str = Field("disable", env="KOMPANION_PG_SSLMODE")


class BookStorageSettings(BaseSettings):
    type: str = Field("local", env="KOMPANION_BOOK_STORAGE_TYPE")  # "local" or "s3"
    path: str = Field("./books", env="KOMPANION_BOOK_STORAGE_PATH")
    s3_endpoint: Optional[str] = Field(None, env="KOMPANION_BOOK_STORAGE_S3_ENDPOINT")
    s3_region: Optional[str] = Field(None, env="KOMPANION_BOOK_STORAGE_S3_REGION")
    s3_bucket: Optional[str] = Field(None, env="KOMPANION_BOOK_STORAGE_S3_BUCKET")
    s3_access_key_id: Optional[str] = Field(None, env="KOMPANION_BOOK_STORAGE_S3_ACCESS_KEY_ID")
    s3_secret_access_key: Optional[str] = Field(None, env="KOMPANION_BOOK_STORAGE_S3_SECRET_ACCESS_KEY")
    s3_use_ssl: bool = Field(True, env="KOMPANION_BOOK_STORAGE_S3_USE_SSL")


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    http: HTTPSettings = HTTPSettings()
    log: LogSettings = LogSettings()
    pg: PGSettings = PGSettings()
    book_storage: BookStorageSettings = BookStorageSettings()

    class Config:
        env_nested_delimiter = "__"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
