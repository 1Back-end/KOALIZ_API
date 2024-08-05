from enum import Enum
from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

from app.main.models.children import MealQuality



class MealBase(BaseModel):
    meal_time: datetime
    bottle_milk_ml: Optional[int] = None
    breastfeeding_duration_minutes: Optional[int] = 0
    meal_quality: MealQuality
    observation: Optional[str] = None
    nursery_uuid: Optional[str] = None
    child_uuid: Optional[str] = None
    employee_uuid : Optional[str] = None

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    meal_time: Optional[datetime] = None
    bottle_milk_ml: Optional[int] = None
    breastfeeding_duration_minutes: Optional[int] = None
    meal_quality: Optional[MealQuality] = None
    observation: Optional[str] = None
    nursery_uuid: Optional[str] = None
    child_uuid: Optional[str] = None

class MealDelete(BaseModel):
    uuid: str

class MealResponse(MealBase):
    uuid: str
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)
