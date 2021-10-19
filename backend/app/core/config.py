import logging
import os
from os import environ as env
import secrets
from typing import Any, Dict, Optional
from pathlib import Path
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Debug
    DEBUG: bool = env.get("DEBUG") or True

    # Server
    API_KEY: str = secrets.token_urlsafe(32)  # for access control
    SECRET_KEY: str = secrets.token_urlsafe(32)  # for JWT signing
    ALGORITHM = 'HS256'  # for JTW security
    ACCESS_TOKEN_EXPIRATION: int = 60  # for auth on subsequent requests without spinup
    MAX_CONTENT_LENGTH: int
    OPENAPI_URL = '/openapi.json'
    SITE_HOST: str

    # Environment
    ROOT_PATH: Path = Path().cwd().parent
    if env.get("HOME") is not None:
        ROOT_PATH = Path(env.get("HOME"))
    BACKEND_PATH: Path = ROOT_PATH / "backend"
    FRONTEND_PATH: Path = ROOT_PATH / "frontend"
    STATIC_PATH: Path = FRONTEND_PATH / "static"
    UPLOAD_PATH: Path = ROOT_PATH / "upload"

    # Configuration
    ALLOWED_UPLOAD_MIMETYPES: list = ["image/jpg", "image/jpeg", "image/png"]

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
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
            query=values.get('POSTGRES_SSL')
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

# TODO: Debug Heroku deployment
if os.environ.get("DYNO"):
    logger.debug("Config fields loaded:")
    logger.debug(settings.dict())
