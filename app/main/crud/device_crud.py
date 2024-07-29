import math
from typing import Any, Dict, Optional, Union
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main import crud
from app.main.crud.base import CRUDBase
from app.main.models import Device
from app.main.schemas import DeviceCreate, DeviceUpdate, DataList


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: DeviceCreate) -> Device:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["uuid"] = str(uuid.uuid4())
        db_obj = Device(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(
            self, db: Session, *, db_obj: Device, obj_in: Union[DeviceUpdate, Dict[str, Any]]
    ) -> Device:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    @classmethod
    def get_by_user(self, db: Session, *, page: int = 1, per_page: int = 100) -> DataList:

        record_query = db.query(Device).order_by(Device.date_added.desc())

        total = record_query.count()

        result = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return DataList(
            total=total,
            pages=math.ceil(total / per_page),
            current_page=page,
            per_page=per_page,
            data=result
        )

    @classmethod
    def delete(self, db: Session, user_uuid: str, uuids: list[str] = None) -> DataList:

        devices = db.query(Device).filter_by(user_uuid=user_uuid)
        if uuids:
            devices = devices.filter(Device.uuid.in_(uuids))
        devices.delete(synchronize_session=False)
        db.commit()

    @classmethod
    def get_by_device_name(cls, db: Session, name: str) -> Optional[Device]:
        res = db.query(Device)
        res = res.filter(
                or_(
                    Device.name.ilike(str(name))

                )
            ).\
            first()

        if res and not res.qrcode:
            qrcode = crud.storage.store_qrcode(db=db, code=res.code)
            res.qrcode_uuid = qrcode.uuid if qrcode else None
            db.commit()

        return res

    @classmethod
    def get_by_device_code(cls, db: Session, code: str) -> Optional[Device]:
        res = db.query(Device)
        res = res.filter(
                or_(
                    Device.code.ilike(str(code))

                )
            ).\
            first()
        return res

device = CRUDDevice(Device)
