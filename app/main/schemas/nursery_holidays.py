from pydantic import BaseModel,ConfigDict
from datetime import datetime
class NurseryHolidayBase(BaseModel):
    name: str
    day: int
    month: int
    is_active: bool = True
    nursery_uuid: str

class NurseryHolidayCreate(NurseryHolidayBase):
    pass

class NurseryHolidayUpdate(NurseryHolidayBase):
    pass

class NurseryHoliday(NurseryHolidayBase):
    uuid: str
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
