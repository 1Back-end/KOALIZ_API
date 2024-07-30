from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional,List
router = APIRouter(prefix="/nursery-close-hours", tags=["nursery-close-hours"])

@router.post("/", response_model=schemas.NurseryCloseHour)
def create_nursery_close_hour(
    close_hour: schemas.NurseryCloseHourCreate, 
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))):
    try:
        return crud.NurseryCloseHourCRUD.create_nursery_close_hour(db=db, close_hour=close_hour,owner_uuid=current_user.uuid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
@router.get("/{close_hour_uuid}", response_model=schemas.NurseryCloseHour)
def read_nursery_close_hour(close_hour_uuid: str, db: Session = Depends(get_db)):
    db_close_hour = crud.NurseryCloseHourCRUD.get_nursery_close_by_uuid(db=db, close_hour_uuid=close_hour_uuid)
    if db_close_hour is None:
        raise HTTPException(status_code=404, detail="Nursery close hour not found")
    return db_close_hour

@router.get("/", response_model=List[schemas.NurseryCloseHour])
def read_nursery_close_hours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.NurseryCloseHourCRUD.get_nursery_close_hours(db, skip=skip, limit=limit)

@router.put("/{close_hour_uuid}", response_model=schemas.NurseryCloseHour)
def update_nursery_close_hour(
    close_hour_uuid: str, 
    close_hour: schemas.NurseryCloseHourUpdate,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    try:
        return crud.NurseryCloseHourCRUD.update_nursery_close_hour(db=db, close_hour_uuid=close_hour_uuid, close_hour=close_hour, owner_uuid=current_user.uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
