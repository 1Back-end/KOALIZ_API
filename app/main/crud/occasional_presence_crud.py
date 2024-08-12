import math
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import OccasionalPresence
from app.main.schemas import OccasionalPresenceCreate, OccasionalPresenceUpdate, OccasionalPresenceList, OccasionalPresenceMini


class CRUDOccasionalPresence(CRUDBase[OccasionalPresence, OccasionalPresenceCreate, OccasionalPresenceUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: OccasionalPresenceCreate) -> OccasionalPresence:
        db_obj = OccasionalPresence(
            uuid=str(uuid.uuid4()),
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            date=obj_in.date,
            note=obj_in.note,
            added_by_uuid=obj_in.employee_uuid if obj_in.employee_uuid else None,
            child_uuid=obj_in.child_uuid,
            nursery_uuid=obj_in.nursery_uuid if obj_in.nursery_uuid else None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_occasional_presence_by_uuid(cls, db: Session, uuid: str) -> Optional[OccasionalPresenceMini]:
        return db.query(OccasionalPresence).filter(OccasionalPresence.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: OccasionalPresenceUpdate) -> OccasionalPresenceMini:
        occasional_presence = cls.get_occasional_presence_by_uuid(db, obj_in.uuid)
        occasional_presence.start_time = obj_in.start_time if obj_in.start_time else occasional_presence.start_time
        occasional_presence.end_time = obj_in.end_time if obj_in.end_time else occasional_presence.end_time
        occasional_presence.note = obj_in.note if obj_in.note else occasional_presence.note
        occasional_presence.date = obj_in.date if obj_in.date else occasional_presence.date
        db.commit()
        db.refresh(occasional_presence)
        return occasional_presence
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> OccasionalPresenceMini:
        db.query(OccasionalPresence).filter(OccasionalPresence.uuid.in_(uuids)).delete()
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
        record_query = db.query(OccasionalPresence)

        if keyword:
            record_query = record_query.filter(
                or_(
                    OccasionalPresence.note.ilike('%' + str(keyword) + '%')
                )
            )

        if child_uuid:
            record_query = record_query.filter(OccasionalPresence.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(OccasionalPresence.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(OccasionalPresence.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(OccasionalPresence, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(OccasionalPresence, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return OccasionalPresenceList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

occasional_presence = CRUDOccasionalPresence(OccasionalPresence)
