from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.core.mail import send_account_creation_email, send_reset_password_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models, crud
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_password


class CRUDFather(CRUDBase[models.Father, schemas.FatherCreate,schemas.FatherUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Father, None]:
        return db.query(models.Father).filter(models.Father.uuid == uuid).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.FatherCreate) -> models.Father:
        # password:str = generate_password(8, 8)
        # send_account_creation_email(email_to=obj_in.email,prefered_language="en", name=obj_in.firstname,password=password)

        role = crud.role.get_by_code(db=db, code="parent")
        if not role:
            raise HTTPException(status_code=404, detail=__("role-not-found"))

        father = models.Father(
            uuid= str(uuid.uuid4()),
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            email = obj_in.email,
            password_hash = get_password_hash(obj_in.password),
            role_uuid = role.uuid,
            status = models.UserStatusType.ACTIVED
        )
        db.add(father)
        db.commit()
        db.refresh(father)

        return father

    @classmethod
    def update(cls, db: Session,obj_in: schemas.FatherUpdate) -> models.Father:
        father = cls.get_by_uuid(db, obj_in.uuid)
        father.firstname = obj_in.firstname if obj_in.firstname else father.firstname
        father.lastname = obj_in.lastname if obj_in.lastname else father.lastname
        father.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else father.avatar_uuid

        db.commit()
        db.refresh(father)
        return father
    
    @classmethod
    def delete(cls,db:Session, uuid) -> models.Father:
        father = cls.get_by_uuid(db, uuid)
        db.delete(father)
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, uuid) -> models.Father:
        father = cls.get_by_uuid(db, uuid)
        father.status = models.UserStatusType.DELETED
        db.commit()
    
    @classmethod
    def get_by_email(cls,db:Session,email:EmailStr) -> models.Father:
        return db.query(models.Father).filter(models.Father.email == email).first()
    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        user_uuid:Optional[str] = None,
        keyword:Optional[str]= None
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Father).options(joinedload(models.Father.role))

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Father, order_filed))

        record_query = record_query.filter(models.Father.status.not_in(["DELETED","BLOCKED"]))
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Father.firstname.ilike('%' + str(keyword) + '%'),
                    models.Father.email.ilike('%' + str(keyword) + '%'),
                    models.Father.lastname.ilike('%' + str(keyword) + '%'),
                    models.Role.title_fr.ilike('%' + str(keyword) + '%'),
                    models.Role.title_en.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Father.status == status)

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Father.date_added.asc())

        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Father.date_added.desc())

        if user_uuid:
            record_query = record_query.filter(models.Father.uuid == user_uuid)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.FatherResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )


    @classmethod
    def authenticate(cls, db: Session, email: str, password: str, role_group: str) -> Optional[models.Father]:
        db_obj: models.Father = db.query(models.Father).filter(
            models.Father.email == email,
            models.Father.role.has(models.Role.group == role_group)
        ).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    def is_active(self, user: models.Father) -> bool:
        return user.status == models.UserStatusType.ACTIVED

father = CRUDFather(models.Father)


