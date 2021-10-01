from pydantic import BaseModel, validator


class InstanceRequestModel(BaseModel):
    """ Route client -> POST /api/auth/instance. """
    x_api_key: str

    @validator("x_api_key")
    def api_key_format_validator(cls, v) -> str:
        if len(v) == 32 and str(v).isalnum() and str(v).islower():
            return v
        raise ValueError("Invalid X-API-KEY received. Keys must be 32 characters in length, strictly alphanumeric, and lowercase.")


class InstanceResponseModel(BaseModel):
    """ Route client <- POST /api/auth/instance. """
    token: str
