# Time management
import arrow

# Dependencies
from uuid import uuid4
from typing import Optional

# Database
from sqlalchemy.orm import Session
from app.db.crud.base import CRUDBase
from app.db.schemas import AuthenticationCreate, AuthenticationUpdate
from app.db.models import Authentication


class CRUDAuthentication(CRUDBase[Authentication, AuthenticationCreate, AuthenticationUpdate]):
    def create_session(self, db: Session, token: str) -> Authentication:
        session = Authentication(
            instance=token,
            nonce=uuid4().hex,
            created=arrow.utcnow().datetime,
            expires=arrow.utcnow().shift(minutes=60).datetime
        )
        return self.create(db, data=session)

    def get_session(self, db: Session, token: str) -> Optional[Authentication]:
        """ Helper method to return a match if a user with the requested username is found """
        return self.read(db, {self.model.instance: token}, first=True)

    def set_instance_token(self, db: Session, user: Authentication, instance_token: str):
        """ Allows setting and updating of the instance token. """
        self.update(
            db=db,
            model_object=user,
            data={'instance': instance_token}
        )

    def clear_expired_instances(self, db: Session):
        """ Uses current call to search for aging kronos instances and destroys them """
        sessions: list[Authentication] = db.query(self.model).all()
        for session in sessions:
            if arrow.now() >= session.expires:
                self.delete(db, session)

    # TODO: Need migration or an access table for storing session information
    # def store_session_data(self, db: Session, user: Authentication, payload: dict):
    #     if user.session:
    #         self.clear_session_data(db, user=user)
    #     self.update(
    #         db=db,
    #         db_obj=user,
    #         obj_in={'session': payload}
    #     )
    #
    # def clear_session_data(self, db: Session, user: Authentication):
    #     self.update(
    #         db=db,
    #         db_obj=user,
    #         obj_in={'session': None}
    #     )


# Instantiate and export
db_authentication = CRUDAuthentication(Authentication)
