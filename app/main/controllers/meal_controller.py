from app.main.core.dependencies import get_db,  TeamTokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional,List
router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=schemas.MealResponse)
def create_meal(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.MealCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.meal.create_meal(
        db=db,
        obj_in=obj_in
    )

@router.put("", response_model=schemas.MealResponse)
def update(
    *,
    db: Session = Depends(get_db), 
    obj_in: schemas.MealUpdate, 
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    # Vérifier l'existence de la nursery
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail="Nursery not found")

    # Vérifier l'existence de l'enfant
    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=(len(obj_in.child_uuids)):
        raise HTTPException(status_code=404, detail="Child not found")

    # Vérifier l'existence de l'employé
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Mettre à jour le repas
    return crud.meal.update_meal(
        db=db,
        obj_in=obj_in
    )


@router.get("",response_model=schemas.MeaList)
def get_meals(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["ASC", "DESC"]),
    nursery_uuid: Optional[str] = None,
    child_uuid: Optional[str] = None,
    keyword: Optional[str] = None,
    meal_quality: str = Query(None, enum=[st.value for st in models.MealQuality]),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[])),

):
    return crud.meal.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        nursery_uuid=nursery_uuid,
        child_uuid=child_uuid,
        keyword=keyword,
        meal_quality=meal_quality
        
    )
    
@router.delete("/{uuid}" ,response_model=schemas.Msg)
def delete(
    *,
    uuid: str,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    try:
        crud.meal.delete_meal(db=db, uuid=uuid)
        return {"message": "Meal successfully deleted"}
    except Exception as e:
        return {"detail": str(e)}
    


@router.get("/{uuid}" ,response_model=schemas.MealResponse)
def get_meal(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    db_meal = crud.meal.get_meal_by_uuid(db=db,uuid=uuid)
    if not db_meal:
        raise HTTPException(status_code=404, detail=__("meal-not-found"))
    return db_meal
