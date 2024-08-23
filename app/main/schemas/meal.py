from enum import Enum
from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

from app.main.models.children import MealQuality,MealTypeEnum
from app.main.schemas.base import DataList
from app.main.schemas.employee import EmployeBase
from app.main.schemas.nursery import NurserySlim
from app.main.schemas.preregistration import ChildMini2



class MealBase(BaseModel):
    meal_time: Optional[datetime]=None
    bottle_milk_ml: Optional[int] = None
    meal_quality: Optional[MealQuality]=None
    meal_type:MealTypeEnum
    observation: Optional[str] = None
    nursery_uuid: str
    child_uuids: list[str]
    employee_uuid : str


class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    uuid: str
    meal_time: Optional[datetime] = None
    bottle_milk_ml: Optional[int] = None
    breastfeeding_duration_minutes: Optional[int] = None
    meal_quality: Optional[MealQuality] = None
    meal_type:MealTypeEnum
    observation: Optional[str] = None
    nursery_uuid: str
    child_uuids: list[str]
    employee_uuid: str 


class MealResponse(BaseModel):
    uuid: Optional[str] = None
    child: Optional[ChildMini2] = None
    meal_time: Optional[datetime] = None
    bottle_milk_ml: Optional[int] = None
    breastfeeding_duration_minutes: Optional[int] = None
    meal_quality: Optional[MealQuality] = None
    meal_type: Optional[MealTypeEnum] = None
    observation: Optional[str] = None    
    nursery: Optional[NurserySlim]=None
    added_by: Optional[EmployeBase]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

    
class MeaList(DataList):
    data: list[MealResponse]

   