from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/owners", tags=["owners"])



@router.post("/parent-pickup-child-authorization-for-nursery", response_model=schemas.ChildMini, status_code=201)
def give_parent_pickup_child_authorization_for_nursery(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildrenConfirmation = Body(...),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ give parent permission to pickup child from nursery """

    parent = crud.parent.get_by_email(db, obj_in.parent_email)
    if not parent:
        raise HTTPException(status_code=404, detail=__("parent-not-found"))
    
    if parent.status in [st.value for st in models.UserStatusType if st.value == models.UserStatusType.DELETED or st.value == models.UserStatusType.BLOCKED]:
        raise HTTPException(status_code=403, detail=__("parent-status-not-allowed"))
    
    if not obj_in.nursery_uuid  in [current_nursery.uuid for current_nursery in current_user.nurseries]:
        raise HTTPException(status_code = 400,detail = __("nursery-owner-not-authorized"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    accepted_preregistration = next((pr for pr in child.preregistrations if pr.nursery_uuid == obj_in.nursery_uuid and pr.status == models.PreRegistrationStatusType.ACCEPTED), None) 
    
    if not accepted_preregistration:
        raise HTTPException(status_code=404, detail=__("child-not-registered-in-nursery"))
    
    crud.owner.give_parent_pickup_child_authorization_for_nursery(db=db, obj_in=obj_in, added_by=current_user)

    return child

@router.post("/apps-authorization", response_model=schemas.ChildMini, status_code=201)
def confirm_apps_authorization(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildrenConfirmation = Body(...),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner", "administrator"]))
):
    """ Confirm apps authorization """

    parent = crud.parent.get_by_email(db, obj_in.parent_email)
    if not parent:
        parent = db.query(models.ParentGuest).filter(models.ParentGuest.email == obj_in.parent_email).first()
        if not parent:
            raise HTTPException(status_code=404, detail=__("parent-not-found"))
    
    if parent.status in ["DELETED", "BLOCKED"]:
        raise HTTPException(status_code=403, detail=__("parent-status-not-allowed"))
    
    # if not obj_in.nursery_uuid  in [current_nursery.uuid for current_nursery in current_user.nurseries]:
    #     raise HTTPException(status_code = 400,detail = __("nursery-owner-not-authorized"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    accepted_preregistration = next((pr for pr in child.preregistrations if pr.nursery_uuid == obj_in.nursery_uuid and pr.status == models.PreRegistrationStatusType.ACCEPTED), None) 
    
    if not accepted_preregistration:
        raise HTTPException(status_code=404, detail=__("child-not-registered-in-nursery"))
    
    crud.owner.confirm_apps_authorization(db=db, obj_in=obj_in, added_by=current_user, preregistration = accepted_preregistration)

    return child

@router.post("/create", response_model=schemas.Owner, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.OwnerCreate,
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester"]))
):
    """
    Create owner
    """
    user = crud.owner.get_by_email(db, obj_in.email)
    if user:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))

    if obj_in.avatar_uuid:
        avatar = crud.storage.get(db=db, uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    return crud.owner.create(db, obj_in, current_user.uuid)

@router.put("/{uuid}", response_model=schemas.Owner, status_code=201)
def update(
    uuid: str,
    obj_in: schemas.OwnerUpdateBase,
    db: Session = Depends(get_db),
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester"]))
):
    """
    Update nursery owner
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
        
    return crud.owner.update(db, user, obj_in)


@router.put("/{uuid}/status", response_model=schemas.Owner, status_code=201)
def update(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester"]))
):
    """
    Update nursery owner status
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.status == status:
        return user

    return crud.owner.update(db, user, {"status": status})


@router.get("/{uuid}", response_model=schemas.Owner, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester", "accountant"]))
):
    """
    Get nursery owner details
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return user


@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester"]))
):
    """
    Delete many(or one)
    """
    crud.owner.delete(db, uuids)
    return {"message": __("user-deleted")}


@router.get("/", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester", "accountant"]))
):
    """
    get all with filters
    """
    
    return crud.owner.get_multi(
        db, 
        page, 
        per_page, 
        order, 
        order_filed,
        keyword
    )
