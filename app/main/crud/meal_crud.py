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


class CRUDMeal(CRUDBase[models.Meal,schemas.MealCreate, schemas.MealUpdate]):

    def get_meal_by_nursery(self, *,db: Session, nursery_uuid: str):
        return db.query(models.Meal).filter(models.Meal.nursery_uuid == nursery_uuid).all()
    
    def get_meal_by_uuid(self,*, db: Session, uuid: str):
        return db.query(models.Meal).filter(models.Meal.uuid == uuid).first()
    def get_many(
            self,
            *,
            db:Session,
            page:int = 1,
            per_page:int = 30,
            order:Optional[str] = None,
            nursery_uuid:Optional[str] = None,
            child_uuid:Optional[str] = None,
            keyword:Optional[str]= None,
            meal_quality:Optional[str]= None

    ):
        record_query = db.query(models.Meal)

        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Meal.date_added.asc())

        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Meal.date_added.desc())
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Meal.observation.ilike('%' + str(keyword) + '%'),
                    
                )
            )

        if child_uuid:
            record_query = record_query.filter(models.Meal.child_uuid == child_uuid)

        if nursery_uuid:
            record_query = record_query.filter(models.Meal.nursery_uuid == nursery_uuid)

        if meal_quality:
            record_query = record_query.filter(models.Meal.meal_quality == meal_quality)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MeaList(
            total=total,
            pages=math.ceil(total/per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )




    def create_meal(self,*,db:Session, obj_in:schemas.MealCreate):
        db_meal = models.Meal(
            uuid=str(uuid.uuid4()),
            meal_time=obj_in.meal_time,
            bottle_milk_ml=obj_in.bottle_milk_ml,
            breastfeeding_duration_minutes=obj_in.breastfeeding_duration_minutes,
            meal_quality=obj_in.meal_quality,
            observation=obj_in.observation,
            nursery_uuid=obj_in.nursery_uuid,
            child_uuid=obj_in.child_uuid,
            added_by_uuid=obj_in.employee_uuid
        )
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        return db_meal
    
    
    def update_meal(self, *, db: Session, obj_in: schemas.MealUpdate):
        # Récupérer le repas à partir de l'UUID
        db_meal = db.query(models.Meal).filter(models.Meal.uuid == obj_in.uuid).first()

        # Vérifier si le repas existe
        if not db_meal:
            raise HTTPException(status_code=404, detail="Meal not found")

        # Mettre à jour les attributs du repas uniquement si les valeurs sont fournies
        if obj_in.bottle_milk_ml is not None:
            db_meal.bottle_milk_ml = obj_in.bottle_milk_ml
        if obj_in.breastfeeding_duration_minutes is not None:
            db_meal.breastfeeding_duration_minutes = obj_in.breastfeeding_duration_minutes
        if obj_in.meal_quality is not None:
            db_meal.meal_quality = obj_in.meal_quality
        if obj_in.observation is not None:
            db_meal.observation = obj_in.observation

        # Commit the changes to the database
        db.commit()
        db.refresh(db_meal)
        return db_meal
        

    @classmethod
    def delete_meal(cls, db: Session, uuid: str):
        # Récupérer le repas à partir de l'UUID
        db_meal = db.query(models.Meal).filter(models.Meal.uuid == uuid).first()
        # Vérifier si le repas existe
        if not db_meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        # Supprimer le repas de la base de données
        db.delete(db_meal)
        db.commit()


meal = CRUDMeal(models.Meal)
        
        
