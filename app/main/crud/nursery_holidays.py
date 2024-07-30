from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug


class NuseryHolidayCRUD(CRUDBase[models.NuseryHoliday,schemas.NurseryHolidayCreate,schemas.NurseryHolidayUpdate]):

    @classmethod
    def get_nursery_holiday_by_uuid(db: Session, holiday_uuid: str):
        return db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid == holiday_uuid).first()
    
    @classmethod
    def get_nursery_holiday(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.NuseryHoliday).offset(skip).limit(limit).all()
    
    @classmethod
    def create_nursery_holiday(db: Session, holiday: schemas.NurseryHolidayCreate):
        nursery_exists = db.query(models.Nursery).filter(models.Nursery.uuid==holiday.nursery_uuid).first()
        if not nursery_exists:
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))
        db_holidays=models.NuseryHoliday(
            uuid=str(uuid.uuid4()),
            name=holiday.name,
            day=holiday.day,
            month=holiday.month,
            is_active=holiday.is_active,
            nursery_uuid=holiday.nursery_uuid
        )
        db.add(db_holidays)
        db.commit()
        db.refresh(db_holidays)
        return db_holidays
    
    @classmethod
    def update_nursery_holiday(db: Session, holiday_uuid: str, holiday: schemas.NurseryHolidayUpdate):
        db_holiday = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid == holiday_uuid).first()
        if not db_holiday:
            raise HTTPException(status_code=404, detail=__("holiday-not-found"))
        if db_holiday.name is not None:
            db_holiday.name = holiday.name
        if db_holiday.day is not None:
            db_holiday.day = holiday.day
        if db_holiday.month is not None:
            db_holiday.month = holiday.month
        if db_holiday.is_active is not None:
            db_holiday.is_active = holiday.is_active
        db.commit()
        db.refresh(db_holiday)
        return db_holiday
    @classmethod
    def delete_nursery_holiday(db: Session, holiday_uuid: str):
        db_holiday = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid == holiday_uuid).first()
        if not db_holiday:
            raise HTTPException(status_code=404, detail=__("holiday-not-found"))
        db.delete(db_holiday)
        db.commit()


nusery_holiday = NuseryHolidayCRUD(models.NuseryHoliday)

