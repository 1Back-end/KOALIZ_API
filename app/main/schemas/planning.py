from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.preregistration import ChildMini2

from .base import DataList


class ChildPlanningBase(BaseModel):
    nursery_uuid: Optional[str] = None
    child_uuid: Optional[str] = None
    end_time: Optional[datetime] = None


class ChildPlanningCreate(ChildPlanningBase):
    pass


class ChildPlanningUpdate(ChildPlanningBase):
    uuid: Optional[str] = None

class ChildPlanning(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class ChildPlanningMini(BaseModel):
    uuid: Optional[str] = None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)



class ChildPlanningList(DataList):

    data: List[ChildPlanning] = []