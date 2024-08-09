from datetime import datetime, timedelta
import math
from typing import Union, Optional, List
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid


class CRUDTypeActivity(CRUDBase[models.Activity,schemas.ActivityCreate,schemas.ActivityUpdate]):

    def create_activity(self, *, db: Session, obj_in: schemas.ActivityCreate):
        db_obj = models.Activity(
            uuid=str(uuid.uuid4()),
            name_fr=obj_in.name_fr,
            name_en=obj_in.name_en
        )
        db.add(db_obj)
       
        for activity_uuid in obj_in.activity_category_uuid_tab:
            activity_category = self.get_by_uuid(activity_uuid, db)
            if not activity_category:
                raise HTTPException(
                    status_code=404,
                    detail=f"La catégorie d'activité avec l'UUID {activity_uuid} n'existe pas."
                )
            # db_obj.activity_categories.append(activity_category)
            exist_category_activity = db.query(activity_category_table).\
                    filter(activity_category_table.c.category_uuid == db_obj.uuid,
                           activity_category_table.c.activity_uuid ==activity_uuid).\
                            first()


    

    
       
    
    def get_by_uuid(self,uuid: str, db: Session):
       return db.query(models.ActivityCategory).filter(models.ActivityCategory).first()
    

    def update_activity(self,*,db: Session, activity_update: schemas.ActivityUpdate):
        # Récupérer l'activité existante
        activity = db.query(models.Activity).filter_by(uuid=activity_update.uuid).first()
        
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"L'activité avec l'UUID {activity_update.uuid} n'existe pas."
            )
        
        # Vérifier si une nouvelle catégorie est fournie
        if activity_update.activity_category_uuid_tab:
            valid_categories = []
            invalid_category_uuids = []
            
            for category_uuid in activity_update.activity_category_uuid_tab:
                try:
                    category = db.query(models.ActivityCategory).filter_by(uuid=category_uuid).one()
                    valid_categories.append(category)
                except NoResultFound:
                    invalid_category_uuids.append(category_uuid)
            
            if invalid_category_uuids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Les catégories suivantes n'existent pas : {', '.join(invalid_category_uuids)}"
                )
            
            # Supprimer les anciennes catégories et ajouter les nouvelles
            activity.activity_categories = valid_categories

            # Mettre à jour les champs de l'activité s'ils sont fournis
            if activity_update.name_fr:
                activity.name_fr = activity_update.name_fr
            if activity_update.name_en:
                activity.name_en = activity_update.name_en
            
            db.commit()
            db.refresh(activity)
            
            return activity

activity =  CRUDTypeActivity(models.Activity)





            
          
