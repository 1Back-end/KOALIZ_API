import math
from typing import Any, Dict, Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import HealthRecord
from app.main.schemas import HealthRecordCreate, HealthRecordUpdate, HealthRecordList, HealthRecordMini


class CRUDHealthRecord(CRUDBase[HealthRecord, HealthRecordCreate, HealthRecordUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: HealthRecordCreate) -> HealthRecord:

        for child_uuid in obj_in.child_uuids:
            db_obj = HealthRecord(
                uuid=str(uuid.uuid4()),
                child_uuid=child_uuid,
                care_type=obj_in.care_type,
                route = obj_in.route,
                medication_type=obj_in.medication_type,
                medication_name=obj_in.medication_name,
                observation=obj_in.observation,
                weight=obj_in.weight,
                nursery_uuid=obj_in.nursery_uuid,
                time=obj_in.time,
                temperature=obj_in.temperature,
                added_by_uuid=obj_in.employee_uuid
            )
            db.add(db_obj)
            db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_health_record_by_uuid(cls, db: Session, uuid: str) -> Optional[HealthRecordMini]:
        return db.query(HealthRecord).filter(HealthRecord.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: HealthRecordUpdate) -> HealthRecordMini:
        health_record = cls.get_health_record_by_uuid(db, obj_in.uuid)
        for child_uuid in obj_in.child_uuids:
            exist_health_record = db.query(HealthRecord).\
                filter(HealthRecord.uuid == health_record.uuid).\
                filter(HealthRecord.child_uuid == child_uuid).\
                    first()
            if exist_health_record:
                exist_health_record.care_type = obj_in.care_type if obj_in.care_type else exist_health_record.care_type
                exist_health_record.time = obj_in.time if obj_in.time else exist_health_record.time
                exist_health_record.weight = obj_in.weight if obj_in.weight else exist_health_record.weight
                exist_health_record.temperature = obj_in.temperature if obj_in.temperature else exist_health_record.temperature
                exist_health_record.route = obj_in.route if obj_in.route else health_record.route
                exist_health_record.medication_type = obj_in.medication_type if obj_in.medication_type else exist_health_record.medication_type
                exist_health_record.medication_name = obj_in.medication_name if obj_in.medication_name else exist_health_record.medication_name
                exist_health_record.observation = obj_in.observation if obj_in.observation else exist_health_record.observation

                db.flush()
        db.commit()
        db.refresh(health_record)
        return health_record
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> HealthRecordMini:
        db.query(HealthRecord).filter(HealthRecord.uuid.in_(uuids)).delete()
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
        route:Optional[str]= None,
        care_type:Optional[str]= None,
        medication_type:Optional[str]= None
    ):
        record_query = db.query(HealthRecord)

        if keyword:
            record_query = record_query.filter(
                or_(
                    HealthRecord.observation.ilike('%' + str(keyword) + '%'),
                    HealthRecord.medication_name.ilike('%' + str(keyword) + '%')
                )
            )

        if medication_type:
            record_query = record_query.filter(HealthRecord.medication_type == medication_type)
        if care_type:
            record_query = record_query.filter(HealthRecord.care_type == care_type)
        if route:
            record_query = record_query.filter(HealthRecord.route == route)
        if child_uuid:
            record_query = record_query.filter(HealthRecord.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(HealthRecord.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(HealthRecord.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(HealthRecord, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(HealthRecord, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return HealthRecordList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

health_record = CRUDHealthRecord(HealthRecord)
