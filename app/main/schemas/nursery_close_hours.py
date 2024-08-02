from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

class NurseryCloseHourBase(BaseModel):
    name: str
    start_day: int
    start_month: int
    end_day: int
    end_month: int
    nursery_uuid: str

class NurseryCloseHourCreate(NurseryCloseHourBase):
    pass

class NurseryCloseHourUpdate(BaseModel):
    name: Optional[str] = None
    start_day: Optional[int] = None
    start_month: Optional[int] = None
    end_day: Optional[int] = None
    end_month: Optional[int] = None
    is_active: Optional[bool] = None
    nursery_uuid: Optional[str] = None

class NurseryCloseHour(NurseryCloseHourBase):
    uuid: str
    is_active: bool
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
