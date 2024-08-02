import math
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.models.db.base_class import Base
from app.main import schemas, models

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, uuid: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get_multi(
            self, db: Session, *, page: int = 0, per_page: int = 20
    ) -> schemas.DataList:

        total = db.query(self.model).count()
        result = db.query(self.model).offset((page - 1) * per_page).limit(per_page).all()
        return schemas.DataList(
            total=total,    
            pages=math.ceil(total / per_page),
            current_page=page,
            per_page=per_page,
            data=result
        )

    @staticmethod
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                print(field)
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, uuid: int) -> ModelType:
        obj = db.query(self.model).get(uuid)
        db.delete(obj)
        db.commit()
        return obj


    def get_elements_by_tag(self, db: Session, tag: str) -> list:

        query = db.query(models.TagElement).join(models.Tags, models.Tags.uuid==models.TagElement.tag_uuid)
        query = query.filter(or_(
            # models.Tags.title_en.ilike("%"+tag_type+"%"),
            # models.Tags.title_fr.ilike("%"+tag_type+"%")
            models.Tags.title_en==tag,
            models.Tags.title_fr==tag
        ))

        tag_elements = query.all()

        elements = []
        for tag_element in tag_elements:
            element = tag_element.element
            if element is None:
                continue  # Skip elements with no associated element

            # Dynamic element type handling (replace with your actual model mapping)
            element_type_mapping = {
                "PRE_ENROLLMENT": "PreRegistration",
                "CHILDREN": "Membership",
                "PARENTS": "ParentGuest",
                "PICTURE": "Storage",
            }
            model_name = element_type_mapping.get(tag_element.element_type)
            # if not model_name:
            #     raise ValueError(f"Unsupported element type: {tag_element.element_type}")

            # Assuming your models have a `__repr__` method for human-readable output
            element_data = element
            elements.append({"model": model_name, "data": element_data})

        return elements


