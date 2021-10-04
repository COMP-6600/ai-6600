from sqlalchemy import Column, String, DateTime, LargeBinary, Integer

from app.db.base import Base


class Batch(Base):
    __tablename__ = "batch"

    id = Column(Integer, primary_key=True)
    batch = Column(String, nullable=False, unique=True)
    created = Column(DateTime, nullable=False)
    image_original = Column(LargeBinary, nullable=False)
    image_processed = Column(LargeBinary)
