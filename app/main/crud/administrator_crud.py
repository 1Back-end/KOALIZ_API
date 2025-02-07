from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from pydantic import EmailStr
from sqlalchemy import or_
from app.main.core.i18n import __, get_language
from app.main.core.mail import send_account_creation_email, send_reset_password_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
from app.main.core.config import Config
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_password


class CRUDAdministrator(CRUDBase[models.Administrator, schemas.AdministratorCreate,schemas.AdministratorUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Administrator, None]:
        return db.query(models.Administrator).filter(models.Administrator.uuid == uuid).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.AdministratorCreate,added_by:models.Administrator) -> models.Administrator:
        password:str = generate_password(8, 8)
        lang: str = get_language()
        send_account_creation_email(email_to=obj_in.email, prefered_language=lang, name=obj_in.firstname,
                                    password=password, login_link=Config.ADMIN_LOGIN_LINK.format(lang))
        administrator = models.Administrator(
            uuid= str(uuid.uuid4()),
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            email = obj_in.email,
            added_by_uuid =added_by.uuid,
            password_hash = get_password_hash(password),
            role_uuid = obj_in.role_uuid if obj_in.role_uuid else None,
            avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else None,
            status = models.UserStatusType.UNACTIVED
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
    def update_status(cls, db: Session, admin: models.Administrator, status: models.UserStatusType) -> models.Administrator:
        admin.status = status
        db.commit()
        return admin
    
    @classmethod
    def delete(cls,db:Session, uuid) -> models.Administrator:
        administrator = cls.get_by_uuid(db, uuid)
        db.delete(administrator)
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, uuid) -> models.Administrator:
        administrator = cls.get_by_uuid(db, uuid)
        administrator.status = models.UserStatusType.DELETED
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
        status:Optional[str] = None,
        user_uuid:Optional[str] = None,
        keyword:Optional[str]= None
        # order_filed:Optional[str] = None   
    ):
        record_query = db.query(models.Administrator).options(joinedload(models.Administrator.role))

        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Administrator, order_filed))

        record_query = record_query.filter(models.Administrator.status.not_in(["DELETED","BLOCKED"]))
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Administrator.firstname.ilike('%' + str(keyword) + '%'),
                    models.Administrator.email.ilike('%' + str(keyword) + '%'),
                    models.Administrator.lastname.ilike('%' + str(keyword) + '%'),
                    models.Role.title_fr.ilike('%' + str(keyword) + '%'),
                    models.Role.title_en.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Administrator.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Administrator.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Administrator.date_added.desc())

        if user_uuid:
            record_query = record_query.filter(models.Administrator.uuid == user_uuid)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.AdministratorResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

    def get_all_active(self, db):
        return db.query(models.Administrator).filter(models.Administrator.status == models.UserStatusType.ACTIVED).all()

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
    
administrator = CRUDAdministrator(models.Administrator)


