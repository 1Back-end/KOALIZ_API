from typing import Optional, Any

from fastapi import Body, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from datetime import datetime, time, date

from app.main import models
from app.main.core.i18n import __
from app.main.schemas import DataList, NurseryMini
from app.main.schemas.base import Items


class TimeSlotInputSchema(BaseModel):
    """
    Model representing a time range (from_time, to_time).
    """
    from_time: str = Body(..., regex=r'^\d{2}:\d{2}$')
    to_time: str = Body(..., regex=r'^\d{2}:\d{2}$')

    @model_validator(mode='wrap')
    def validate_to_after_from(self, handler):
        validated_self = handler(self)
        try:
            from_time_obj = time.fromisoformat(validated_self.from_time)
            to_time_obj = time.fromisoformat(validated_self.to_time)
        except ValueError:
            raise ValueError(__("invalid-time-format"))

        if to_time_obj <= from_time_obj:
            raise ValueError('to_time must be after from_time')
        return validated_self

    model_config = ConfigDict(from_attributes=True)


class ContractSchema(BaseModel):
    begin_date: date
    end_date: date
    typical_weeks: list[list[list[TimeSlotInputSchema]]]

    @model_validator(mode='wrap')
    def validate_end_date(self, handler):
        validated_self = handler(self)
        for week in validated_self.typical_weeks:
            for day in week:
                if len(day) > 5:
                    raise HTTPException(status_code=422, detail=("Each week's data list cannot exceed 5 items"))

        begin_date = validated_self.begin_date
        if validated_self.end_date <= begin_date:
            raise ValueError("End date must be after to begin date.")
        return validated_self


class Contract(BaseModel):
    begin_date: date
    end_date: date
    typical_weeks: list[Any]

    model_config = ConfigDict(from_attributes=True)
