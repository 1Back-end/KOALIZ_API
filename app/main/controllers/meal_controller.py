from app.main.core.dependencies import get_db,  TeamTokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional,List
router = APIRouter(prefix="/meal", tags=["meal"])


@router.post("/meal", response_model=schemas.MealResponse)
def create_meal(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.MealCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.meal.create_meal(
        db=db,
        obj_in=obj_in
    )
    
