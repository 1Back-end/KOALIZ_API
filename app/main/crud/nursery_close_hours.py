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

class NurseryCloseHourCRUD(CRUDBase[models.NurseryCloseHour,schemas.NurseryCloseHourCreate,schemas.NurseryCloseHourUpdate]):

    @classmethod
    def get_nursery_close_by_uuid(cls, db: Session, close_hour_uuid: str, owner_uuid: str):
        # Jointure avec la table Nursery pour vérifier le propriétaire
        result = db.query(models.NurseryCloseHour).join(models.Nursery, models.NurseryCloseHour.nursery_uuid == models.Nursery.uuid).filter(
            models.NurseryCloseHour.uuid == close_hour_uuid,
            models.Nursery.owner_uuid == owner_uuid
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Close Hour not found or not authorized")
        
        return result
    
    def get_nursery_close_hours(
            db: Session,
            owner_uuid:str,
            page:int = 1,
            per_page:int = 30,
            order:Optional[str] = None,
            status:Optional[str] = None,
            keyword:Optional[str]= None):
        
        record_query = db.query(models.NurseryCloseHour)\
            .join(models.Nursery, models.NurseryCloseHour.nursery_uuid == models.Nursery.uuid)\
            .filter(models.Nursery.owner_uuid == owner_uuid)

        if not record_query:
            raise HTTPException(status_code=404, detail="Nurseries not found")
        
        if order and order.lower() =="asc":
            record_query = record_query.order_by(models.NurseryCloseHour.date_added.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.NurseryCloseHour.date_added.desc())

        if status in [True, False]:
            record_query = record_query.filter(models.NurseryCloseHour.is_active == status)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.NurseryCloseHour.name.ilike('%' + str(keyword) + '%'),
                
                ))
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.NurseryCloseHourResponsiveList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
            
    def create_nursery_close_hour(db: Session, close_hour: schemas.NurseryCloseHourCreate,owner_uuid: str):
        # Check if the nursery exists
        nursery_exists = db.query(models.Nursery).filter(models.Nursery.uuid == close_hour.nursery_uuid).first()
        if not nursery_exists:
            raise HTTPException(status_code=404, detail="Nursery not found")
        if nursery_exists.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to create close hour for this nursery")
        db_close_hour = models.NurseryCloseHour(
            uuid=str(uuid.uuid4()),
            nursery_uuid=close_hour.nursery_uuid,
            name=close_hour.name,
            start_day=close_hour.start_day,
            start_month=close_hour.start_month,
            end_day=close_hour.end_day,
            end_month=close_hour.end_month
            #is_active=close_hour.is_active
        )
        db.add(db_close_hour)
        db.commit()
        db.refresh(db_close_hour)
        return db_close_hour
    
    def update_nursery_close_hour(db: Session, close_hour_uuid: str, close_hour: schemas.NurseryCloseHourUpdate,owner_uuid: str):
        db_close_hour = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.uuid == close_hour_uuid).first()
        if not db_close_hour:
            raise HTTPException(status_code=404, detail="Close Hour not found")
        # Vérifiez si la crèche associée appartient au propriétaire
        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == db_close_hour.nursery_uuid).first()
        if nursery is None:
            raise HTTPException(status_code=404, detail="Nursery not found")
        if nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to update this close hour")

        # Appliquez les mises à jour en une ligne chacune
        db_close_hour.name = close_hour.name if close_hour.name is not None else db_close_hour.name
        db_close_hour.start_day = close_hour.start_day if close_hour.start_day is not None else db_close_hour.start_day
        db_close_hour.start_month = close_hour.start_month if close_hour.start_month is not None else db_close_hour.start_month
        db_close_hour.end_day = close_hour.end_day if close_hour.end_day is not None else db_close_hour.end_day
        db_close_hour.end_month = close_hour.end_month if close_hour.end_month is not None else db_close_hour.end_month
        db_close_hour.is_active = close_hour.is_active if close_hour.is_active is not None else db_close_hour.is_active
        db.commit()
        db.refresh(db_close_hour)
        return db_close_hour

    def soft_delete_nursery_close_hour(db: Session, close_hour_uuid: str, owner_uuid: str):
        db_close_hour = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.uuid == close_hour_uuid, models.NurseryCloseHour.is_deleted == False).first()
        if not db_close_hour:
            raise HTTPException(status_code=404, detail="Close Hour not found")
        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == db_close_hour.nursery_uuid).first()
        if not nursery:
            raise HTTPException(status_code=404, detail="Nursery not found")
        if nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this close hour") 
        db_close_hour.is_deleted = True
        db.commit()
        return {"detail": "Close Hour deleted"}
    
    def delete_nursery_all(db: Session, close_hour_uuid: str, owner_uuid: str):
        db_close_hour = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.uuid == close_hour_uuid).first()
        if not db_close_hour:
            raise HTTPException(status_code=404, detail="Close Hour not found")
        nursery = db.query(models.Nursery).filter(models.Nursery.uuid == db_close_hour.nursery_uuid).first()
        if not nursery:
            raise HTTPException(status_code=404, detail="Nursery not found")
        if nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this close hour")
        db.delete(db_close_hour)
        db.commit()
        return {"detail": "Close Hour deleted"}
    
nursery_close_hour = NurseryCloseHourCRUD(models.NurseryCloseHour)