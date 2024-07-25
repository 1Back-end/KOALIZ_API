from datetime import datetime
import math
from typing import  Optional, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.main import crud, schemas, models
import uuid
from app.main.core.security import generate_code, generate_slug
from app.main.utils.helper import convert_dates_to_strings


class CRUDPreRegistration(CRUDBase[models.PreRegistration, schemas.PreregistrationCreate, schemas.PreregistrationUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[schemas.PreregistrationDetails]:
        return db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
    
    @classmethod
    def delete_a_special_folder(cls, db: Session, folder_uuid: str, performed_by_uuid: str):
        folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == folder_uuid).first()
        if not folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        # Create the log tracking
        before_changes = schemas.PreregistrationDetails.model_validate(folder).model_dump()
        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=folder.uuid,
            action="DELETE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes={}
        )

        db.delete(folder)
        db.commit()

    @classmethod
    def change_status_of_a_special_folder(cls, db: Session, folder_uuid: str, status: str, performed_by_uuid: str) -> Optional[schemas.PreregistrationDetails]:

        exist_folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == folder_uuid).first()
        if not exist_folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))
        
        # Create the log tracking
        before_changes = schemas.PreregistrationDetails.model_validate(exist_folder).model_dump()

        exist_folder.status = status
        
        if status in ['REFUSED']:
            exist_folder.refused_date = datetime.now()

        if status in ['ACCEPTED']:
            exist_folder.accepted_date = datetime.now()

        db.commit()

        after_changes = schemas.PreregistrationDetails.model_validate(exist_folder).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=exist_folder.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        # Update others folders with refused status
        if status in ['ACCEPTED']:
            others_folders = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid!=folder_uuid).\
                filter(models.PreRegistration.child_uuid==exist_folder.child_uuid).\
                all()
            for folder in others_folders:
                folder.status = models.PreRegistrationStatusType.REFUSED
                folder.refused_date = datetime.now()
                db.commit()

        return exist_folder

    @classmethod
    def add_tracking_case(cls, db: Session, obj_in: schemas.TrackingCase, interaction_type: str, performed_by_uuid: str) -> Optional[schemas.PreregistrationDetails]:

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

        after_changes = schemas.TrackingCaseMini.model_validate(interaction).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="TrackingCase",
            entity_id=interaction.uuid,
            action="CREATE",
            before_changes={},
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return exist_folder

    @classmethod
    def update(cls, db: Session, obj_in: schemas.PreregistrationUpdate, performed_by_uuid: str) -> models.Child:

        preregistration = db.query(models.PreRegistration).\
            filter(models.PreRegistration.uuid==obj_in.uuid).\
            first()

        # Before update the data
        before_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

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
        contract = db.query(models.PreContract).filter(models.PreContract.uuid == obj_in.pre_contract.uuid).first()
        if not contract:
            raise HTTPException(status_code=404, detail=__("contract-not-found"))

        contract.begin_date=obj_in.pre_contract.begin_date,
        contract.end_date=obj_in.pre_contract.end_date,
        contract.typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)

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

        # After update the data
        after_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=preregistration.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return child
    @classmethod
    def update_pre_registration(cls, db: Session, obj_in: schemas.PreregistrationUpdate) -> models.Child:

        preregistration = db.query(models.PreRegistration).\
            filter(models.PreRegistration.uuid==obj_in.uuid).\
            first()

        # Before update the data
        before_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

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
        contract = db.query(models.PreContract).filter(models.PreContract.uuid == obj_in.pre_contract.uuid).first()
        if not contract:
            raise HTTPException(status_code=404, detail=__("contract-not-found"))

        contract.begin_date=obj_in.pre_contract.begin_date,
        contract.end_date=obj_in.pre_contract.end_date,
        contract.typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)

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

        # After update the data
        after_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=preregistration.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            after_changes=convert_dates_to_strings(after_changes)
        )

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

        contract = models.PreContract(
            uuid=str(uuid.uuid4()),
            begin_date=obj_in.pre_contract.begin_date,
            end_date=obj_in.pre_contract.end_date,
            typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)
        )
        db.add(contract)

        child.pre_contract_uuid = contract.uuid

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
                pre_contract_uuid=contract.uuid,
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

    def get_tracking_cases(self,
        db,
        preregistration_uuid,
        interaction_type,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = 'desc',
        order_field: Optional[str] = 'date_added',
        # keyword: Optional[str] = None,
    ):
        record_query = db.query(models.TrackingCase).filter(models.TrackingCase.preregistration_uuid==preregistration_uuid)
        if interaction_type:
            record_query = record_query.filter(models.TrackingCase.interaction_type==interaction_type)

        # if keyword:
        #     record_query = record_query.filter(
        #         or_(
        #             models.Child.firstname.ilike('%' + str(keyword) + '%'),
        #             models.Child.lastname.ilike('%' + str(keyword) + '%'),
        #         )
        #     )


        if order == "asc":
            record_query = record_query.order_by(getattr(models.TrackingCase, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(models.TrackingCase, order_field).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.TrackingCaseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


    def transfer(self, db, uuid, obj_in: schemas.TransferPreRegistration, current_user_uuid: str):
        preregistration = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
        if not preregistration:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
        if not nursery or nursery.owner_uuid != current_user_uuid:
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        if preregistration.nursery_uuid == obj_in.nursery_uuid:
            raise HTTPException(status_code=400, detail=__("folder-already-in-nursery"))

        preregistration.nursery_uuid = nursery.uuid
        db.commit()
        return preregistration

    @classmethod
    def code_unicity(cls, code: str, db: Session):
        while cls.get_by_code(db, code):
            slug = f"{code}-{generate_code(length=4)}"
            return cls.code_unicity(slug, db)
        return code

    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


preregistration = CRUDPreRegistration(models.PreRegistration)


