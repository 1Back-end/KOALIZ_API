import math
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Media, Child
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
            db_obj.children.append(child)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_media_by_uuid(cls, db: Session, uuid: str) -> Optional[MediaMini]:
        return db.query(Media).filter(Media.uuid == uuid).first()

    @classmethod
    def update(cls, db: Session,obj_in: MediaUpdate) -> MediaMini:
        media = cls.get_media_by_uuid(db, obj_in.uuid)
        media.file_uuid = obj_in.file_uuid if obj_in.file_uuid else media.file_uuid
        media.time = obj_in.time if obj_in.time else media.time
        media.media_type = obj_in.media_type if obj_in.media_type else media.media_type
        media.observation = obj_in.observation if obj_in.observation else media.observation

        if obj_in.child_uuids:
            media.children = []
            for child in db.query(Child).filter(Child.uuid.in_(obj_in.child_uuids)).all():
                media.children.append(child)

        db.commit()
        db.refresh(media)
        return media

    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> MediaMini:
        db.query(Media).filter(Media.uuid.in_(uuids)).delete()
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
        record_query = db.query(Media)

        if keyword:
            record_query = record_query.filter(
                or_(
                    Media.observation.ilike('%' + str(keyword) + '%')
                )
            )

        if media_type:
            record_query = record_query.filter(Media.media_type == media_type)
        if child_uuid:
            record_query = record_query.filter(Media.child_uuid == child_uuid)
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

media = CRUDMedia(Media)
