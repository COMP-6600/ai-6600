from pydantic import BaseModel, validator
from app.core.config import settings


class UploadExtension(BaseModel):
    filename: str
    extension: str = None

    @validator("extension")
    def filename_to_extension_validator(cls, v) -> str:
        if v in settings.ALLOWED_UPLOAD_MIMETYPES:
            return v
        raise ValueError("Invalid MIME type received on file upload. Keys must be 32 characters in length, strictly alphanumeric, and lowercase.")

