import math
from typing import Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Observation
from app.main.schemas import ObservationCreate, ObservationUpdate, ObservationList, ObservationMini


class CRUDObservation(CRUDBase[Observation, ObservationCreate, ObservationUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: ObservationCreate) -> Observation:
        for child_uuid in obj_in.child_uuids:
            db_obj = Observation(
                uuid=str(uuid.uuid4()),
                time=obj_in.time,
                observation=obj_in.observation,
                added_by_uuid=obj_in.employee_uuid,
                child_uuid=child_uuid,
                nursery_uuid=obj_in.nursery_uuid,
            )
            db.add(db_obj)
            db.flush()

        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_observation_by_uuid(cls, db: Session, uuid: str) -> Optional[ObservationMini]:
        return db.query(Observation).filter(Observation.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session,obj_in: ObservationUpdate) -> ObservationMini:
        observation = cls.get_observation_by_uuid(db, obj_in.uuid)
        for child_uuid in obj_in.child_uuids:
        
            exist_observation_for_child = db.query(Observation).\
                filter(Observation.child_uuid == child_uuid, Observation.uuid == observation.uuid).\
                first()
            if exist_observation_for_child:
                observation.time = obj_in.time if obj_in.time else observation.time
                observation.observation = obj_in.observation if obj_in.observation else observation.observation
                db.flush()
        db.commit()
        db.refresh(observation)
        return observation
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> ObservationMini:
        db.query(Observation).filter(Observation.uuid.in_(uuids)).delete()
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
        record_query = db.query(Observation)

        if keyword:
            record_query = record_query.filter(
                or_(
                    Observation.observation.ilike('%' + str(keyword) + '%')
                )
            )

        if child_uuid:
            record_query = record_query.filter(Observation.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(Observation.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(Observation.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(Observation, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Observation, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return ObservationList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

observation = CRUDObservation(Observation)
