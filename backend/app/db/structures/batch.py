from pydantic import BaseModel, root_validator
from app.core.config import logger


class BatchStatus(BaseModel):
    status: str
    detail: str = None

    @root_validator(skip_on_failure=True)
    def set_detail_on_status(cls, values):
        status_dict = {
            "completed": "the image is ready to download.",
            "processing": "the image is currently being processed.",
            "queued": "the image is in line for processing.",
            "error": "there was an issue processing the image provided."
        }
        if values['status'] in status_dict:
            values['detail'] = status_dict[values['status']]
            return values
        logger.error(f"[Validator.BatchStatus] - A valid status was not provided. {values['status']=}")
        raise ValueError("The status provided is not allowed, verify the proper status was used.")
