import math
from typing import Any, Dict, Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import ActivityCategory,Activity,activity_category_table
from app.main.schemas import ActivityCategoryCreate,ActivityCategoryUpdate,ActivityCategoryList


class CRUDActivitCategory(CRUDBase[ActivityCategory, ActivityCategoryCreate, ActivityCategoryUpdate]):

    @classmethod
    def get_activity_type_by_uuid(cls, db: Session, uuid: str) -> Optional[Activity]:
        return db.query(Activity).filter(Activity.uuid == uuid).first()
    
    @classmethod
    def create(cls, db: Session, obj_in: ActivityCategoryCreate) -> ActivityCategory:
        db_obj = ActivityCategory(
            uuid=str(uuid.uuid4()),
            name_fr=obj_in.name_fr,
            name_en=obj_in.name_en,
        )
        db.add(db_obj)

        for activity_uuid in obj_in.activity_type_uuid_tab:
            activity_type = cls.get_activity_type_by_uuid(db, activity_uuid)
            if activity_type:
                exist_category_activity = db.query(activity_category_table).\
                    filter(activity_category_table.c.category_uuid == db_obj.uuid,
                           activity_category_table.c.activity_uuid ==activity_uuid).\
                            first()
                
                if not exist_category_activity:
                    activity_type = cls.get_activity_type_by_uuid(db, activity_uuid)
                    db_obj.activities.append(activity_type)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_activity_category_by_uuid(cls, db: Session, uuid: str) -> Optional[ActivityCategory]:
        return db.query(ActivityCategory).filter(ActivityCategory.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: ActivityCategoryUpdate) -> ActivityCategory:
        db_obj = cls.get_activity_category_by_uuid(db, obj_in.uuid)
        db_obj.name_fr = obj_in.name_fr if obj_in.name_fr else db_obj.name_fr
        db_obj.name_en = obj_in.name_en if obj_in.name_en else db_obj.name_en
        
        for activity_uuid in obj_in.activity_type_uuid_tab:
            activity_type = cls.get_activity_type_by_uuid(db, activity_uuid)
            if activity_type:
                exist_category_activity = db.query(activity_category_table).\
                    filter(activity_category_table.c.category_uuid == db_obj.uuid,
                           activity_category_table.c.activity_uuid ==activity_uuid).\
                            first()
                
                if not exist_category_activity:
                    activity_type = cls.get_activity_type_by_uuid(db, activity_uuid)
                    db_obj.activities.append(activity_type)

        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> ActivityCategory:
        db.query(activity_category_table).filter(activity_category_table.c.activity_uuid.in_(uuids)).delete()
        db.query(ActivityCategory).filter(ActivityCategory.uuid.in_(uuids)).delete()
        db.commit()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        # employee_uuid:Optional[str] = None,
        # nursery_uuid:Optional[str] = None,
        # child_uuid:Optional[str] = None,
        order_field:Optional[str] = 'date_added',
        keyword:Optional[str]= None,
        # quality:Optional[str]= None
    ):
        record_query = db.query(ActivityCategory)

        if keyword:
            record_query = record_query.filter(
                or_(
                    ActivityCategory.name_fr.ilike('%' + str(keyword) + '%'),
                    ActivityCategory.name_en.ilike('%' + str(keyword) + '%'),

                )
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(ActivityCategory, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(ActivityCategory, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return ActivityCategoryList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

activity_category = CRUDActivitCategory(ActivityCategory)
