# Routing and Database
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Header,
    Request,
    File,
    UploadFile,
    BackgroundTasks,
    Query
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# CRUD
from app.db.crud import db_batch

# Dependencies
from app.utils.dependencies import (
    get_db,
    generate_upload_uuid,
    validate_image,
    queue_watermark_removal
)

# Load settings
from app.core.config import logger, settings

# Models
import app.db.structures as structure

# Libraries
from io import BytesIO
from typing import Optional


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
@router.post('/upload', response_model=structure.UploadResponse)
async def upload(
        request: Request,
        background_tasks: BackgroundTasks,
        content_length: int = Header(None),
        db: Session = Depends(get_db),
        image: UploadFile = File(..., description="Binary data of an uploaded image that we should process.")
):
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

    # Queue a background task to process image through completed model
    background_tasks.add_task(queue_watermark_removal, db, image_uuid, image_temp)

    # Notify user of successful upload and pass a batch token for follow-up
    logger.debug(f"File: {image.filename} was uploaded to the server by {request.client.host}")
    return {
        "status": "success",
        "filename": image.filename,
        "batch_token": image_uuid
    }


@router.get("/batch", response_model=structure.BatchStatus)
def get_batch_status(
        token: str = Query(..., min_length=32, max_length=32, description="The batch token for the image to retrieve."),
        db: Session = Depends(get_db)
):
    """ Endpoint to poll periodically to check the status of the batch job to avoid a more complex approach (WS). """
    try:
        return {
            "status": db_batch.get_ticket(db, batch_token=token).process_status,
            "detail": None
        }
    except (ValueError, AttributeError):
        logger.error(f"Image with batch_token={token} was not found in the database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The batch token submitted does not correspond to a batch ticket. Please try again.",
        )


@router.get("/download", response_class=StreamingResponse)
def download_processed_image(
        token: str = Query(..., min_length=32, max_length=66, description="The batch token for the image to retrieve."),
        original: Optional[str] = Query(None, description="Set to 'true' if we should retrieve the original image instead of the processed one."),
        db: Session = Depends(get_db)
) -> StreamingResponse:
    """ Endpoint to be hit when image is ready to download.
        Alternatively, set optional=1 to retrieve the original image instead.
     """
    ticket = db_batch.get_ticket(db, batch_token=token)
    if ticket is None or ticket.process_status != "completed":
        logger.error(f"Image with batch_token={token} is not yet ready to download or does not exist.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The batch token submitted does not correspond to a batch ticket or is not available for download. Please check request and retry.",
        )

    # Request is valid if token is in table, return chunked data stream
    if original:
        return StreamingResponse(BytesIO(ticket.image_original), media_type="image/png")
    return StreamingResponse(BytesIO(ticket.image_processed), media_type="image/png")
