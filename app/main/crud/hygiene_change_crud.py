import math
from typing import Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import HygieneChange
from app.main.schemas import HygieneChangeCreate, HygieneChangeUpdate, HygieneChangeList, HygieneChangeMini


class CRUDHygieneChange(CRUDBase[HygieneChange, HygieneChangeCreate, HygieneChangeUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: HygieneChangeCreate) -> HygieneChange:

        for child_uuid in obj_in.child_uuids:
            db_obj = HygieneChange(
                uuid=str(uuid.uuid4()),
                time=obj_in.time,
                cleanliness=obj_in.cleanliness,
                pipi=obj_in.pipi,
                stool_type=obj_in.stool_type,
                additional_care=obj_in.additional_care,
                observation=obj_in.observation,
                child_uuid=child_uuid,
                nursery_uuid=obj_in.nursery_uuid,
                added_by_uuid=obj_in.employee_uuid
            )
            db.add(db_obj)
            db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_hygiene_change_by_uuid(cls, db: Session, uuid: str) -> Optional[HygieneChangeMini]:
        return db.query(HygieneChange).filter(HygieneChange.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: HygieneChangeUpdate) -> HygieneChangeMini:
        hygiene_change = cls.get_hygiene_change_by_uuid(db, obj_in.uuid)
        for child_uuid in obj_in.child_uuids:
            exist_hygiene_change_for_child = db.query(HygieneChange).\
                filter(HygieneChange.uuid == hygiene_change.uuid).\
                filter(HygieneChange.child_uuid == child_uuid).\
                first()
        
            hygiene_change.time = obj_in.time if obj_in.time else hygiene_change.time
            hygiene_change.cleanliness = obj_in.cleanliness if obj_in.cleanliness else hygiene_change.cleanliness
            if obj_in.pipi == False:
                hygiene_change.pipi = False
            if obj_in.pipi == True:
                hygiene_change.pipi = True
            hygiene_change.stool_type = obj_in.stool_type if obj_in.stool_type else hygiene_change.stool_type
            hygiene_change.additional_care = obj_in.additional_care if obj_in.additional_care else hygiene_change.additional_care
            hygiene_change.observation = obj_in.observation if obj_in.observation else hygiene_change.observation
            db.flush()
            
        db.commit()
        db.refresh(hygiene_change)
        return hygiene_change
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> HygieneChangeMini:
        db.query(HygieneChange).filter(HygieneChange.uuid.in_(uuids)).delete()
        db.commit()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        employee_uuid:Optional[str] = None,
        nursery_uuid:Optional[str] = None,
        child_uuid:Optional[str] = None,
        order_field:Optional[str] = 'date_added',
        keyword:Optional[str]= None,
        cleanliness:Optional[str]= None,
        stool_type:Optional[str]= None,
        additional_care:Optional[str]= None
    ):
        record_query = db.query(HygieneChange)

        if keyword:
            record_query = record_query.filter(
                or_(
                    HygieneChange.observation.ilike('%' + str(keyword) + '%'),
                )
            )

        if cleanliness:
            record_query = record_query.filter(HygieneChange.cleanliness == cleanliness)
        if stool_type:
            record_query = record_query.filter(HygieneChange.stool_type == stool_type)
        if additional_care:
            record_query = record_query.filter(HygieneChange.additional_care == additional_care)
        if child_uuid:
            record_query = record_query.filter(HygieneChange.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(HygieneChange.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(HygieneChange.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(HygieneChange, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(HygieneChange, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return HygieneChangeList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

hygiene_change = CRUDHygieneChange(HygieneChange)
