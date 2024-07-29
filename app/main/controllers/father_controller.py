from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/fathers", tags=["fathers"])



@router.post("",response_model =schemas.Father ,status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.FatherCreate,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))

):
    """
    Create father for  owners
    """
    if obj_in.avatar_uuid:
        avatar = crud.storage.get(db,obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
        
    father = crud.father.get_by_email(db, obj_in.email)
    if father:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))
    
    role = crud.role.get_by_uuid(db, obj_in.role_uuid)
    if not role:
        raise HTTPException(status_code=404, detail=__("role-not-found"))
    
    # if not crud.father.password_confirmation(db, obj_in.password, obj_in.confirm_password):
    #     raise HTTPException(status_code=400, detail=__("passwords-not-match"))
    
    return crud.father.create(db, obj_in)

@router.put("", response_model=schemas.Father, status_code=200)
def update(
    obj_in: schemas.FatherUpdate,
    db: Session = Depends(get_db),
    current_user: models.Father = Depends(TokenRequired(roles =["parent"] ))
):
    """
    Update father
    """
    user = crud.father.get_by_uuid(db, obj_in.uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
    
    if obj_in.email and obj_in.email != user.email:
        if crud.father.get_by_email(db, obj_in.email):
            raise HTTPException(status_code=409, detail=__("user-email-taken"))

    return crud.father.update(db ,obj_in)


@router.put("/status", response_model=schemas.Father, status_code=201)
def update(
    *,
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Father = Depends(TokenRequired(roles=["parent"]))
):
    """
    Update father status
    """
    user = crud.father.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.status == status:
        return user

    return crud.father.update_status(db,user,status)


@router.get("/{uuid}", response_model=schemas.Father, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Father = Depends(TokenRequired(roles=["parent"]))
):
    """
    Get father details
    """
    user = crud.father.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return user


@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Father = Depends(TokenRequired(roles =["parent"]))
):
    """
    Delete many(or one)
    """
    crud.father.delete(db, uuids)
    return {"message": __("user-deleted")}


@router.get("", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    status:Optional[str] = None,
    parent_uuid: Optional[str] = None,
    keyword: Optional[str] = None,
    # current_user: models.Father = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.father.get_multi(
        db,
        page,
        per_page,
        order,
        status,
        parent_uuid,
        order_filed,
        keyword
    )
