from pydantic import BaseModel, validator, root_validator
from app.core.config import settings, logger


class UploadExtension(BaseModel):
    filename: str
    extension: str = None

    @validator("extension")
    def filename_to_extension_validator(cls, v) -> str:
        if v in settings.ALLOWED_UPLOAD_MIMETYPES:
            return v
        raise ValueError("Invalid MIME type received on file upload. Keys must be 32 characters in length, strictly alphanumeric, and lowercase.")


class UploadRequest(BaseModel):
    pass


class UploadResponse(BaseModel):
    status: str
    filename: str = None
    batch_token: str = None

    @root_validator(skip_on_failure=True)
    def verify_valid_output(cls, values):
        if values['status'] == "success" and len(values['batch_token']) == 32:
            return values
        elif values['status'] == "failure" and values['batch_token'] is None:
            return values
        logger.error(f"[Validator.UploadResponse] - The upload response did not match the format specified. {values=}")
        raise ValueError("A success response should have a batch token with 32 characters, and a failure response should not have a token attached.")
