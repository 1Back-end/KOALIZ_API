from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug


class NuseryHolidayCRUD(CRUDBase[models.NuseryHoliday,schemas.NurseryHolidayCreate,schemas.NurseryHolidayUpdate]):

    def get_holiday_by_uuid(self,*, db: Session, holiday_uuid: str, owner_uuid: str):
        # Jointure avec la table Nursery pour vérifier le propriétaire
        result = db.query(models.NuseryHoliday).join(models.Nursery, models.NuseryHoliday.nursery_uuid == models.Nursery.uuid).filter(
            models.NuseryHoliday.uuid == holiday_uuid,
            models.Nursery.owner_uuid == owner_uuid
        ).first()
        if not result:
            raise HTTPException(status_code=404, detail="Nursery-not-found-or-not-authorized")
        return result
    
    def get_all_nursery(
            self,
            *,
            db:Session,
            owner_uuid:str,
            page:int = 1,
            per_page:int = 30,
            order:Optional[str] = None,
            status:Optional[str] = None,
            keyword:Optional[str]= None
):
        
        record_query = db.query(models.NuseryHoliday)\
        .join(models.Nursery, models.NuseryHoliday.nursery_uuid == models.Nursery.uuid)\
        .filter(models.Nursery.owner_uuid == owner_uuid)\
        .filter(models.NuseryHoliday.is_deleted!=True)\
        .filter(models.NuseryHoliday.is_active==True)

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.NuseryHoliday.date_added.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.NuseryHoliday.date_added.desc())
        
        if status in [True, False]:
            record_query = record_query.filter(models.NuseryHoliday.is_active == status)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.NuseryHoliday.name_fr.ilike('%' + str(keyword) + '%'),
                    models.NuseryHoliday.name_en.ilike('%' + str(keyword) + '%')
                )
            )
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.NurseryHolidayList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page = page,
            data = record_query
        )
    
    def create_nursery_holidays(self,*, db: Session,nursery_holiday: schemas.NurseryHolidayCreate, owner_uuid: str):
        db_holiday_exists = db.query(models.Nursery).filter(models.Nursery.uuid == nursery_holiday.nursery_uuid).first()
        if not db_holiday_exists:
            raise HTTPException(status_code=404, detail="Nursery-not-found")
        
        if db_holiday_exists.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not-authorized-to create-close-hour-for-this-nursery")
        
        # Generate a unique UUID for the holiday
        db_holiday = models.NuseryHoliday(
            uuid=str(uuid.uuid4()),
            nursery_uuid=nursery_holiday.nursery_uuid,
            name_fr=nursery_holiday.name_fr,
            name_en=nursery_holiday.name_en,
            day=nursery_holiday.day,
            month=nursery_holiday.month
        )
        db.add(db_holiday)
        db.commit()
        db.refresh(db_holiday)
        
        return db_holiday
    

    def update_nursery_holiday(self,*, db: Session, holiday_uuid: str, nursery_holiday: schemas.NurseryHolidayUpdate, owner_uuid: str):
        # Check if the holiday exists
        db_holiday = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid == holiday_uuid).first()
        if not db_holiday:
            raise HTTPException(status_code=404, detail="Holiday-not-found")

        # Check if the associated nursery exists and the owner is authorized
        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == db_holiday.nursery_uuid).first()
        if not nursery:
            raise HTTPException(status_code=404, detail="Nursery-not-found")
        if nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not-authorized-to-update-this-holiday")
                       # Apply updates to the holiday
        db_holiday.name_fr = nursery_holiday.name_fr if nursery_holiday.name_fr is not None else db_holiday.name_fr,
        db_holiday.name_en = nursery_holiday.name_en if nursery_holiday.name_en is not None else db_holiday.name_en,
        db_holiday.day = nursery_holiday.day if nursery_holiday.day is not None else db_holiday.day
        db_holiday.month = nursery_holiday.month if nursery_holiday.month is not None else db_holiday.month
        db.commit()
        db.refresh(db_holiday)
        
        return db_holiday
    
    
    def delete_nursery_holiday(self, db: Session, holiday_uuid: str, owner_uuid: str):
        # Check if the holiday exists
        db_holiday = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid == holiday_uuid).first()
        if not db_holiday:
            raise HTTPException(status_code=404, detail="Holiday-not-found")
        
        # Check if the associated nursery exists and the owner is authorized
        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == db_holiday.nursery_uuid).first()
        if not nursery:
            raise HTTPException(status_code=404, detail="Nursery-not-found")
        if nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not-authorized-to-delete-this-holiday")
        
        # Delete the holiday
        db.delete(db_holiday)
        db.commit()
       
    @classmethod
    def update_status(cls, uuids:List[str], status: bool, db: Session,owner_uuid: str):
        records = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid.in_(uuids)).all()
        for record in records:
            nursery = db.query(models.Nursery).filter(models.Nursery.uuid == record.nursery_uuid).first()
            if nursery is None:
                raise HTTPException(status_code=404, detail="nursery-not-found")
            if nursery.owner_uuid != owner_uuid:
                raise HTTPException(status_code=403, detail="You-are-not-authorized-to-update-this-close-hour")
            record.is_active=status
        db.commit()
        db.refresh(record)

    def soft_delete(self, uuids:List[str],db: Session, owner_uuid: str):
        # Check if the holidays exist
        db_holidays = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.uuid.in_(uuids)).all()
        if not db_holidays:
            raise HTTPException(status_code=404, detail="Holidays-not-found")
        
        # Check if the associated nurseries exist and the owner is authorized
        for holiday in db_holidays:
            nursery = db.query(models.Nursery).filter(models.Nursery.uuid == holiday.nursery_uuid).first()
            if not nursery:
                raise HTTPException(status_code=404, detail="Nursery-not-found")
            if nursery.owner_uuid != owner_uuid:
                raise HTTPException(status_code=403, detail="Not-authorized-to-delete-this-holiday")
            # Soft delete the holiday
            holiday.is_active = False
            db.commit()
            
    
nursery_holiday = NuseryHolidayCRUD(models.NuseryHoliday)
