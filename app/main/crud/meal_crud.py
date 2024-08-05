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

    def get_meal_by_nursery(self, db: Session, nursery_uuid: str) -> Optional[List[models.Meal]]:
        return db.query(models.Meal).filter(models.Meal.nursery_uuid == nursery_uuid).all()
    
    def get_meal_by_uuid(self, db: Session, uuid: str) -> Optional[models.Meal]:
        return db.query(models.Meal).filter(models.Meal.uuid == uuid).first()

    def create_meal(self,*,db:Session, obj_in:schemas.MealCreate):
        db_meal = models.Meal(
            uuid=str(uuid.uuid4()),
            meal_time=obj_in.meal_time,
            bottle_milk_ml=obj_in.bottle_milk_ml,
            breastfeeding_duration_minutes=obj_in.breastfeeding_duration_minutes,
            meal_quality=obj_in.meal_quality,
            observation=obj_in.observation,
            nursery_uuid=obj_in.nursery_uuid,
            child_uuid=obj_in.child_uuid
        )
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        return db_meal
    
    def get_meal_by_child(self, db: Session, child_uuid: str) -> Optional[List[models.Meal]]:
        return db.query(models.Meal).filter(models.Meal.child_uuid == child_uuid).all()
    
    def update_meal(self, *, db: Session, uuid: str, obj_in: schemas.MealUpdate):
        # Récupérer le repas existant
        db_meal = self.get_meal_by_uuid(db, uuid)
        if not db_meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        # Mettre à jour les champs du repas si les valeurs sont fournies
        if obj_in.meal_time is not None:
            db_meal.meal_time = obj_in.meal_time
        if obj_in.bottle_milk_ml is not None:
            db_meal.bottle_milk_ml = obj_in.bottle_milk_ml
        if obj_in.breastfeeding_duration_minutes is not None:
            db_meal.breastfeeding_duration_minutes = obj_in.breastfeeding_duration_minutes
        if obj_in.meal_quality is not None:
            db_meal.meal_quality = obj_in.meal_quality
        if obj_in.observation is not None:
            db_meal.observation = obj_in.observation
        if obj_in.nursery_uuid is not None:
            db_meal.nursery_uuid = obj_in.nursery_uuid
        if obj_in.child_uuid is not None:
            db_meal.child_uuid = obj_in.child_uuid
        # Commit les changements dans la base de données
        db.commit()
        db.refresh(db_meal)
        

    def delete_meal(self,*, db: Session, uuid: str, device_uuid:str):
        db_meal = self.get_meal_by_uuid(db, uuid)
        if not db_meal:
            raise HTTPException(status_code=404, detail=__("meal not found"))
        
        if db_meal.added_by_uuid!= device_uuid:
            raise HTTPException(status_code=403, detail=__("unauthorized to delete this meal"))
        
        db.delete(db_meal)
        db.commit()


meal = CRUDMeal(models.Meal)
        
        
