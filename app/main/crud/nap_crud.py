import math
from typing import Any, Dict, Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Nap
from app.main.schemas import NapCreate, NapUpdate, NapList, NapMini


class CRUDNap(CRUDBase[Nap, NapCreate, NapUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: NapCreate) -> Nap:

        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["uuid"] = str(uuid.uuid4())
        obj_in_data["added_by_uuid"] = obj_in.employee_uuid
        db_obj = Nap(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_nap_by_uuid(cls, db: Session, uuid: str) -> Optional[NapMini]:
        return db.query(Nap).filter(Nap.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: NapUpdate) -> NapMini:
        nap = cls.get_nap_by_uuid(db, obj_in.uuid)
        nap.start_time = obj_in.start_time if obj_in.start_time else nap.start_time
        nap.end_time = obj_in.end_time if obj_in.end_time else nap.end_time
        nap.quality = obj_in.quality if obj_in.quality else nap.quality
        nap.observation = obj_in.observation if obj_in.observation else nap.observation
        db.commit()
        db.refresh(nap)
        return nap
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> NapMini:
        db.query(Nap).filter(Nap.uuid.in_(uuids)).delete()
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
        quality:Optional[str]= None
    ):
        record_query = db.query(Nap)

        if keyword:
            record_query = record_query.filter(
                or_(
                    Nap.observation.ilike('%' + str(keyword) + '%')
                )
            )

        if quality:
            record_query = record_query.filter(Nap.quality == quality)
        if child_uuid:
            record_query = record_query.filter(Nap.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(Nap.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(Nap.employee_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(Nap, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Nap, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return NapList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

nap = CRUDNap(Nap)
