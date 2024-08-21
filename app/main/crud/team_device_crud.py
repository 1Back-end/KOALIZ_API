import math
from typing import Any, Dict, Optional, Union
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main import crud
from app.main.core.security import generate_code
from app.main.crud.base import CRUDBase
from app.main.models import TeamDevice
from app.main.schemas import TeamDeviceCreate, TeamDeviceUpdate, DataList, TeamDeviceList


class CRUDTeamDevice(CRUDBase[TeamDevice, TeamDeviceCreate, TeamDeviceUpdate]):

    @classmethod
    def is_nursery_team_device(cls,db:Session,team_device_uuid:str,nursery_uuid:str)->bool:
        device = db.query(TeamDevice).filter(TeamDevice.uuid == team_device_uuid).first()
        return device.nursery_uuid == nursery_uuid

        
    @classmethod
    def create(self, db: Session, obj_in: TeamDeviceCreate) -> TeamDevice:

        code = generate_code(length=15)

        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["uuid"] = str(uuid.uuid4())
        obj_in_data["code"] = str(code)
        db_obj = TeamDevice(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(
            self, db: Session, *, db_obj: TeamDevice, obj_in: Union[TeamDeviceUpdate, Dict[str, Any]]
    ) -> TeamDevice:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


    @classmethod
    def delete(self, db: Session, uuids: list[str]) -> DataList:

        team_devices = db.query(TeamDevice).filter(TeamDevice.uuid.in_(uuids))
        team_devices.delete(synchronize_session=False)
        db.commit()

    @classmethod
    def get_by_team_device_name(cls, db: Session, name: str) -> Optional[TeamDevice]:
        res = db.query(TeamDevice)
        res = res.filter(
                or_(
                    TeamDevice.name.ilike(str(name))

                )
            ).\
            first()
        return res
    
    @classmethod
    def get_by_team_device_name_for_nursery(cls, db: Session, name: str, nursery_uuid: str) -> Optional[TeamDevice]:
        res = db.query(TeamDevice).filter(TeamDevice.nursery_uuid==nursery_uuid)
        res = res.filter(
                or_(
                    TeamDevice.name.ilike(str(name))

                )
            ).\
            first()
        return res

    @classmethod
    def get_by_team_device_code(cls, db: Session, code: str) -> Optional[TeamDevice]:
        res = db.query(TeamDevice)
        res = res.filter(
                or_(
                    TeamDevice.code.ilike(str(code))

                )
            ).\
            first()
        return res
    
    @classmethod
    def get_by_team_device_uuid(cls, db: Session, device_uuid: str) -> Optional[TeamDevice]:
        return db.query(TeamDevice).filter(TeamDevice.uuid==device_uuid).first()
    
    @classmethod
    def get_device_by_nursery_uuid(cls, db: Session, nursery_uuid: str) -> Optional[TeamDevice]:
        return db.query(TeamDevice).filter(TeamDevice.nursery_uuid==nursery_uuid).first()


    def get_many(self,
        db,
        nursery_uuid,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_field: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        record_query = db.query(TeamDevice).filter(TeamDevice.nursery_uuid==nursery_uuid)


        if keyword:
            record_query = record_query.filter(TeamDevice(
                or_(
                    TeamDevice.code.ilike('%' + str(keyword) + '%'),
                    TeamDevice.name.ilike('%' + str(keyword) + '%'),
                ))
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(TeamDevice, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(TeamDevice, order_field).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return TeamDeviceList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

team_device = CRUDTeamDevice(TeamDevice)
