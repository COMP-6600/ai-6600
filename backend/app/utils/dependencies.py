# Dependencies
from typing import Generator, Any
from uuid import uuid4
from pathlib import Path

# FastAPI and routes
from fastapi import Depends, HTTPException, status

# JWT and Security
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from jose import jwt  # noqa
from jose.exceptions import JOSEError  # noqa

# Database and CRUD
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

# Model and schemas
# import app.db.schemas as schema
# import app.db.models as model
import app.db.structures as structure

# Validation and Error Handling
# import app.utils.exceptions
from pydantic import ValidationError


# GLOBALS
oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"/api/auth/instance")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()  # noqa


def unpack_token(token: str) -> structure.TokenPayload:
    """ Parses received token and returns the payload. A JWT exception is passed down the chain on failure. """
    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return structure.TokenPayload(**payload)
    except (JOSEError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate session, please refresh token: {e}"
        )


def generate_upload_uuid() -> str:
    return uuid4().hex


def validate_api_key(key: str) -> bool:
    """ Uses API key to validate user. """
    return key == settings.API_KEY


def invalidate_token(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> bool:  # noqa
    """ Expire token to force API validation again. """
    pass


def get_session_from_token(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> Any:  # noqa
    """ Obtain the user referenced in the session token if one exists. """
    # Unpack and parse token


def get_session_from_api_key(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> Any:  # noqa
    """ Obtain the user referenced in the session token if one exists. """
    # Unpack and parse token
    pass
