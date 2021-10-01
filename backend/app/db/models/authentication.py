from sqlalchemy import Column, String, DateTime

from app.db.base import Base


class Authentication(Base):
    __tablename__ = "authentication"

    instance = Column(String, primary_key=True)
    nonce = Column(String, nullable=False, unique=True)
    created = Column(DateTime, nullable=False)
    expires = Column(DateTime, nullable=False)
