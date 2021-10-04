# Time management
import arrow

# Dependencies
from typing import Optional

# Database
from sqlalchemy.orm import Session
from app.db.crud.base import CRUDBase
from app.db.schemas import BatchCreate, BatchUpdate
from app.db.models import Batch


class CRUDBatch(CRUDBase[Batch, BatchCreate, BatchUpdate]):
    def create_ticket(self, db: Session, batch_token: str, original_image_data: bytes) -> Batch:
        ticket = Batch(
            batch=batch_token,
            created=arrow.utcnow().datetime,
            image_original=original_image_data
        )
        return self.create(db, data=ticket)

    def get_ticket(self, db: Session, batch_token: str) -> Optional[Batch]:
        """ Obtain a batch ticket if it is available in the database """
        return self.read(db, {"batch": batch_token}, first=True)

    def store_processed_image(self, db: Session, ticket: Batch, processed_image_data: bytes):
        """ Allows setting and updating of the instance token. """
        self.update(
            db=db,
            model_object=ticket,
            data={'image_processed': processed_image_data}
        )

    def get_status(self, db: Session, batch_token) -> str:
        """ Checks the status of a batch ticket. Returns READY if it is ready to retrieve, and PROCESSING if it is being worked on, or QUEUED if it is in line. """
        ticket = self.get_ticket(db, batch_token=batch_token)

        # TODO: This is not efficient and will result in delays, add an additional column with completion status and poll that instead
        completed = ticket.image_processed
        if completed is not None:
            return "READY"
        return "QUEUED"


# Instantiate and export
db_batch = CRUDBatch(Batch)
