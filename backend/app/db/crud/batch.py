# Time management
import arrow

# Dependencies
from typing import Optional, Union

# Database
from sqlalchemy.orm import Session
from app.db.crud.base import CRUDBase
from app.db.schemas import BatchCreate, BatchUpdate
from app.db.models import Batch

# Logging
from app.core.config import logger


class CRUDBatch(CRUDBase[Batch, BatchCreate, BatchUpdate]):
    def create_ticket(self, db: Session, batch_token: str, original_image_data: bytes) -> Batch:
        ticket = Batch(
            batch=batch_token,
            created=arrow.utcnow().datetime,
            image_original=original_image_data,
            process_status="queued"
        )
        return self.create(db, data=ticket)

    def get_ticket(self, db: Session, batch_token: str) -> Union[Batch, None]:
        """ Obtain a batch ticket if it is available in the database """
        return self.read(db, {"batch": batch_token}, first=True)

    def store_processed_image(self, db: Session, batch_token: str, processed_image_data: bytes):
        """ Allows setting and updating of the instance token. """
        ticket = self.get_ticket(db, batch_token=batch_token)
        ticket.image_processed = processed_image_data
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

    def get_status(self, db: Session, batch_token: str) -> str:
        """ Checks the status of a batch ticket. Returns READY if it is ready to retrieve, and PROCESSING if it is being worked on, or QUEUED if it is in line. """
        ticket = self.get_ticket(db, batch_token=batch_token)
        return ticket.process_status

    def update_status(self, db: Session, batch_token: str, process_status: str) -> bool:
        """ Updates the status of an image processing batch session to make it available for endpoint polling. """
        ticket = self.get_ticket(db, batch_token=batch_token)

        valid_status = ['queued', 'processing', 'completed', 'error']
        if process_status not in valid_status:
            logger.error(f"Cannot update batch status with {process_status=}")
            return False

        # Update ticket status
        ticket.process_status = process_status
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return True


# Instantiate and export
db_batch = CRUDBatch(Batch)
