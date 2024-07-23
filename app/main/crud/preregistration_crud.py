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
import json

class CRUDPreRegistration(CRUDBase[models.PreRegistration, schemas.PreregistrationCreate, schemas.PreregistrationUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[schemas.PreregistrationDetails]:
        print(db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first())
        return db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
    
    @classmethod
    def delete_a_special_folder(cls, db: Session, uuid: str):
        folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
        if not folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))
        
        db.delete(folder)
        db.commit()

    @classmethod
    def change_status_of_a_special_folder(cls, db: Session, uuid: str, status: str) -> Optional[schemas.PreregistrationDetails]:

        exist_folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
        if not exist_folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        exist_folder.status = status
        db.commit()

        # Update others folders with refused status
        if status in ['ACCEPTED']:
            others_folders = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid!=uuid).\
                filter(models.PreRegistration.child_uuid==exist_folder.child_uuid).\
                all()
            for folder in others_folders:
                folder.status = models.PreRegistrationStatusType.REFUSED
                db.commit()

        return exist_folder
    
    @classmethod
    def add_tracking_case(cls, db: Session, obj_in: schemas.TrackingCase, interaction_type: str) -> Optional[schemas.PreregistrationDetails]:

        exist_folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == obj_in.preregistration_uuid).first()
        if not exist_folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        interaction = models.TrackingCase(
            uuid=str(uuid.uuid4()),
            preregistration_uuid=exist_folder.uuid,
            interaction_type=interaction_type,
            details=obj_in.details.root
        )
        db.add(interaction)
        db.commit()

        return exist_folder
    
    @classmethod
    def update(cls, db: Session, obj_in: schemas.PreregistrationUpdate) -> models.Child:

        obj_in.nurseries = set(obj_in.nurseries)
        nurseries = crud.nursery.get_by_uuids(db, obj_in.nurseries)
        if len(obj_in.nurseries) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        # Child information update
        child = db.query(models.Child).filter(models.Child.uuid==obj_in.child.uuid).first()
        if not child:
            raise HTTPException(status_code=404, detail=__("child-not-found"))

        child.firstname=obj_in.child.firstname
        child.lastname=obj_in.child.lastname
        child.gender=obj_in.child.gender
        child.birthdate=obj_in.child.birthdate
        child.birthplace=obj_in.child.birthplace

        # Contract information update
        contract = db.query(models.Contract).filter(models.Contract.uuid==obj_in.contract.uuid).first()
        if not contract:
            raise HTTPException(status_code=404, detail=__("contract-not-found"))

        contract.begin_date=obj_in.contract.begin_date,
        contract.end_date=obj_in.contract.end_date,
        contract.typical_weeks=jsonable_encoder(obj_in.contract.typical_weeks)

        # Delete the old parents data
        db.query(models.ParentGuest).\
            filter(models.ParentGuest.child_uuid==child.uuid).\
            delete()
        
        db.commit()

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
            preregistration = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid==obj_in.uuid).\
                filter(models.PreRegistration.nursery_uuid==nursery_uuid).\
                first()
            if preregistration:
                preregistration.code = code
                preregistration.note = obj_in.note if obj_in.note else preregistration.note
                db.commit()

        db.commit()
        db.refresh(child)

        return child

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


