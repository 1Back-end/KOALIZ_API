import math
from typing import Any, Dict, Optional,List
import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import ChildActivity,AbsenceStatusEnum
from app.main.schemas import ChildActivityCreate, ChildActivityUpdate, ChildActivityList,ChildActivityDetails,ChildActivityDelete


class CRUDChildActivity(CRUDBase[ChildActivity, ChildActivityCreate, ChildActivityUpdate]):

    @classmethod
    def create(cls, db: Session, obj_in: ChildActivityCreate):
        for child_uuid in obj_in.child_uuids:
            db_obj = cls.get_by_activity_uuid_and_child_uuid(db,obj_in.activity_uuid,child_uuid)
            if db_obj:

                db_obj.activity_time = obj_in.activity_time
            else:
                db_obj = ChildActivity(
                    activity_time=obj_in.activity_time,
                    added_by_uuid=obj_in.employee_uuid if obj_in.employee_uuid else None,
                    child_uuid=child_uuid,
                    nursery_uuid=obj_in.nursery_uuid if obj_in.nursery_uuid else None,
                    activity_uuid=obj_in.activity_uuid
                )
                db.add(db_obj)
                db.flush()
            print("Added-child-activity",db_obj)
            # child_activities.append(db_obj)
        db.commit()
        return db_obj 
    
    @classmethod
    def get_by_activity_uuid_and_child_uuid(cls, db: Session, activity_uuid: str,child_uuid:str) -> Optional[ChildActivity]:
        return db.query(ChildActivity).\
            filter(ChildActivity.activity_uuid == activity_uuid,
                   ChildActivity.child_uuid == child_uuid,
                   ChildActivity.status!= AbsenceStatusEnum.DELETED).\
                first()
    
    @classmethod
    def update(cls, db: Session,obj_in: ChildActivityUpdate) -> ChildActivity:
        child_activity = cls.get_by_activity_uuid_and_child_uuid(db, obj_in.activity_uuid,obj_in.child_uuid)
        child_activity.activity_time = obj_in.activity_time if obj_in.activity_time else child_activity.activity_time
        # child_activity.activity_uuid = obj_in.activity_uuid if obj_in.activity_uuid else child_activity.activity_uuid
        db.commit()
        db.refresh(child_activity)
        return child_activity
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> ChildActivity:
        db.query(ChildActivity).filter(ChildActivity.uuid.in_(uuids)).delete()
        db.commit()

    @classmethod
    def soft_delete(cls,db:Session, obj_in:list[ChildActivityDelete]):
        for obj in obj_in:
            exist_child_activity = cls.get_by_activity_uuid_and_child_uuid(
                db,
                obj.activity_uuid,
                obj.child_uuid
            )
            if exist_child_activity:
                exist_child_activity.status = AbsenceStatusEnum.DELETED
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
        record_query = db.query(ChildActivity).filter(ChildActivity.status!=AbsenceStatusEnum.DELETED)

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
