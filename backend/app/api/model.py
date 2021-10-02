# Routing and Database
import mimetypes

from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, File, UploadFile
from sqlalchemy.orm import Session
import aiofiles

# Model and Schema
# import app.db.schemas as schema
# import app.db.models as model
import app.db.structures as structure

# CRUD
from app.db.crud import db_authentication

# Dependencies
from pydantic import BaseModel, validator,  root_validator
from app.utils.dependencies import get_db, validate_api_key, generate_upload_uuid

# Load settings
from app.core.config import logger, settings


# -------------------
#  ROUTER DEFINITION
# -------------------
router = APIRouter(
    prefix="/api/model",
    tags=["model"],
    responses={404: {"status": "undocumented endpoint", "detail": "route was not found"}},
)


# -------------------
#   INITIALIZATION
# -------------------
@router.post('/upload')
async def upload(request: Request, db: Session = Depends(get_db), image: UploadFile = File(...)):
    # Gather content type from submission (shallow validation). Perform more rigorous validation with PIL in a model.
    if image.content_type != "image/jpeg" and image.content_type != "image/png":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File type does not match MIME type of image/jpeg or image/png. Please submit an image.",
        )

    # TODO: Don't write extension, allow PIL to guess and validate to prevent issues on mismatch
    image_uuid = generate_upload_uuid()
    async with aiofiles.open(str(settings.UPLOAD_PATH / f"{image_uuid}.batch"), "wb") as f:
        await f.write(await image.read())

    logger.debug(f"File: {image.filename} was uploaded to the server by {request.client.host}")
    return {
        "status": "upload successful",
        "filename": image.filename,
        "batch_token": image_uuid
    }
