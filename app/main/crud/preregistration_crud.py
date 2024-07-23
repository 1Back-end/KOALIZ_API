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
from app.main.core.security import generate_code, generate_slug


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

    def get_elements_by_tag(self, db: Session, tag: str) -> List:

        query = db.query(models.TagElement).join(models.Tags, models.Tags.uuid==models.TagElement.tag_uuid)
        query = query.filter(or_(
            # models.Tags.title_en.ilike("%"+tag_type+"%"),
            # models.Tags.title_fr.ilike("%"+tag_type+"%")
            models.Tags.title_en==tag,
            models.Tags.title_fr==tag
        ))

        tag_elements = query.all()

        elements = []
        for tag_element in tag_elements:
            element = tag_element.element
            if element is None:
                continue  # Skip elements with no associated element

            # Dynamic element type handling (replace with your actual model mapping)
            element_type_mapping = {
                "PRE_ENROLLMENT": "PreRegistration",
                "CHILDREN": "Membership",
                "PARENTS": "ParentGuest",
                "PICTURE": "Storage",
            }
            model_name = element_type_mapping.get(tag_element.element_type)
            # if not model_name:
            #     raise ValueError(f"Unsupported element type: {tag_element.element_type}")

            # Assuming your models have a `__repr__` method for human-readable output
            element_data = element
            elements.append({"model": model_name, "data": element_data})

        return elements


    def get_many(self,
        db,
        nursery_uuid,
        tag_uuid,
        status,
        begin_date,
        end_date,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_field: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        record_query = db.query(models.PreRegistration).filter(models.PreRegistration.nursery_uuid==nursery_uuid)
        if status:
            record_query = record_query.filter(models.PreRegistration.status==status)

        if begin_date and end_date:
            record_query = record_query.filter(models.PreRegistration.date_added.between(begin_date, end_date))

        if keyword:
            record_query = record_query.filter(models.PreRegistration.child.has(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%'),
                ))
            )
        if tag_uuid:
            elements = self.get_elements_by_tag(db, tag_uuid)
            element_uuids = [element.get("data", {}).uuid for element in elements]
            record_query = record_query.filter(models.PreRegistration.uuid.in_(element_uuids))

        if order == "asc":
            record_query = record_query.order_by(getattr(models.PreRegistration, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(models.PreRegistration, order_field).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.PreRegistrationList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    @classmethod
    def code_unicity(cls, code: str, db: Session):
        while cls.get_by_code(db, code):
            slug = f"{code}-{generate_code(length=4)}"
            return cls.code_unicity(slug, db)
        return code

    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


preregistration = CRUDPreRegistration(models.PreRegistration)


