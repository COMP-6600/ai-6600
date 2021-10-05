# Routing and Database
from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, File, UploadFile
from sqlalchemy.orm import Session

# File handling and identification
from PIL import Image

# CRUD
from app.db.crud import db_batch

# Dependencies
from app.utils.dependencies import get_db, generate_upload_uuid, validate_image

# Load settings
from app.core.config import logger


# -------------------
#  ROUTER DEFINITION
# -------------------
router = APIRouter(
    prefix="/api/model",
    tags=["model"],
    responses={404: {"status": "undocumented endpoint", "detail": "route was not found"}},
)


# ---------------------
#   IMAGE PROCESSING
# ---------------------
@router.post('/upload')
async def upload(request: Request, db: Session = Depends(get_db), image: UploadFile = File(...)):
    # Gather content type from submission (shallow validation). Perform more rigorous validation with PIL in a model.
    if image.content_type != "image/jpeg" and image.content_type != "image/png":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File type does not match MIME type of image/jpeg or image/png. Please submit an image.",
        )

    # Don't write extension, allow PIL to guess and validate to prevent issues on mismatch
    image_uuid = generate_upload_uuid()
    image_temp = await image.read()
    if not validate_image(image_temp):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File submitted is corrupted and cannot be read as an image. Please try again.",
        )

    # Create a batch ticket to queue image for processing
    db_batch.create_ticket(
        db=db,
        batch_token=image_uuid,
        original_image_data=image_temp
    )

    # Notify user of successful upload and pass a batch token for follow-up
    logger.debug(f"File: {image.filename} was uploaded to the server by {request.client.host}")
    return {
        "status": "upload successful",
        "filename": image.filename,
        "batch_token": image_uuid
    }


@router.get("/batch")
def get_batch_status(token: str, db: Session = Depends(get_db)):
    """ Endpoint to poll periodically to check the status of the batch job to avoid a more complex approach (WS). """
    batch_status = db_batch.get_status(db, batch_token=token)
    if batch_status == "READY":
        return {
            "status": "ready",
            "detail": "the image is ready to download."
        }
    elif batch_status == "PROCESSING":
        return {
            "status": "processing",
            "detail": "the image is currently being processed."
        }
    elif batch_status == "QUEUED":
        return {
            "status": "queued",
            "detail": "the image is in line for processing."
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The batch token submitted does not correspond to a batch ticket. Please try again.",
        )
