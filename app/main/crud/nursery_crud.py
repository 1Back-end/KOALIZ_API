from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password


class CRUDNursery(CRUDBase[models.Nursery, schemas.NurseryCreateSchema, schemas.NurseryUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Nursery]:
        return db.query(models.Nursery).filter(models.Nursery.uuid == uuid)\
            .filter(models.Nursery.status.notin_([models.UserStatusType.DELETED])).first()

    @classmethod
    def get_by_email(cls, db: Session, email: EmailStr) -> models.Nursery:
        return db.query(models.Nursery).filter(models.Nursery.email == email)\
            .filter(models.Nursery.status.notin_([models.UserStatusType.DELETED])).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.NurseryCreate) -> models.Administrator:
        # logo = crud.storage.get(db=db, uuid=obj_in.logo_uuid)
        # if not logo:
        #     raise HTTPException(status_code=404, detail=__("logo-not-found"))
        # signature = crud.storage.get(db=db, uuid=obj_in.signature_uuid)
        # if not signature:
        #     raise HTTPException(status_code=404, detail=__("signature-not-found"))
        # stamp = crud.storage.get(db=db, uuid=obj_in.signature_uuid)
        # if not stamp:
        #     raise HTTPException(status_code=404, detail=__("stamp-not-found"))

        # address = crud.address.create(db=db, obj_in=obj_in.address)

        nursery = models.Nursery(
            uuid=str(uuid.uuid4()),
            email=obj_in.email,
            name=obj_in.name,
            logo_uuid=obj_in.logo_uuid,
            signature_uuid=obj_in.signature_uuid,
            stamp_uuid=obj_in.stamp_uuid,
            total_places=obj_in.total_places,
            phone_number=obj_in.phone_number
        )
        db.add(nursery)
        db.commit()
        db.refresh(nursery)
        return nursery
    
    @classmethod
    def update(cls, db: Session, obj_in: schemas.AdministratorUpdate) -> models.Administrator:
        administrator = cls.get_by_uuid(db, obj_in.uuid)
        administrator.firstname = obj_in.firstname if obj_in.firstname else administrator.firstname
        administrator.lastname = obj_in.lastname if obj_in.lastname else administrator.lastname
        administrator.email = obj_in.email if obj_in.email else administrator.email
        administrator.role_uuid = obj_in.role_uuid if obj_in.role_uuid else administrator.role_uuid
        administrator.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else administrator.avatar_uuid

        db.commit()
        db.refresh(administrator)
        return administrator
    
    @classmethod
    def delete(cls, db: Session, uuid) -> None:
        user = cls.get_by_uuid(db, uuid)
        if user:
            user.status = models.UserStatusType.DELETED
            db.commit()

    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Administrator).options(joinedload(models.Administrator.role))

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Administrator, order_filed))

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Administrator.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Administrator.date_added.desc())
        
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.AdministratorResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )


    @classmethod
    def authenticate(cls, db: Session, email: str, password: str, role_group: str) -> Optional[models.Administrator]:
        db_obj: models.Administrator = db.query(models.Administrator).filter(
            models.Administrator.email == email,
            models.Administrator.role.has(models.Role.group == role_group)
        ).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


nursery = CRUDNursery(models.Nursery)


