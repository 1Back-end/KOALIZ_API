from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_, and_

from app.main.core.i18n import __, get_language
from app.main.core.mail import send_account_creation_email
from app.main.crud.base import CRUDBase
from app.main.crud.role_crud import role as crud_role
from sqlalchemy.orm import Session,joinedload
from app.main import schemas, models
from app.main.core.config import Config
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
        lang: str = get_language()
        send_account_creation_email(email_to=obj_in.email, prefered_language=lang, name=obj_in.firstname,
                                    password=password, login_link=Config.LOGIN_LINK.format(lang))
        return user
    
    @classmethod
    def update(cls, db: Session, user: models.Owner, obj_in: Union[schemas.OwnerUpdate, dict]) -> models.Administrator:
        if type(obj_in) != dict:
            obj_in = obj_in.model_dump(exclude_unset=True)
        return super().update(models.Owner, db, db_obj=user, obj_in=obj_in)

    @classmethod
    def delete(cls, db: Session, uuids: list[str]) -> None:
        uuids = list(set(uuids))
        users = cls.get_by_uuids(db, uuids)

        if len(uuids) != len(users):
            raise HTTPException(status_code=404, detail=__("user-not-found"))

        for user in users:
            if user.role.code != "assistant":
                raise HTTPException(status_code=403, detail=__("user-not-assistant"))

        for user in users:
            user.status = models.UserStatusType.DELETED
            db.commit()

    def delete_assistants(self, db: Session, uuids: list[str], owner_uuid: str, nursery_uuid: str) -> None:
        uuids = list(set(uuids))
        users = self.get_by_uuids(db, uuids, role_code="assistant")

        if len(uuids) != len(users):
            raise HTTPException(status_code=404, detail=__("user-not-found"))

        for user in users:
            if not any([nursery.uuid == nursery_uuid for nursery in user.structures]):
                raise HTTPException(status_code=403, detail=__("nursery-assistant-not-authorized"))

        for user in users:
            if not any([nursery.owner_uuid == owner_uuid for nursery in user.structures]):
                raise HTTPException(status_code=403, detail=__("nursery-owner-not-authorized"))

        # Delete user from the nursery(NurseryUser) and if the nursery is the last one delete user completely
        nursery_users: list[models.NurseryUser] = db.query(models.NurseryUser).filter(models.NurseryUser.user_uuid.in_(uuids))\
            .filter(models.NurseryUser.nursery_uuid == nursery_uuid).all()
        for nursery_user in nursery_users:
            db.delete(nursery_user)
            db.commit()
            db.refresh(nursery_user.user)
            if not nursery_user.user.structures:
                nursery_user.user.status = models.UserStatusType.DELETED
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
        nurser_uuid: str = None,
        role_code: str = None,
        owner_uuid: str = None
    ):
        print(owner_uuid)
        record_query = db.query(models.Owner).filter(models.Owner.status != models.UserStatusType.DELETED)

        if role_code:
            if nurser_uuid and owner_uuid:
                record_query = record_query.filter(
                    models.Owner.structures.any(and_(
                        models.Nursery.uuid == nurser_uuid,
                        models.Nursery.owner_uuid == owner_uuid
                    ))
                )
            record_query = record_query.filter(models.Owner.role.has(models.Role.code == role_code))
        else:
            if nurser_uuid:
                record_query = record_query.join(models.Owner.nurseries).filter(models.Nursery.uuid == nurser_uuid)
            record_query = record_query.filter(models.Owner.role.has(models.Role.code == "owner"))

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
    def get_by_uuids(cls, db: Session, uuids: list[str], role_code: str = None) -> list[Optional[models.Owner]]:
        query = db.query(models.Owner).filter(models.Owner.uuid.in_(uuids))\
            .filter(models.Owner.status.notin_([models.UserStatusType.DELETED]))
        if role_code:
            query = query.filter(models.Owner.role.has(models.Role.code == role_code))
        return query.all()

    def create_assistant(self, db: Session, obj_in: schemas.AssistantCreate, added_by_uuid) -> models.Owner:
        password: str = generate_password(8, 8)
        role = crud_role.get_by_code(db=db, code="assistant")
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
            status = models.UserStatusType.ACTIVED,
        )
        db.add(user)

        for nursery_uuid in obj_in.nursery_uuids:
            db.add(models.NurseryUser(uuid=str(uuid.uuid4()), nursery_uuid=nursery_uuid, user_uuid=user.uuid))

        db.commit()
        db.refresh(user)
        lang: str = get_language()
        send_account_creation_email(email_to=obj_in.email, prefered_language=lang, name=obj_in.firstname,
                                    password=password, login_link=Config.LOGIN_LINK.format(lang))
        return user

    
owner = CRUDOwner(models.Owner)


