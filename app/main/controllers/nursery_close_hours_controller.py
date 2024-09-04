from datetime import datetime
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional,List

router = APIRouter(prefix="/nursery-close-hours", tags=["nursery-close-hours"])

@router.post("/nursery_close_hours",response_model=schemas.NurseryCloseHour)
def create(
    *,
    db: Session = Depends(get_db),
    close_hour: schemas.NurseryCloseHourCreate, 
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):

    return crud.nursery_close_hour.create_nursery_close_hour(
        db=db,
        close_hour=close_hour,
        owner_uuid=current_user.uuid
)


@router.get("", response_model=schemas.NurseryCloseHourResponsiveList)
def get_all_nursery_close_hours(
    *,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"])),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    status: bool = None,
    keyword:Optional[str] = None
):
    
    db_close_hours = crud.nursery_close_hour.get_nursery_close_hours(
        db=db,
        owner_uuid=current_user.uuid,
        page=page, 
        per_page=per_page, 
        order=order,
        status=status,
        keyword=keyword
    )
    return db_close_hours   

@router.put("/nursery_close_hours/{close_hour_uuid}", response_model=schemas.NurseryCloseHour)
def update_nursery_close_hour(
    close_hour_uuid: str, 
    close_hour: schemas.NurseryCloseHourUpdate,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    try:
        return crud.nursery_close_hour.update_nursery_close_hour(db=db, close_hour_uuid=close_hour_uuid, close_hour=close_hour, owner_uuid=current_user.uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/nursery_close_hours/{close_hour_uuid}", response_model=schemas.Msg)
def delete_nursery_close_hour(
    close_hour_uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    crud.nursery_close_hour.delete_nursery_close_hour(
        db=db,
        close_hour_uuid=close_hour_uuid,
        owner_uuid=current_user.uuid
    )
    return {"message": __("Close-Hour-deleted-successfully")}


@router.get("/{close_hour_uuid}", response_model=schemas.NurseryCloseHour)
def read_nursery_close_hour(
    close_hour_uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    db_close_hour = crud.nursery_close_hour.get_nursery_close_by_uuid(db=db,
    close_hour_uuid=close_hour_uuid, owner_uuid=current_user.uuid)
    if db_close_hour is None:
        raise HTTPException(status_code=404, detail="Nursery-close-hour-not-found")
    return db_close_hour

@router.put("/status/update")
def update_status(
    uuids : List[str],
    status: bool = None,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    crud.nursery_close_hour.update_status(
        db=db,
        uuids=uuids,
        status=status,
        owner_uuid=current_user.uuid
    )
    return {"message": __("Close-Hour-status-updated-successfully")}

@router.delete("/soft/delete")
def soft_delete_nursery_close_hours(
    uuids : List[str],
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    crud.nursery_close_hour.soft_delete(db=db, uuids=uuids,owner_uuid=current_user.uuid)
    return {"message": __("Close-Hours-soft-deleted-successfully")}

# Modèle de requête pour la duplication des heures d'ouverture




