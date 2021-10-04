# Typing and validation
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union
from pydantic import BaseModel

# Database and formatting
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
from app.db.base import Base

# Define standard models and modificationn schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """ Generic base operations for all CRUD tasks.
     Implement true CRUD methodology by providing base methods for each operation. """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, data: Union[ModelType, CreateSchemaType]) -> ModelType:
        """ Create a new object of this model given a validated schema. """
        # Convert data to JSON and feed through model
        db_obj = data
        if type(data) == DeclarativeMeta:
            db_obj = self.model(**(jsonable_encoder(data)))

        # Add to database and return
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def read(self, db: Session, item: dict, first=False) -> Union[list[ModelType], ModelType, None]:
        """ Return object by arbitrary primary-key value if it exists """
        values = (
            db
            .query(self.model)
            .filter_by(**item)
            .all()
        )
        if first:
            return values[0]
        return values

    def update(self, db: Session, model_object: ModelType, data: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """ Update a database model object with another object or a dictionary with key-value pairs. """
        # Break up input into json and mirror data into a temporary model mapping
        obj_data = jsonable_encoder(model_object)
        mirror_obj = self.model(**obj_data)

        # Parse either a pydantic schema or a dictionary with key-value pairs
        if isinstance(data, dict):
            update_data: dict = data
        else:
            update_data: dict = data.dict(exclude_unset=True)

        # Create the intersection of both dictionaries and keep only update data
        intersection = obj_data.keys() & update_data.keys()
        for field in intersection:
            setattr(model_object, field, update_data[field])

        # Update database unless no changes were made
        if mirror_obj == model_object:
            return model_object
        db.add(model_object)
        db.commit()
        db.refresh(model_object)
        return model_object

    def delete(self, db: Session, item: Union[ModelType, Dict[str, Any]]) -> Optional[list[ModelType]]:
        """ Delete rows from the database by locating the values given as keys and removing. """
        # If passed a model, delete it
        if not isinstance(item, dict):
            db.delete(item)
            db.commit()
            return

        # Find object by value of the primary key
        obj = db.query(self.model).filter_by(**item).all()

        # Delete object and return
        if not obj:
            return
        for del_obj in obj:
            db.delete(del_obj)
        db.commit()
        return obj
