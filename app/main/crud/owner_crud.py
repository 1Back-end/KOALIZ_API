from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.core.mail import send_account_creation_email
from app.main.crud.base import CRUDBase
from app.main.crud.role_crud import role as crud_role
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_password


class CRUDOwner(CRUDBase[models.Owner, schemas.AdministratorCreate, schemas.AdministratorUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Owner, None]:
        return db.query(models.Owner).filter(models.Owner.uuid == uuid)\
            .filter(models.Owner.status.notin_([models.UserStatusType.BLOCKED, models.UserStatusType.DELETED])).first()

    @classmethod
    def get_by_email(cls, db: Session, email: EmailStr) -> models.Owner:
        return db.query(models.Owner).filter(models.Owner.email == email)\
            .filter(models.Owner.status.notin_([models.UserStatusType.BLOCKED, models.UserStatusType.DELETED])).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: schemas.AdministratorCreate, added_by_uuid) -> models.Owner:
        password: str = generate_password(8, 8)
        print(f"Owner password: {password}")
        role = crud_role.get_by_code(db=db, code="owner")
        if not role:
            raise HTTPException(status_code=404, detail=__("role-not-found"))

        user = models.Owner(
            uuid= str(uuid.uuid4()),
            email = obj_in.email,
            firstname = obj_in.firstname,
            lastname = obj_in.lastname,
            phone_number = obj_in.phone_number,
            password_hash = get_password_hash(password),
            role_uuid = role.uuid,
            avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else None,
            added_by_uuid = added_by_uuid,
            status = models.UserStatusType.ACTIVED,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        send_account_creation_email(email_to=obj_in.email, prefered_language="fr", name=obj_in.firstname,
                                    password=password)
        return user
    
    @classmethod
    def update(cls, db: Session, user: models.Owner, obj_in: Union[schemas.OwnerUpdate, dict]) -> models.Administrator:
        if type(obj_in) != dict:
            obj_in = obj_in.model_dump(exclude_unset=True)
        return super().update(models.Owner, db, db_obj=user, obj_in=obj_in)

    @classmethod
    def delete(cls, db: Session, uuids: list[str]) -> None:
        uuids = set(uuids)
        users = cls.get_by_uuids(db, uuids)
        if len(uuids) != len(users):
            raise HTTPException(status_code=404, detail=__("user-not-found"))
        for user in users:
            user.status = models.UserStatusType.DELETED
            db.commit()

    
    @classmethod
    def get_multi(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_filed: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        record_query = db.query(models.Owner).filter(models.Owner.status != models.UserStatusType.DELETED)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Owner.firstname.ilike('%' + str(keyword) + '%'),
                    models.Owner.lastname.ilike('%' + str(keyword) + '%'),
                    models.Owner.email.ilike('%' + str(keyword) + '%'),
                )
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Owner, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Owner, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.OwnerList(
            total=total,
            pages=math.ceil(total/per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


    @classmethod
    def authenticate(cls, db: Session, email: str, password: str, role_group: str) -> Optional[models.Owner]:
        db_obj: models.Owner = db.query(models.Owner).filter(
            models.Owner.email == email,
            models.Owner.role.has(models.Role.group == role_group)
        ).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> list[Optional[models.Owner]]:
        return db.query(models.Owner).filter(models.Owner.uuid.in_(uuids))\
            .filter(models.Owner.status.notin_([models.UserStatusType.DELETED])).all()
    
owner = CRUDOwner(models.Owner)


