import uuid
from datetime import datetime, timedelta
from typing import Union, Optional, List

from fastapi.encoders import jsonable_encoder
from pydantic_core import to_json

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.main.models import User
from app.main import schemas, models
from app.main.core.security import get_password_hash, verify_password, generate_code
from app.main import utils
from fastapi import HTTPException


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str) -> Union[models.User, None]:
        db_obj: models.User = db.query(models.User).filter(models.User.email == email).first()
        if not db_obj:
            return None
        if not verify_password(password, db_obj.password_hash):
            return None
        return db_obj


    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.email == email).first()

    @classmethod
    def resend_otp(cls, db: Session, *, db_obj: models.User) -> models.User:
        # code = generate_code(length=9)[0:5]
        code = "00000"
        db_obj.otp = code
        db_obj.otp_expired_at = datetime.now() + timedelta(minutes=5)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.UserCreate) -> models.User:
        if len(obj_in.country_code) > 5:
            raise HTTPException(status_code=400, detail="Country code cannot be longer than 5 characters")
        else:
            db_obj = models.User(
                uuid=str(uuid.uuid4()),
                full_phone_number=f"{obj_in.country_code}{obj_in.phone_number}",
                country_code=obj_in.country_code,
                phone_number=obj_in.phone_number,
                email=obj_in.email,
                password_hash=get_password_hash(obj_in.password),
                firstname=obj_in.firstname,
                lastname=obj_in.lastname,
                status=models.UserStatusType.UNACTIVED,
                birthday=obj_in.birthday if obj_in.birthday else None,
                address=obj_in.address if obj_in.address else None,
            )
            db.add(db_obj)
            db.commit()
            cls.resend_otp(db=db, db_obj=db_obj)
            return db_obj

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) -> Union[models.User, None]:
        return db.query(models.User).filter(models.User.uuid == uuid).first()

    @classmethod
    def update_profile(cls, db: Session, obj_in: schemas.UserUpdate):
        exist_storage = None

        user = db.query(User).filter(User.uuid == obj_in.user_uuid).first()
        if user:
            print("===user====",user)
            user.firstname = obj_in.firstname if obj_in.firstname else user.firstname
            user.lastname = obj_in.lastname if obj_in.lastname else user.lastname
            user.email = obj_in.email if obj_in.email else user.email

            user.country = obj_in.country_code if obj_in.country_code else user.country_code
            user.address = obj_in.address if obj_in.address else user.address
            user.phone_number = obj_in.phone_number if obj_in.phone_number else user.phone_number

            user.birthday = obj_in.birthday if obj_in.birthday else user.birthday
            user.full_phone_number = user.country_code + obj_in.phone_number if obj_in.phone_number else user.full_phone_number
            user.storage_uuid = None
            print(f".....................new uuid:{obj_in.storage_uuid}")
            print(f".....................new user:{user}")
            if obj_in.storage_uuid:
                storage_uuids = [obj_in.storage_uuid]

                exist_storage = exist_storage[0] if exist_storage else None

                user.storage_uuid = exist_storage["uuid"] if exist_storage else user.storage_uuid

                db.commit()
                db.refresh(user)
                user = jsonable_encoder(user)

                user["avatar"] = exist_storage

            return user



user = CRUDUser(models.User)
