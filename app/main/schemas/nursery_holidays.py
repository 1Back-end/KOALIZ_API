from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

from app.main.schemas.base import DataList
class NurseryHolidayBase(BaseModel):
    name_fr: str
    name_en: str
    day: int
    month: int
    nursery_uuid: str

class NurseryHolidayCreate(NurseryHolidayBase):
    pass

class NurseryHolidayUpdate(BaseModel):
    name_fr: Optional[str]=None
    name_en: Optional[str]=None
    day: Optional[int]=None
    month: Optional[int]=None
    is_active: Optional[bool]=None

class NurseryHoliday(NurseryHolidayBase):
    uuid: str
    is_active: bool
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
    


class NurseryHolidayList(DataList):
    data: list[Optional[NurseryHoliday]]

    model_config = ConfigDict(from_attributes=True)

class NurseryHolidaysDetails(BaseModel):
        uuid : str
        name_fr: Optional[str]=None
        name_en: Optional[str]=None
        day: int
        month: int

        model_config = ConfigDict(from_attributes=True)
