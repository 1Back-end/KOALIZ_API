import math
from typing import Any, Dict, Optional
import uuid

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Media, Child,children_media,AbsenceStatusEnum
from app.main.schemas import MediaCreate, MediaUpdate, MediaList, MediaMini


class CRUDMedia(CRUDBase[Media, MediaCreate, MediaUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: MediaCreate) -> Media:
        db_obj = Media(
            uuid=str(uuid.uuid4()),
            file_uuid=obj_in.file_uuid,
            time=obj_in.time,
            media_type=obj_in.media_type,
            observation=obj_in.observation,
            added_by_uuid=obj_in.employee_uuid,
            nursery_uuid=obj_in.nursery_uuid,
        )
        db.add(db_obj)
        db.flush()

        for child in db.query(Child).filter(Child.uuid.in_(obj_in.child_uuids)).all():
            exist_child_media = db.query(children_media).\
                filter(children_media.c.child_uuid == child.uuid,
                       children_media.c.media_uuid == db_obj.uuid).\
                        first()
            
            if not exist_child_media:
                db_obj.children.append(child)
                db.flush()

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_media_by_uuid(cls, db: Session, uuid: str) -> Optional[MediaMini]:
        return db.query(Media).filter(Media.uuid == uuid,Media.status!=AbsenceStatusEnum.DELETED).first()

    @classmethod
    def update(cls, db: Session,obj_in: MediaUpdate) -> MediaMini:
        media = cls.get_media_by_uuid(db, obj_in.uuid)
        media.file_uuid = obj_in.file_uuid if obj_in.file_uuid else media.file_uuid
        media.time = obj_in.time if obj_in.time else media.time
        media.media_type = obj_in.media_type if obj_in.media_type else media.media_type
        media.observation = obj_in.observation if obj_in.observation else media.observation

        for child in db.query(Child).filter(Child.uuid.in_(obj_in.child_uuids)).all():
            exist_child_media = db.query(children_media).\
                filter(children_media.c.child_uuid == child.uuid,
                       children_media.c.media_uuid == media.uuid).\
                        first()
            
            if not exist_child_media:
                media.children.append(child)
                db.flush()

        db.commit()
        db.refresh(media)
        return media

    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> MediaMini:
        db.query(Media).filter(Media.uuid.in_(uuids)).delete()
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]):
        attendance_tab = db.query(Media).\
            filter(Media.uuid.in_(uuids),Media.status!=AbsenceStatusEnum.DELETED)\
                .all()
        for attendance in attendance_tab:
            attendance.status = AbsenceStatusEnum.DELETED
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
        media_type:Optional[str]= None
    ):
        record_query = db.query(Media).filter(Media.status!=AbsenceStatusEnum.DELETED)

        if keyword:
            record_query = record_query.filter(
                or_(
                    Media.observation.ilike('%' + str(keyword) + '%')
                )
            )

        if media_type:
            record_query = record_query.filter(Media.media_type == media_type)
        if child_uuid:
            record_query = record_query.\
                join(children_media,child_uuid == children_media.c.child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(Media.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(Media.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(Media, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Media, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return MediaList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    @classmethod
    def delete_child_media_association(cls,db: Session, child_uuid: str, media_uuid: str):
    # Supprimer l'association entre l'enfant et le média
        result = db.query(children_media).filter(and_(
                    children_media.c.child_uuid == child_uuid,
                    children_media.c.media_uuid == media_uuid))
        if result:
            result.delete()
            db.commit()
            
        
        
        
media = CRUDMedia(Media)
