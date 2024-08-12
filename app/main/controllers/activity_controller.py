from app.main.core.dependencies import get_db, TokenRequired,TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/activities", tags=["activities"])

@router.post("",response_model=schemas.ActivityResponse ,status_code=201)
def create_activity(
    *,
    obj_in: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    try:
        db_obj = crud.activity.create_activity(db=db, obj_in=obj_in)
        return db_obj
    except HTTPException as e:
        raise e  # Re-raise HTTPException to return it as a response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handle other exceptions


@router.put("",response_model=schemas.ActivityResponse)
def update_activity(
    *,
    obj_in: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
   return crud.activity.update(
        db,
        obj_in
   )


@router.get("/{uuid}", response_model=schemas.ActivityResponse)
def read_category(
    *,
    activity_uuid: str,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    category = crud.activity.get_activity_by_uuid(db=db,activity_uuid=activity_uuid)
    if not category:
        raise HTTPException(status_code=404, detail=__("activity-not-found"))
    return category



@router.get("", response_model=schemas.ActivityList)
def get_all(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    keyword: Optional[str] = None,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.activity.get_many(
        db,
        page,
        per_page,
        order,
        keyword,
    )

@router.delete("",response_model=schemas.Msg)
def delete_activity(
    uuids:list[str],
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    crud.activity.delete(
        db,
        uuids
    )
    return {"message": __("Activity deleted successfully")}

