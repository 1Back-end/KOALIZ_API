from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/create", response_model=schemas.EmployeResponse, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.EmployeCreate,
    # current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
):
    """
    Create new member
    """
    
    db_obj = crud.employe.get_by_email(db, obj_in.email)
    
    if obj_in.avatar_uuid:
        avatar = db.query(models.Storage).filter(models.Storage.uuid == obj_in.avatar_uuid).first()
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
    
    if db_obj:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    if obj_in.team_uuid_tab:
        teams = crud.team.get_by_uuids(db, obj_in.team_uuid_tab)
        if not teams or len(teams)!= len(obj_in.team_uuid_tab):
            raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    return crud.employe.create(db, obj_in)

@router.post("/", response_model=schemas.EmployeResponse, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.EmployeUpdate,
    # current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Update a member
    """

    db_obj = crud.employe.get_by_email(db, obj_in.email)
    
    employe = crud.employe.get_by_uuid(db, obj_in.uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    if obj_in.avatar_uuid:
        avatar = db.query(models.Storage).filter(models.Storage.uuid == obj_in.avatar_uuid).first()
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
    
    if db_obj and db_obj.email!=employe.email:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    if obj_in.team_uuid_tab:
        teams = crud.team.get_by_uuids(db, obj_in.team_uuid_tab)
        if not teams or len(teams)!= len(obj_in.team_uuid_tab):
            raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    return crud.administrator.update(db, obj_in)

@router.delete("/{uuid}", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    # current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Delete a member
    """
    employees = crud.employe.get_by_uuids(db, uuids)
    if not employees:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    crud.employe.soft_delete(db, uuids)
    return {"message": __("user-deleted")}

@router.get("/", response_model=schemas.EmployeResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    user_uuid:Optional[str] = None,
    status: str = Query(None, enum =["ACTIVED","UNACTIVED"]),
    keyword:Optional[str] = None,
    # order_filed: Optional[str] = None
    # current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    get members with all data by passing filters
    """
    
    return crud.employe.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        user_uuid,
        # order_filed
        keyword
    )
    