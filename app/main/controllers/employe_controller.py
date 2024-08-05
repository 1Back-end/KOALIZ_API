from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional,List

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/create", response_model=list[schemas.EmployeResponse], status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:list[schemas.EmployeCreate],
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create new member
    """
    exist_email = []
    email_errors = []
    avatar_errors = []
    nursery_errors = []
    team_errors = []
    nursery_owner_errors = []
    
    for employe in obj_in:
        if employe.email in exist_email:
            exist_email.append(employe.email)
        else:
            user = crud.employe.get_by_email(db,employe.email)
            if user:
                email_errors.append(employe.email)

        if employe.avatar_uuid:
            avatar = db.query(models.Storage).filter(models.Storage.uuid == employe.avatar_uuid).first()
            if not avatar:
                avatar_errors.append(employe.avatar_uuid)

        if employe.nursery_uuid_tab:
            for nursery_uuid in employe.nursery_uuid_tab:      
                nursery = crud.nursery.get_by_uuid(db, nursery_uuid)
                if not nursery:
                    nursery_errors.append(nursery_uuid)
                
                if not nursery_uuid in [current_nursery.uuid for current_nursery in current_user.nurseries]:
                    nursery_owner_errors.append(nursery_uuid)
                
        for team_uuid in employe.team_uuid_tab:
            team = crud.team.get_by_uuid(db, team_uuid)
            if not team:
                team_errors.append(team_uuid)
        
    errors = team_errors if team_errors else email_errors if email_errors else nursery_errors if nursery_errors else exist_email if exist_email else nursery_owner_errors      
    status_code = 404 if team_errors or nursery_errors or email_errors or avatar_errors else 409 if exist_email else 400
    key_errors = "team-not-found" if team_errors \
        else "avatar-not-found" if avatar_errors \
            else "nursery-not-found" if nursery_errors else "duplicate-entry-email" \
                if email_errors else "user-email-taken" if exist_email else "nursery-owner-not-authorized"
    
    if errors:
        raise HTTPException(status_code=status_code, detail=f"{__(key_errors)}:" + ' '+'' .join(errors))

    # db_obj = crud.employe.get_by_email(db, obj_in.email)
    
    
    # if db_obj:
    #     raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    # nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    # if not nursery:
    #     raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    # if obj_in.team_uuid_tab:
    #     teams = crud.team.get_by_uuids(db, obj_in.team_uuid_tab)
    #     if not teams or len(teams)!= len(obj_in.team_uuid_tab):
    #         raise HTTPException(status_code=404, detail=__("team-not-found"))
    
    return crud.employe.create(db, obj_in)

@router.put("/", response_model=schemas.EmployeResponse, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.EmployeUpdate,
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Update a member
    """

    nursery_errors =[]
    nursery_owner_errors =[]
    team_errors =[]
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
    
    # nurseries = crud.nursery.get_by_uuids(db, obj_in.nursery_uuid_tab)
    # if not nurseries or len(nurseries)!=len(nurseries)  :
    #     raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    for nursery_uuid in obj_in.nursery_uuid_tab:      
        nursery = crud.nursery.get_by_uuid(db, nursery_uuid)
        if not nursery:
            nursery_errors.append(nursery_uuid)
        
        if not nursery_uuid in [current_nursery.uuid for current_nursery in current_user.nurseries]:
            nursery_owner_errors.append(nursery_uuid)
    errors = nursery_errors if nursery_errors else nursery_owner_errors if nursery_owner_errors else []

    if obj_in.team_uuid_tab:
        for team_uuid in obj_in.team_uuid_tab:
            team = crud.team.get_by_uuid(db, team_uuid)
            if not team:
                team_errors.append(team_uuid)

    status_code = 404 if nursery_errors or team_errors else 400 
    key_errors = "nursery-not-found" if nursery_errors else \
        "team-not-found" if team_errors \
            else "nursery-owner-not-authorized" 
    
    if errors:
        raise HTTPException(status_code=status_code, detail=__(f"{key_errors}") +' '.join(errors))
    
    return crud.employe.update(db, obj_in)

@router.delete("/{uuid}", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    obj_in: list[schemas.EmployeDelete],
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a member
    """
    team_errors = []
    nursery_errors =[]
    employe_errors = []
    nursery_owner_errors =[]
    employees = crud.employe.get_by_uuids(db, [i.uuid for i in obj_in])
        
    if not employees:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    for obj in obj_in:
        employe = crud.employe.get_by_uuid(db, obj.uuid)
        if not employe:
            employe_errors.append(obj.uuid)
    
        if obj.nursery_uuid_tab:
            for nursery_uuid in obj.nursery_uuid_tab:      
                nursery = crud.nursery.get_by_uuid(db, nursery_uuid)
                if not nursery:
                    nursery_errors.append(nursery_uuid)
                if not nursery_uuid in any(nursery.uuid == current_nursery.uuid for current_nursery in current_user.nurseries):
                    nursery_owner_errors.append(nursery_uuid)

            if nursery_owner_errors:
                raise HTTPException(status_code=400, detail=__(f"nursery-owner-not-authorized") + ' '.join(nursery_owner_errors))
            
        if obj.team_uuid_tab:
            for team_uuid in obj.team_uuid_tab:
                team = crud.team.get_by_uuid(db, team_uuid)
                if not team:
                    team_errors.append(team_uuid)

    crud.employe.soft_delete(db, obj_in)

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
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
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
    