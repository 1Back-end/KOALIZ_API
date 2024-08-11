import math
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Absence
from app.main.schemas import AbsenceCreate, AbsenceUpdate, AbsenceList, AbsenceMini


class CRUDAbsence(CRUDBase[Absence, AbsenceCreate, AbsenceUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: AbsenceCreate) -> Absence:
        db_obj = Absence(
            uuid=str(uuid.uuid4()),
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            note=obj_in.note,
            added_by_uuid=obj_in.employee_uuid if obj_in.employee_uuid else None,
            child_uuid=obj_in.child_uuid if obj_in.child_uuid else None,
            nursery_uuid=obj_in.nursery_uuid if obj_in.nursery_uuid else None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_absence_by_uuid(cls, db: Session, uuid: str) -> Optional[AbsenceMini]:
        return db.query(Absence).filter(Absence.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: AbsenceUpdate) -> AbsenceMini:
        absence = cls.get_absence_by_uuid(db, obj_in.uuid)
        absence.start_time = obj_in.start_time if obj_in.start_time else absence.start_time
        absence.end_time = obj_in.end_time if obj_in.end_time else absence.end_time
        absence.note = obj_in.note if obj_in.note else absence.note
        db.commit()
        db.refresh(absence)
        return absence
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> AbsenceMini:
        db.query(Absence).filter(Absence.uuid.in_(uuids)).delete()
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
    ):
        record_query = db.query(Absence)

        if keyword:
            record_query = record_query.filter(
                or_(
                    Absence.note.ilike('%' + str(keyword) + '%')
                )
            )

        if child_uuid:
            record_query = record_query.filter(Absence.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(Absence.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(Absence.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(Absence, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Absence, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return AbsenceList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

absence = CRUDAbsence(Absence)
