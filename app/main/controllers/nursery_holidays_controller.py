from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional,List

router = APIRouter(prefix="/nursery-holidays", tags=["nursery-holidays"])

@router.post("/nursery_holidays/",response_model=schemas.NurseryHoliday)
def create_nursery_holiday(
    *,
    db: Session = Depends(get_db),
    nursery_holiday: schemas.NurseryHolidayCreate,
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))):
    try:
        return crud.nursery_holiday.create_nursery_holidays(
            db=db,
            nursery_holiday=nursery_holiday,
            owner_uuid=current_user.uuid
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{uuid}",response_model=schemas.NurseryHoliday)
def read_nursery_holiday(
    *,
    holiday_uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))):
    db_nursery_holidays= crud.nursery_holiday.get_holiday_by_uuid(
        db=db,
        holiday_uuid=holiday_uuid,
        owner_uuid=current_user.uuid
    )
    if db_nursery_holidays is None:
        raise HTTPException(status_code=404, detail="Nursery holiday not found")
    return db_nursery_holidays

@router.put("/{uuid}", response_model=schemas.NurseryHoliday)
def update_nursery_holiday(
    *,
    holiday_uuid: str,
    db: Session = Depends(get_db),
    nursery_holiday: schemas.NurseryHolidayUpdate,
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))):
    db_nursery_holidays = crud.nursery_holiday.update_nursery_holiday(
        db=db,
        holiday_uuid=holiday_uuid,
        nursery_holiday=nursery_holiday,
        owner_uuid=current_user.uuid
    )
    if db_nursery_holidays is None:
        raise HTTPException(status_code=404, detail="Nursery holiday not found")
    return db_nursery_holidays



@router.get("",response_model=schemas.NurseryHolidayList)
def get(
    *,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"])),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    status: bool = None,
    keyword:Optional[str] = None,
):
    return crud.nursery_holiday.get_all_nursery(
        db=db,
        owner_uuid=current_user.uuid,
        page=page,
        per_page=per_page,
        order=order,
        status=status,
        keyword=keyword
    )

@router.delete("/nursery_holidays/{uuid}",response_model=schemas.Msg)
def delete_nursery_holiday(
    holiday_uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    # Appeler la méthode CRUD pour supprimer le jour férié
    crud.nursery_holiday.delete_nursery_holiday(
        db=db,
        holiday_uuid=holiday_uuid,
        owner_uuid=current_user.uuid
    )
    return {"message": __("Holiday deleted successfully")}

    
@router.put("/status/update")
def update_status(
    uuids : List[str],
    status: bool = None,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    # Appeler la méthode CRUD pour mettre à jour le statut
    crud.nursery_holiday.update_status(
        db=db,
        uuids=uuids,
        status=status,
        owner_uuid=current_user.uuid
    )
    return {"message": __("Holidays status updated successfully")}