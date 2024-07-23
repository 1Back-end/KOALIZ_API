from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/administrators", tags=["administrators"])


@router.post("/create", response_model=schemas.AdministratorResponse, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.AdministratorCreate,
    current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
):
    """
    Create new administrator
    """
    if not current_user.status.lower()=="actived":
        raise HTTPException (status_code=405,detail ="user-not-active")
    
    admin = crud.administrator.get_by_email(db, obj_in.email)
    role = crud.role.get_by_uuid(db, obj_in.role_uuid)
    
    if not role:
        raise HTTPException(status_code=404, detail=__("role-not-found"))
    
    if obj_in.avatar_uuid:
        avatar = db.query(models.Storage).filter(models.Storage.uuid == obj_in.avatar_uuid).first()
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    if admin:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    return crud.administrator.create(db, obj_in,added_by=current_user)

@router.post("/", response_model=schemas.AdministratorResponse, status_code=201)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.AdministratorUpdate,
    current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Update new administrator
    """

    admin = crud.administrator.get_by_uuid(db, obj_in.uuid)
    if not admin:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    email = crud.administrator.get_by_email(db, obj_in.email).email
    print(admin.email,email)

    if email and admin.email != email:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    if obj_in.role_uuid:
        role = crud.role.get_by_uuid(db, obj_in.role_uuid)
        if not role:
            raise HTTPException(status_code=404, detail=__("role-not-found"))
    
    if obj_in.avatar_uuid:
        avatar = db.query(models.Storage).filter(models.Storage.uuid == obj_in.avatar_uuid).first()
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
        
    return crud.administrator.update(db, obj_in)

@router.delete("/{uuid}", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Delete administrator
    """
    if not current_user.status.lower()=="active":
        raise HTTPException (status_code=405,detail ="user-not-active")
    
    admin = crud.administrator.get_by_uuid(db, uuid)
    if not admin:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    crud.administrator.soft_delete(db, uuid)
    return {"message": __("user-deleted")}

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
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    get administrator with all data by passing filters
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
    