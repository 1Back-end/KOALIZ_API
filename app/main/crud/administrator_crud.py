from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from pydantic import EmailStr
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
import uuid
from app.main.core.security import get_password_hash


class CRUDAdministrator(CRUDBase[models.Administrator, schemas.AdministratorCreate,schemas.AdministratorUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Administrator, None]:
        return db.query(models.Administrator).filter(models.Administrator.uuid == uuid).first()
    
    
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.AdministratorCreate) -> models.Administrator:
        administrator = models.Administrator(
            uuid= str(uuid.uuid4()),
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            email = obj_in.email,
            password_hash = get_password_hash(obj_in.password),
            role_uuid = obj_in.role_uuid if obj_in.role_uuid else None,
            avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else None,
        )
        db.add(administrator)
        db.commit()
        db.refresh(administrator)
        return administrator
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.AdministratorUpdate) -> models.Administrator:
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
    def delete(cls,db:Session, uuid) -> models.Administrator:
        administrator = cls.get_by_uuid(db, uuid)
        db.delete(administrator)
        db.commit()
    
    @classmethod
    def get_by_email(cls,db:Session,email:EmailStr) -> models.Administrator:
        return db.query(models.Administrator).filter(models.Administrator.email == email).first()
    
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

    
administrator = CRUDAdministrator(models.Administrator)


