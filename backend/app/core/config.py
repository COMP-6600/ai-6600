import logging
import os
import secrets
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Debug
    DEBUG: bool = os.environ.get("DEBUG") or True

    # Server
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)  # for JWT signing
    ACCESS_TOKEN_EXPIRATION: int = os.environ.get("ACCESS_TOKEN_EXPIRATION") or 60  # for auth on subsequent requests without spinup

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
