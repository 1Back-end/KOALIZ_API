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
    # team_name_errors = []
    # team_name_entry_errors = []
    # team_name_tab = []
    for team in obj_in:
        owner_uuid_tab =[]
        employe = crud.employe.get_by_uuid(db,team.leader_uuid)
        print("leader: %s" % employe)
        if  not employe:
            employe_errors.append(team.leader_uuid)
        else:
            owner_uuid_tab.append(employe.nurseries[0].owner_uuid)

        # exist_team = crud.team.get_by_name(db,team.name)
        # print("team: %s" % exist_team)
        # if exist_team:
        #     team_name_errors.append(team.name)

        # if team.name not in team_name_tab:
        #     team_name_tab.append(team.name)
        # else:
        #     team_name_entry_errors.append(team.name)

        for member_uuid in team.member_uuid_tab:
            member = crud.employe.get_by_uuid(db,member_uuid)
            print("member_uuid: %s" % member)
            if not member:
                member_errors.append(member_uuid)
            else:
                owner_uuid_tab +=[i.owner_uuid for i in member.nurseries]

                for owner_uuid in owner_uuid_tab:      
                    if owner_uuid!=current_user.uuid:
                        nursery_owner_errors.append(f'owner:{owner_uuid}-member:{member_uuid}')
        
    status_code = 404 if employe_errors or  member_errors else 400 
    key_errors = "member-not-found" if member_errors  \
        else "leader-not-found" if employe_errors \
            else "nursery-owner-not-authorized" 

    errors = employe_errors if employe_errors \
        else member_errors if member_errors \
                else nursery_owner_errors
    if len(errors):
        raise HTTPException(status_code=status_code, detail=f"{__(key_errors)}:" + ' '+'' .join(errors))    
    
    # team_members = crud.employe.get_by_uuids(db,obj_in.member_uuid_tab)

    # if not team_members or len(team_members)!= len(obj_in.member_uuid_tab):
    #     raise HTTPException(status_code=404, detail=__("members-not-found"))
    
    return crud.team.create(db, obj_in,current_user.uuid)

@router.post("/", response_model=schemas.TeamResponse, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TeamUpdate,
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Update a Team
    """

    employe_errors = []
    member_errors =[]
    nursery_owner_errors =[]
    # team_name_errors = []
    # team_name_entry_errors = []
    # team_name_tab = []

    owner_uuid_tab =[]
    employe = crud.employe.get_by_uuid(db,obj_in.leader_uuid)
    print("leader: %s" % employe)
    if  not employe:
        employe_errors.append(obj_in.leader_uuid)
    else:
        owner_uuid_tab.append(employe.nurseries[0].owner_uuid)

    team = crud.team.get_by_uuid(db,obj_in.uuid)
    if not team:
        raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    # exist_team = crud.team.get_by_name(db,obj_in.name)
    # print("team: %s" % exist_team)
    # if exist_team:
    #     team_name_errors.append(obj_in.name)

    # if obj_in.name not in team_name_tab:
    #     team_name_tab.append(obj_in.name)
    # else:
    #     team_name_entry_errors.append(obj_in.name)

    for member_uuid in obj_in.member_uuid_tab:
        member = crud.employe.get_by_uuid(db,member_uuid)
        print("member_uuid: %s" % member)
        if not member:
            member_errors.append(member_uuid)
        else:
            owner_uuid_tab +=[i.owner_uuid for i in member.nurseries]

            for owner_uuid in owner_uuid_tab:      
                if owner_uuid!=current_user.uuid:
                    nursery_owner_errors.append(f'owner:{owner_uuid}-member:{member_uuid}')
    # employe = crud.employe.get_by_uuid(db,obj_in.leader_uuid)

    # if  not employe:
    #     raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    # team = crud.team.get_by_uuid(db,obj_in.team_uuid)
    # if not team:
    #     raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    # team_members = crud.employe.get_by_uuids(db,obj_in.member_uuid_tab)

    # if not team_members or len(team_members)!= len(obj_in.member_uuid_tab):
    #     raise HTTPException(status_code=404, detail=__("members-not-found"))

    status_code = 404 if employe_errors or  member_errors else 400 
    key_errors = "member-not-found" if member_errors  \
        else "leader-not-found" if employe_errors \
            else "nursery-owner-not-authorized" 

    errors = employe_errors if employe_errors \
        else member_errors if member_errors \
                else nursery_owner_errors
    if len(errors):
        raise HTTPException(status_code=status_code, detail=f"{__(key_errors)}:" + ' '+'' .join(errors)) 
    
    return crud.team.update(db, obj_in)

@router.delete("/{uuid}", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a Team
    """
    team_errors =[]
    teams = crud.team.get_by_uuids(db, uuids)
    if not teams or len(teams)!=len(uuids):
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    for team in teams:
        if team.owner_uuid!= current_user.uuid:
            team_errors.append(team.uuid)

    if team_errors:
        raise HTTPException(status_code=400, detail=f"{__("team-owner-unauthorized")}:" + ' '+'' .join(team_errors))
    
    crud.team.soft_delete(db, uuids)
    return {"message": __("team-deleted")}

@router.get("/", response_model=schemas.TeamResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    user_uuid:Optional[str] = None,
    status: str = Query(None, enum =["ACTIVED","DELETED"]),
    keyword:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
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
    