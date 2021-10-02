import logging
import os
import secrets
from typing import Any, Dict, Optional
from pathlib import Path
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Debug
    DEBUG: bool = os.environ.get("DEBUG") or True

    # Server
    API_KEY: str = os.environ.get("API_KEY")  # for access control
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)  # for JWT signing
    ALGORITHM = 'HS256'  # for JTW security
    ACCESS_TOKEN_EXPIRATION: int = os.environ.get("ACCESS_TOKEN_EXPIRATION") or 60  # for auth on subsequent requests without spinup

    # Environment
    ROOT_PATH: Path = Path().cwd().parent
    BACKEND_PATH: Path = ROOT_PATH / "backend"
    FRONTEND_PATH: Path = ROOT_PATH / "frontend"
    STATIC_PATH: Path = FRONTEND_PATH / "static"
    UPLOAD_PATH: Path = ROOT_PATH / "upload"

    # Configuration
    ALLOWED_UPLOAD_MIMETYPES: list = ["image/jpg", "image/jpeg", "image/png"]

    # Database
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Configure logger
logger: logging.Logger = logging.getLogger('backend')
logger.setLevel('DEBUG')
logger.addHandler(logging.StreamHandler())

# Export settings
settings = Settings()
