from pydantic import BaseModel


class BatchBase(BaseModel):
    pass


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BatchBase):
    pass
