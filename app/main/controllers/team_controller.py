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
    obj_in:list[schemas.TeamCreate],
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create new Team
    """
    employe_errors = []
    member_errors =[]
    nursery_owner_errors =[]
    for team in obj_in:
        employe = crud.employe.get_by_uuid(db,team.leader_uuid)

        if  not employe:
            employe_errors.append(team.leader_uuid)

        for member_uuid in team.member_uuid_tab:
            member = crud.employe.get_by_uuid(db,member_uuid)
            if not member:
                member_errors.append(member_uuid)
            
            for nursery in member.nurseries:
                if not nursery:
                    print(nursery.uuid)
                    nursery_owner_errors.append(nursery.uuid)
    
    status_code = 404 if employe_errors or member_errors else 400 
    key_errors = "member-not-found" if employe_errors  or member_errors else "nursery-owner-not-authorized" 

    errors = employe_errors if employe_errors else member_errors if member_errors else nursery_owner_errors if nursery_owner_errors else []
    if len(errors):
        raise HTTPException(status_code=status_code, detail=__(f"{key_errors}") +' '.join(errors))    
    
    # team_members = crud.employe.get_by_uuids(db,obj_in.member_uuid_tab)

    # if not team_members or len(team_members)!= len(obj_in.member_uuid_tab):
    #     raise HTTPException(status_code=404, detail=__("members-not-found"))
    
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

    employe_errors = []
    member_errors =[]
    nursery_owner_errors =[]
    team_error = []
    
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
    
    return crud.team.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        user_uuid,
        # order_filed
        keyword
    )
    