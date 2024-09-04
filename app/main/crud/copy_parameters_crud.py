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

class DuplicateParameterCrud(CRUDBase[models.NurseryCloseHour,  schemas.NurseryCloseHourCreate,schemas.NurseryCloseHourUpdate]):


    @classmethod
    def copy_opening_hours(cls, db: Session, source_nursery_uuid: str, target_nursery_uuid: str):
        source_hours = db.query(models.NurseryOpeningHour).filter(models.NurseryOpeningHour.nursery_uuid == source_nursery_uuid).all()
        if not source_hours:
            raise HTTPException(status_code=404, detail="No-opening-hours found in source nursery")
        for source_hour in source_hours:
            # Vérifier si l'heure d'ouverture existe déjà dans la crèche cible
            existing_hour = db.query(models.NurseryOpeningHour).filter(
                models.NurseryOpeningHour.nursery_uuid == target_nursery_uuid,
                models.NurseryOpeningHour.day_of_week == source_hour.day_of_week,
                models.NurseryOpeningHour.from_time == source_hour.from_time,
                models.NurseryOpeningHour.to_time == source_hour.to_time
            ).first()

            if existing_hour:
                # Mettre à jour les heures d'ouverture existantes
                existing_hour.day_of_week = source_hour.day_of_week
                existing_hour.from_time = source_hour.from_time
                existing_hour.to_time = source_hour.to_time
            else:
                # Créer de nouvelles heures d'ouverture
                new_hour = models.NurseryOpeningHour(
                    uuid=str(uuid.uuid4()),
                    day_of_week=source_hour.day_of_week,
                    from_time=source_hour.from_time,
                    to_time=source_hour.to_time,
                    nursery_uuid=target_nursery_uuid
                )
                db.add(new_hour)
                db.commit()



    @classmethod
    def copy_nursery_close_hours(cls, db: Session, source_nursery_uuid: str, target_nursery_uuid: str):
        # Obtenir les heures de fermeture de la crèche source
        source_close_hours = db.query(models.NurseryCloseHour).filter(
            models.NurseryCloseHour.nursery_uuid == source_nursery_uuid
        ).all()
        
        if not source_close_hours:
            raise HTTPException(status_code=404, detail="No close hours found in source nursery")

        for source_close_hour in source_close_hours:
            # Vérifier si l'heure de fermeture existe déjà dans la crèche cible
            existing_close_hour = db.query(models.NurseryCloseHour).filter(
                models.NurseryCloseHour.nursery_uuid == target_nursery_uuid,
                models.NurseryCloseHour.name_en == source_close_hour.name_en,
                models.NurseryCloseHour.name_fr == source_close_hour.name_fr,
                models.NurseryCloseHour.start_day == source_close_hour.start_day,
                models.NurseryCloseHour.start_month == source_close_hour.start_month,
                models.NurseryCloseHour.end_day == source_close_hour.end_day,
                models.NurseryCloseHour.end_month == source_close_hour.end_month
            ).first()

            if existing_close_hour:
                # Mettre à jour les heures de fermeture existantes
                existing_close_hour.name_en = source_close_hour.name_en
                existing_close_hour.name_fr = source_close_hour.name_fr
                existing_close_hour.start_day = source_close_hour.start_day
                existing_close_hour.start_month = source_close_hour.start_month
                existing_close_hour.end_day = source_close_hour.end_day
                existing_close_hour.end_month = source_close_hour.end_month
                # existing_close_hour.is_active = source_close_hour.is_active
                # existing_close_hour.date_modified = datetime.now()
            else:
                # Création de nouvelles heures de fermeture
                new_close_hour = models.NurseryCloseHour(
                    uuid=str(uuid.uuid4()),
                    name_fr=source_close_hour.name_fr,
                    name_en=source_close_hour.name_en,
                    start_day=source_close_hour.start_day,
                    start_month=source_close_hour.start_month,
                    end_day=source_close_hour.end_day,
                    end_month=source_close_hour.end_month,
                    # is_active=source_close_hour.is_active,
                    # is_deleted=source_close_hour.is_deleted,
                    nursery_uuid=target_nursery_uuid,
                    # date_added=datetime.now(),
                    # date_modified=datetime.now()
                )
                db.add(new_close_hour)
                # Commit changes to the database
                db.commit()
        

    @classmethod
    def copy_nursery_holidays(cls, db: Session, source_nursery_uuid: str, target_nursery_uuid: str,owner_uuid: str):
        # Obtenir les jours fériés de la crèche source
        source_holidays = db.query(models.NuseryHoliday).filter(
            models.NuseryHoliday.nursery_uuid == source_nursery_uuid
        ).all()
        
        if not source_holidays:
            raise HTTPException(status_code=404, detail="No holidays found in source nursery")

        for holiday in source_holidays:
            # Vérifier si le jour férié existe déjà dans la crèche cible
            existing_holiday = db.query(models.NuseryHoliday).filter(
                models.NuseryHoliday.nursery_uuid == target_nursery_uuid,
                models.NuseryHoliday.name_en == holiday.name_en,
                models.NuseryHoliday.name_fr == holiday.name_fr,
                models.NuseryHoliday.day == holiday.day,
                models.NuseryHoliday.month == holiday.month
            ).first()

            # if existing_holiday:
            #     # Mettre à jour les jours fériés existants
            #     existing_holiday.name_en = holiday.name_en
            #     existing_holiday.name_fr = holiday.name_fr
            #     existing_holiday.day = holiday.day
            #     existing_holiday.month = holiday.month
            # else:
                
    
    @classmethod
    def copy_parameters_between_nurseries(cls, db: Session, source_nursery_uuid: str, target_nursery_uuid: str, owner_uuid: str, elements_to_copy: List[str]):
        # Vérification des crèches et de l'utilisateur
        source_nursery = db.query(models.Nursery).filter(models.Nursery.uuid == source_nursery_uuid).first()
        if not source_nursery:
            raise HTTPException(status_code=404, detail="source-nursery-not-found")
        
        target_nursery = db.query(models.Nursery).filter(models.Nursery.uuid == target_nursery_uuid).first()
        if not target_nursery:
            raise HTTPException(status_code=404, detail="target-nursery-not-found")
        
        if source_nursery.owner_uuid != owner_uuid or target_nursery.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="You-are-not-authorized-to-copy-parameters-between-nurseries")
        
        # Appeler les fonctions en fonction des éléments à copier
        if "opening_hours" in elements_to_copy:
            cls.copy_opening_hours(db, source_nursery_uuid, target_nursery_uuid)
        
        if "close_hours" in elements_to_copy:
            cls.copy_nursery_close_hours(db, source_nursery_uuid, target_nursery_uuid)
        
        if "holidays" in elements_to_copy:
            cls.copy_nursery_holidays(db, source_nursery_uuid, target_nursery_uuid)
        
        

        
        

   



    
copy_parameters = DuplicateParameterCrud(models.Nursery)