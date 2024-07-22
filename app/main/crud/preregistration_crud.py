from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug


class CRUDPreRegistration(CRUDBase[models.PreRegistration, schemas.PreregistrationCreate, schemas.PreregistrationUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.PreRegistration]:
        return db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()

    @classmethod
    def get_child_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Child]:
        return db.query(models.Child).filter(models.Child.uuid == uuid).first()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.PreregistrationCreate, current_user_uuid: str) -> models.Child:

        obj_in.nurseries = set(obj_in.nurseries)
        nurseries = crud.nursery.get_by_uuids(db, obj_in.nurseries)
        if len(obj_in.nurseries) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        child = models.Child(
            uuid=str(uuid.uuid4()),
            firstname=obj_in.child.firstname,
            lastname=obj_in.child.lastname,
            gender=obj_in.child.gender,
            birthdate=obj_in.child.birthdate,
            birthplace=obj_in.child.birthplace
        )
        db.add(child)

        contract = models.Contract(
            uuid=str(uuid.uuid4()),
            begin_date=obj_in.contract.begin_date,
            end_date=obj_in.contract.end_date,
            typical_weeks=jsonable_encoder(obj_in.contract.typical_weeks)
        )
        db.add(contract)

        child.contract_uuid = contract.uuid

        for pg in obj_in.parents:
            parent_guest = models.ParentGuest(
                uuid=str(uuid.uuid4()),
                link=pg.link,
                firstname=pg.firstname,
                lastname=pg.lastname,
                birthplace=pg.birthplace,
                fix_phone=pg.fix_phone,
                phone=pg.phone,
                email=pg.email,
                recipient_number=pg.recipient_number,
                zip_code=pg.zip_code,
                city=pg.city,
                country=pg.country,
                profession=pg.profession,
                annual_income=pg.annual_income,
                company_name=pg.company_name,
                has_company_contract=pg.has_company_contract,
                dependent_children=pg.dependent_children,
                disabled_children=pg.disabled_children,
                child_uuid=child.uuid
            )
            db.add(parent_guest)

        code = cls.code_unicity(code=generate_slug(f"{child.firstname} {child.lastname}"), db=db)
        for nursery_uuid in obj_in.nurseries:
            new_preregistration = models.PreRegistration(
                uuid=str(uuid.uuid4()),
                code=code,
                child_uuid=child.uuid,
                nursery_uuid=nursery_uuid,
                contract_uuid=contract.uuid,
                note=obj_in.note,
                status=models.PreRegistrationStatusType.PENDING
            )
            db.add(new_preregistration)

        db.commit()
        db.refresh(child)

        return child

    @classmethod
    def get_by_code(cls, db: Session, code: str) -> Optional[models.PreRegistration]:
        return db.query(models.PreRegistration).filter(models.PreRegistration.code == code).first()


    @classmethod
    def code_unicity(cls, code: str, db: Session):
        while cls.get_by_code(db, code):
            slug = f"{code}-{generate_code(length=4)}"
            return cls.code_unicity(slug, db)
        return code

    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


preregistration = CRUDPreRegistration(models.PreRegistration)


