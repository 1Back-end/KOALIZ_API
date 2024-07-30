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

class NurseryCloseHourCRUD:

    @classmethod
    def get_nursery_close_hour(db: Session, close_hour_uuid: str):
        return db.query(models.Nursery).filter(models.Nursery.uuid == close_hour_uuid).first()

    def get_nursery_close_hours(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Nursery).offset(skip).limit(limit).all()

    def get_nursery_by_uuid(db: Session, nursery_uuid: str):
        return db.query(models.Nursery).filter(models.Nursery.uuid == nursery_uuid).first()

    def create_nursery_close_hour(db: Session, close_hour: schemas.NurseryCloseHourCreate):
        db_close_hour = models.NurseryCloseHour(
            uuid=str(uuid.uuid4()),
            name=close_hour.name,
            start_day=close_hour.start_day,
            start_month=close_hour.start_month,
            end_day=close_hour.end_day,
            end_month=close_hour.end_month,
            is_active=close_hour.is_active,
            nursery_uuid=close_hour.nursery_uuid
        )
        db.add(db_close_hour)
        db.commit()
        db.refresh(db_close_hour)
        return db_close_hour

    def create_nursery_close_hour(db: Session, close_hour: schemas.NurseryCloseHourCreate):
        # Check if the nursery exists
        nursery_exists = db.query(models.Nursery).filter(models.Nursery.uuid == close_hour.nursery_uuid).first()
        if not nursery_exists:
            raise HTTPException(status_code=404, detail="Nursery not found")
        db_close_hour = models.NurseryCloseHour(
            uuid=str(uuid.uuid4()),
            nursery_uuid=close_hour.nursery_uuid,
            name=close_hour.name,
            start_day=close_hour.start_day,
            start_month=close_hour.start_month,
            end_day=close_hour.end_day,
            end_month=close_hour.end_month,
            is_active=close_hour.is_active
        )
        db.add(db_close_hour)
        db.commit()
        db.refresh(db_close_hour)
        return db_close_hour
    
    def update_nursery_close_hour(db: Session, close_hour_uuid: str, close_hour: schemas.NurseryCloseHourUpdate):
        db_close_hour = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.uuid == close_hour_uuid).first()
        if not db_close_hour:
            raise HTTPException(status_code=404, detail="Close Hour not found")
        if close_hour.name is not None:
            db_close_hour.name = close_hour.name
        if close_hour.start_day is not None:
            db_close_hour.start_day = close_hour.start_day
        if close_hour.start_month is not None:
            db_close_hour.start_month = close_hour.start_month
        if close_hour.end_day is not None:
            db_close_hour.end_day = close_hour.end_day
        if close_hour.end_month is not None:
            db_close_hour.end_month = close_hour.end_month
        if close_hour.is_active is not None:
            db_close_hour.is_active = close_hour.is_active
        db.commit()
        db.refresh(db_close_hour)
        return db_close_hour

    def delete_nursery_close_hour(db: Session, close_hour_uuid: str):
        db_close_hour = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.uuid == close_hour_uuid).first()
        if not db_close_hour:
            raise HTTPException(status_code=404, detail="Close Hour not found")
        db.delete(db_close_hour)
        db.commit()
        return db_close_hour