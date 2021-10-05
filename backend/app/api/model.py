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
from app.core.config import logger, settings


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
async def upload(request: Request, content_length: int = Header(None), db: Session = Depends(get_db), image: UploadFile = File(...)):
    # Validate content length and reject missing content length header, handles file upload over constraints
    if content_length is None or content_length > settings.MAX_CONTENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is missing a Content-Length header.",
        )

    # Consume image data into memory
    image_temp = await image.read()

    # Add extra sanity check to avoid adding a large file to database, mitigates a more malicious header modification attack
    if len(image_temp) > settings.MAX_CONTENT_LENGTH or len(image_temp) > content_length:
        logger.critical(f"A file was uploaded that did not match Content-Length restrictions. Client info: {request.client}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file submitted exceeds the size set as the Content-Length, this request has been logged.",
        )

    # Gather content type from submission (shallow validation). Perform more rigorous validation with PIL in a model.
    if image.content_type != "image/jpeg" and image.content_type != "image/png":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File type does not match MIME type of image/jpeg or image/png. Please submit an image.",
        )

    # Don't write extension, allow PIL to guess and validate to prevent issues on mismatch
    image_uuid = generate_upload_uuid()
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
