from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main.models.team import TeamStatusEnum

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/create", response_model=list[schemas.Group], status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:list[schemas.GroupCreate],
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create new Group
    """
    errors = []

    for obj in obj_in:
        if obj.team_uuid_tab:
            teams = crud.team.get_by_uuids(db,obj.team_uuid_tab)

            if not teams or len(teams)!= len(obj.team_uuid_tab):
                errors.append(obj.team_uuid_tab)
        
    if len(errors):
        raise HTTPException(status_code=404, detail=f"{__("team-not-found")}")    
    
    return crud.group.create(db, obj_in,current_user)

@router.put("/", response_model=schemas.Group, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.GroupUpdate,
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Update a Group
    """

    exist_group = crud.group.get_by_uuid(db,obj_in.uuid)
    if not exist_group:
        raise HTTPException(status_code=404, detail=__("group-not-found"))
    
    if obj_in.team_uuid_tab:
        teams = crud.team.get_by_uuids(db,obj_in.team_uuid_tab)
        if not teams or len(teams)!= len(obj_in.team_uuid_tab):
            raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    return crud.group.update(db, obj_in)

@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a Group
    """
    groups = crud.group.get_by_uuids(db, uuids)
    if not groups or len(groups)!=len(uuids):
        raise HTTPException(status_code=404, detail=__("group-not-found"))

    crud.group.soft_delete(db, uuids)
    return {"message": __("group-deleted")}

@router.delete("/team/delete", response_model=schemas.Msg)
def delete_team_from_group(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.DeleteTeamFromGroup,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a Group
    """
    group = crud.group.get_by_uuid(db, obj_in.group_uuid)
    if not group:
        raise HTTPException(status_code=404, detail=__("group-not-found"))
    
    teams = crud.team.get_by_uuids(db, obj_in.team_uuid_tab)
    if not teams or len(teams)!= len(obj_in.team_uuid_tab):
        raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    crud.group.delete_team_from_group(db, obj_in)
    return {"message": __("group-deleted")}

@router.get("/", response_model=schemas.GroupResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["asc","desc"]),
    group_uuid:Optional[str] = None,
    status: str = Query(None, enum =["CREATED","UNACTIVED","SUSPENDED"]),
    keyword:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    get Group with all data by passing filters
    """
    
    return crud.group.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        group_uuid,
        keyword
    )
    