# Date management, formatting, and typing support
import arrow
from typing import Generator, Union, Any

# FastAPI and routes
from fastapi import Depends, HTTPException, status

# JWT and Security
from app.core import security
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JOSEError

# Database and CRUD
from ..db.session import SessionLocal
from sqlalchemy.orm import Session

# Model and schemas
from app.db import schemas as schema
from app.db import models as model

# Validation and Error Handling
# import ..common.exceptions
from pydantic import BaseModel, ValidationError


# GLOBALS
oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"/api/instance")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()  # noqa


def unpack_token(token: str) -> schema.TokenPayload:
    """ Parses received token and returns the payload. A JWT exception is passed down the chain on failure.

    :param token: the token received from the client
    :return: the token payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM]
        )
        return schema.TokenPayload(**payload)
    except (JOSEError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate session, please refresh token: {e}"
        )


def invalidate_token(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> bool:
    """ Expire token to force API validation again """
    pass


def get_session_from_token(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> Any:
    """ Obtain the user referenced in the session token if one exist """
    # Unpack and parse token


def get_session_from_api_key(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> Any:
    """ Obtain the user referenced in the session token if one exist """
    # Unpack and parse token
    pass
