from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional
class NurseryHolidayBase(BaseModel):
    name: str
    day: int
    month: int
    nursery_uuid: str

class NurseryHolidayCreate(NurseryHolidayBase):
    pass

class NurseryHolidayUpdate(BaseModel):
    name: Optional[str]
    day: Optional[int]
    month: Optional[int]
    is_active: Optional[bool]
    nursery_uuid: Optional[str]

class NurseryHoliday(NurseryHolidayBase):
    uuid: str
    is_active: bool
    date_added: datetime
    date_modified: datetime

    class Config:
        orm_mode: True