from typing import Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main import models, schemas

import uuid


class CRUDAddress(CRUDBase[models.Address, schemas.AddressCreate, schemas.AddressUpdate]):


    def create(self, db: Session, *, obj_in: schemas.AddressCreate) -> models.Address:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            obj_in_data["uuid"] = str(uuid.uuid4())
            db_obj = self.model(**obj_in_data)
            # db_obj = models.Address(
            #     uuid=str(uuid.uuid4()),
            #     **{obj_in.model_dump()}
            # )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        
        except Exception as e:
            print(str(e))
            db.rollback()


    def get_address_by_uuid(self, db: Session, uuid: str) -> models.Address:
        return db.query(models.Address).filter(models.Address.uuid == uuid).first()


    def update(
        self, db: Session, *, db_obj: models.Address, obj_in: schemas.AddressUpdate
    ) -> models.Address:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            return super().update(db, db_obj=db_obj, obj_in=update_data)
        except Exception as e:
            print(str(e))
            db.rollback()

        
address = CRUDAddress(models.Address)