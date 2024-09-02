from datetime import date, datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import Date, cast, or_

from app.main.core.i18n import __, get_language
from app.main.core.mail import admin_send_new_nursery_email, send_new_nursery_email
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session, joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug
from app.main.models.preregistration import Child, PreRegistration, PreRegistrationStatusType


class CRUDInvoicingSettings(CRUDBase[models.QuoteSetting, schemas.QuoteSettingsUpdate, schemas.QuoteSettingUpdate]):
    def get_by_uuid(self, db: Session, uuid: str):
        return db.query(self.model).filter(self.model.uuid == uuid).filter(
            self.model.is_deleted == False
        ).first()

    def get_default_quote_settings(self, db: Session, nursery_uuid: str):
        return db.query(self.model).filter(self.model.nursery_uuid == nursery_uuid).filter(
            self.model.is_default == True).first()

    def get_by_nursery_uuid(self, db: Session, nursery_uuid: str):
        return db.query(self.model).filter(self.model.nursery_uuid == nursery_uuid).first()

    def create_quote_settings(self, db: Session, obj_in: schemas.QuoteSettingCreate):
        obj = self.model(**obj_in.model_dump(exclude_unset=True), uuid=str(uuid.uuid4()))
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_quote_settings(self, db: Session, nursery_uuid: str, current_user_uuid: str, page: int, per_page: int,
                           order: str = "desc", order_filed: str = "date_added", is_default: bool = None):
        query = db.query(self.model).filter(
            self.model.nursery_uuid == nursery_uuid).filter(
            self.model.nursery.has(models.Nursery.owner_uuid == current_user_uuid)).filter(self.model.is_deleted == False)

        if is_default is not None:
            query = query.filter(self.model.is_default == is_default)
        try:
            query = query.order_by(getattr(getattr(self.model, order_filed), order)())
        except:
            query = query.order_by(self.model.date_added.desc())

        query = query.offset((page - 1) * per_page).limit(per_page)
        total = query.count()

        return schemas.DataList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=query.all()
        )

    def update_quote_settings(self, db: Session, db_obj: models.QuoteSetting, obj_in: schemas.QuoteSettingsUpdate):
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_default_quote_settings(self, db: Session, uuid: str):
        db.query(self.model).filter(self.model.is_default == True).update({self.model.is_default: False})
        db.query(self.model).filter(self.model.uuid == uuid).update({self.model.is_default: True})
        db.commit()
        return self.get_by_uuid(db, uuid)

    def delete_quote_settings(self, db: Session, uuid: str):
        db.query(self.model).filter(self.model.uuid == uuid).update({self.model.is_deleted: True})
        db.commit()
        # Also soft delete linked hourly rate range
        self.delete_hourly_rate_range_by_quote_setting(db, uuid)

    def get_hourly_rate_range_by_quote_setting_and_number_of_day(self, db: Session, quote_setting_uuid: str, number_of_day: int):
        return db.query(models.HourlyRateRange).filter(models.HourlyRateRange.quote_setting_uuid == quote_setting_uuid).filter(
            models.HourlyRateRange.number_of_day == number_of_day).filter(
            models.HourlyRateRange.is_deleted == False).first()

    def create_hourly_rate_range(self, db: Session, obj_in: schemas.HourlyRateRangeCreate):
        obj = models.HourlyRateRange(**obj_in.model_dump(exclude_unset=True), uuid=str(uuid.uuid4()))
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_hourly_rate_range_by_uuid(self, db: Session, uuid: str):
        return db.query(models.HourlyRateRange).filter(models.HourlyRateRange.uuid == uuid).filter(
            models.HourlyRateRange.is_deleted == False).first()

    def update_hourly_rate_range(self, db: Session, db_obj: models.HourlyRateRange,
                                 obj_in: schemas.HourlyRateRangeUpdate):
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_hourly_rate_range(self, db: Session, uuid: str):
        db.query(models.HourlyRateRange).filter(models.HourlyRateRange.uuid == uuid).update(
            {models.HourlyRateRange.is_deleted: True})
        db.commit()

    def delete_hourly_rate_range_by_quote_setting(self, db: Session, quote_setting_uuid: str):
        db.query(models.HourlyRateRange).filter(models.HourlyRateRange.quote_setting_uuid == quote_setting_uuid).update(
            {models.HourlyRateRange.is_deleted: True})
        db.commit()


invoicing_settings = CRUDInvoicingSettings(models.QuoteSetting)
