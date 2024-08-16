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


class CRUDActivity(CRUDBase[models.Activity,schemas.ActivityCreate,schemas.ActivityUpdate]):

    @classmethod
    def get_many(
            cls,
            db:Session,
            page:int = 1,
            per_page:int = 30,
            order:Optional[str] = None,
            keyword:Optional[str]= None,
        ):
            """Récupère les activités en fonction des paramètres de pagination et de recherche."""
            record_query = db.query(models.Activity)
            if keyword:
                record_query = record_query.filter(
                    or_(
                        models.Activity.name_fr.ilike('%' + str(keyword) + '%'),
                        models.Activity.name_en.ilike('%' + str(keyword) + '%')
                    )
                )

            if order and order.lower() ==  "asc":
                record_query = record_query.order_by(models.Activity.date_added.asc())
            else:
                record_query = record_query.order_by(models.Activity.date_added.desc())

            total = record_query.count()
            record_query = record_query.offset((page - 1) * per_page).limit(per_page)

            return schemas.ActivityList(
                total = total,
                pages = math.ceil(total/per_page),
                per_page = per_page,
                current_page =page,
                data =record_query
            )

    @classmethod
    def create_activity(cls,db: Session, obj_in: schemas.ActivityCreate):
        db_obj = models.Activity(
            uuid=str(uuid.uuid4()),
            name_fr=obj_in.name_fr,
            name_en=obj_in.name_en,
        )
        db.add(db_obj)
        
        if obj_in.activity_category_uuid_tab:
            non_existing_categories = []

            for category_uuid in obj_in.activity_category_uuid_tab:
                activity_category = cls.get_category_activity_by_uuid(category_uuid, db)
                if not activity_category:
                    non_existing_categories.append(category_uuid)

            if non_existing_categories:
                raise HTTPException(
                    status_code=404,
                    detail=f"Les catégories d'activité avec les UUIDs suivants n'existent pas : {', '.join(non_existing_categories)}"
                )

            for category_uuid in obj_in.activity_category_uuid_tab:
                activity_category = cls.get_category_activity_by_uuid(category_uuid, db)
                exist_activity_category = db.query(models.activity_category_table)\
                    .filter(models.activity_category_table.c.activity_uuid == db_obj.uuid)\
                    .filter(models.activity_category_table.c.category_uuid == activity_category.uuid).first()
                
                if not exist_activity_category and activity_category:
                    db_obj.activity_categories.append(activity_category)
        
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    @classmethod
    def get_category_activity_by_uuid(cls, uuid: str, db: Session):
        return db.query(models.ActivityCategory).filter(models.ActivityCategory.uuid == uuid).first()
    
    @classmethod
    def get_activity_by_uuid(cls,activity_uuid:str,db:Session):
        return db.query(models.Activity).filter(models.Activity.uuid == activity_uuid).first()
    

    @classmethod
    def update(cls,db: Session, obj_in: schemas.ActivityUpdate):
        db_obj = cls.get_activity_by_uuid(obj_in.uuid, db)
        if not db_obj:
            raise HTTPException(status_code=404, detail=f"L'activité avec l'UUID {obj_in.uuid} n'existe pas.")
        
        db_obj.name_fr = obj_in.name_fr if obj_in.name_fr else db_obj.name_fr
        db_obj.name_en = obj_in.name_en if obj_in.name_en else db_obj.name_en


        if obj_in.activity_category_uuid_tab:
            non_existing_categories = []

            for category_uuid in obj_in.activity_category_uuid_tab:
                activity_category = cls.get_category_activity_by_uuid(category_uuid, db)
                if not activity_category:
                    non_existing_categories.append(category_uuid)

            if non_existing_categories:
                raise HTTPException(
                    status_code=404,
                    detail=f"Les catégories d'activité avec les UUIDs suivants n'existent pas : {', '.join(non_existing_categories)}"
                )

            for category_uuid in obj_in.activity_category_uuid_tab:
                activity_category = cls.get_category_activity_by_uuid(category_uuid, db)
                exist_activity_category = db.query(models.activity_category_table)\
                    .filter(models.activity_category_table.c.activity_uuid == db_obj.uuid)\
                    .filter(models.activity_category_table.c.category_uuid == activity_category.uuid).first()
                
                if not exist_activity_category and activity_category:
                    db_obj.activity_categories.append(activity_category)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    @classmethod
    def delete(cls,db:Session, uuids:list[str]):
        db.query(models.activity_category_table).filter(models.activity_category_table.c.activity_uuid.in_(uuids)).delete()
        db.query(models.Activity).filter(models.Activity.uuid.in_(uuids)).delete()
        db.commit()

    
    
        
       

activity =  CRUDActivity(models.Activity)





            
          
