from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/create", response_model=schemas.TeamResponse, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TeamCreate,
    # current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
):
    """
    Create new Team
    """
    
    employe = crud.employe.get_by_uuid(db,obj_in.leader_uuid)

    if  not employe:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    # team = crud.team.get_by_uuid(db,obj_in.team_uuid)
    # if not team:
    #     raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    team_members = crud.employe.get_by_uuids(db,obj_in.member_uuid_tab)

    if not team_members or len(team_members)!= len(obj_in.member_uuid_tab):
        raise HTTPException(status_code=404, detail=__("members-not-found"))
    
    return crud.team.create(db, obj_in)

@router.post("/", response_model=schemas.EmployeResponse, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TeamUpdate,
    # current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Update a Team
    """

    employe = crud.employe.get_by_uuid(db,obj_in.leader_uuid)

    if  not employe:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    team = crud.team.get_by_uuid(db,obj_in.team_uuid)
    if not team:
        raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    team_members = crud.employe.get_by_uuids(db,obj_in.member_uuid_tab)

    if not team_members or len(team_members)!= len(obj_in.member_uuid_tab):
        raise HTTPException(status_code=404, detail=__("members-not-found"))
    
    return crud.team.update(db, obj_in)

@router.delete("/{uuid}", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    # current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Delete a Team
    """
    teams = crud.team.get_by_uuids(db, uuids)
    if not teams:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    crud.team.soft_delete(db, uuids)
    return {"message": __("team-deleted")}

@router.get("/", response_model=None)
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
    get team with all data by passing filters
    """
    
    return crud.administrator.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        user_uuid,
        # order_filed
        keyword
    )
    