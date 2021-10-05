# Dependencies
from typing import Generator, Any
from uuid import uuid4
from pathlib import Path

import PIL
from PIL import Image
from io import BytesIO

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
from app.db.crud import db_batch

# Model and schemas
# import app.db.schemas as schema
# import app.db.models as model
import app.db.structures as structure

# Validation, Error Handling, and Loggging
from pydantic import ValidationError
from app.core.config import logger


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
    """ Generates a one-time uuid4 number for batch tickets or key generation. """
    return uuid4().hex


def validate_api_key(key: str) -> bool:
    """ Uses API key to validate user. """
    return key == settings.API_KEY


def validate_image(input_data: bytes) -> bool:
    """ Runs image through PIL to verify that it can be opened, as an added benefit, PIL verifies it is not a decompression bomb. """
    try:
        Image.open(BytesIO(input_data))
    except PIL.UnidentifiedImageError:
        return False
    return True


async def queue_watermark_removal(batch_token: str, image_data: bytes, db: Session = Depends(get_db)):
    """ Initiate process of removing watermark from image. """
    # Set status to processing
    db_batch.update_status(
        db=db,
        batch_token=batch_token,
        process_status="processing"
    )

    # Remove watermark from image
    processed_image_data: bytes = b''
    try:
        # TODO: Pass image data through trained model to remove watermark and store the output
        processed_image_data = b'NOT_IMPLEMENTED'
    except Exception as e:
        # Set status to error
        db_batch.update_status(
            db=db,
            batch_token=batch_token,
            process_status="error"
        )
        logger.exception(f"An exception occurred while removing watermark from image with {batch_token=}.", exc_info=e)
        return

    # Write processed image data to database
    db_batch.store_processed_image(
        db=db,
        batch_token=batch_token,
        processed_image_data=processed_image_data
    )

    # Set status to completed
    db_batch.update_status(
        db=db,
        batch_token=batch_token,
        process_status="completed"
    )


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
