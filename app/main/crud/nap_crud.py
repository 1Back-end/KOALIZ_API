import math
from typing import Any, Dict, Optional, Union
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main import crud
from app.main.crud.base import CRUDBase
from app.main.models import Nap
from app.main.schemas import NapCreate, NapUpdate, DataList, NapList


class CRUDNap(CRUDBase[Nap, NapCreate, NapUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: NapCreate) -> Nap:

        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["uuid"] = str(uuid.uuid4())
        db_obj = Nap(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

nap = CRUDNap(Nap)
