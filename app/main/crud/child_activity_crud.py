import math
from typing import Any, Dict, Optional
import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import ChildActivity
from app.main.schemas import ChildActivityCreate, ChildActivityUpdate, ChildActivityList


class CRUDChildActivity(CRUDBase[ChildActivity, ChildActivityCreate, ChildActivityUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: ChildActivityCreate) -> ChildActivity:
        
        for child_uuid in obj_in.child_uuids:
            db_obj = ChildActivity(
                uuid=str(uuid.uuid4()),
                activity_time=obj_in.activity_time,
                added_by_uuid=obj_in.employee_uuid,
                child_uuid=child_uuid,
                nursery_uuid=obj_in.nursery_uuid,
                activity_uuid=obj_in.activity_uuid
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_child_activity_by_uuid(cls, db: Session, child_activity_uuid: str) -> Optional[ChildActivity]:
        return db.query(ChildActivity).filter(ChildActivity.uuid == child_activity_uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: ChildActivityUpdate) -> ChildActivity:
        child_activity = cls.get_child_activity_by_uuid(db, obj_in.uuid)
        child_activity.activity_time = obj_in.activity_time if obj_in.activity_time else child_activity.activity_time
        child_activity.activity_uuid = obj_in.activity_uuid if obj_in.activity_uuid else child_activity.activity_uuid
        db.commit()
        db.refresh(child_activity)
        return child_activity
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> ChildActivity:
        db.query(ChildActivity).filter(ChildActivity.uuid.in_(uuids)).delete()
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
        record_query = db.query(ChildActivity)

        # if keyword:
        #     record_query = record_query.filter(
        #         or_(
        #             ChildActivity.observation.ilike('%' + str(keyword) + '%')
        #         )
        #     )

        if child_uuid:
            record_query = record_query.filter(ChildActivity.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(ChildActivity.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(ChildActivity.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(ChildActivity, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(ChildActivity, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return ChildActivityList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

child_activity = CRUDChildActivity(ChildActivity)
