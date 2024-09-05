from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/owners", tags=["owners"])


def determine_parent_has_app_authorization(db: Session, parent: models.ParentGuest, nursery_uuid: str, child_uuid: str):
    return bool(db.query(models.ParentChild).filter(
        models.ParentChild.parent_email == parent.email,
        models.ParentChild.child_uuid == child_uuid,
        models.ParentChild.nursery_uuid == nursery_uuid,
    ).first())


@router.post("/parent-pickup-child-authorization-for-nursery", response_model=schemas.ParentContractSchema, status_code=201)
def give_parent_pickup_child_authorization_for_nursery(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildPickUp,
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Toggle parent permission to pickup child from nursery """

    parent_guest = crud.parent.get_parent_guest_by_uuid(db, obj_in.parent_guest_uuid)
    if not parent_guest:
        raise HTTPException(status_code=404, detail=__("parent-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if obj_in.nursery_uuid not in [current_nursery.uuid for current_nursery in current_user.valid_nurseries]:
        raise HTTPException(status_code=400, detail=__("nursery-owner-not-authorized"))

    accepted_preregistration = next((pr for pr in parent_guest.child.preregistrations if pr.nursery_uuid == obj_in.nursery_uuid and pr.status  == models.PreRegistrationStatusType.ACCEPTED), None)

    if not accepted_preregistration:
        raise HTTPException(status_code=404, detail=__("child-not-registered-in-nursery"))

    crud.owner.give_parent_pickup_child_authorization_for_nursery(db=db, parent_guest=parent_guest)

    db.refresh(parent_guest)
    parent_guest.has_app_authorization = determine_parent_has_app_authorization(db, parent_guest, obj_in.nursery_uuid, parent_guest.child_uuid)
    return parent_guest


@router.post("/apps-authorization", response_model=list[schemas.ParentContractSchema], status_code=201)
def confirm_apps_authorization(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildrenConfirmation = Body(...),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner", "administrator"]))
):
    """ Confirm apps authorization """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if obj_in.nursery_uuid not in [current_nursery.uuid for current_nursery in current_user.valid_nurseries]:
        raise HTTPException(status_code=400,detail=__("nursery-owner-not-authorized"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    accepted_preregistration = next((pr for pr in child.preregistrations if pr.nursery_uuid == obj_in.nursery_uuid and pr.status == models.PreRegistrationStatusType.ACCEPTED), None)

    if not accepted_preregistration:
        raise HTTPException(status_code=404, detail=__("child-not-registered-in-nursery"))

    crud.owner.confirm_apps_authorization(db=db, obj_in=obj_in, added_by=current_user)

    for parent in child.parents:
        parent.has_app_authorization = determine_parent_has_app_authorization(db, parent, obj_in.nursery_uuid, obj_in.child_uuid)

    return child.parents


@router.put("/parent", response_model=schemas.Parent, status_code=200)
def update_paren_informations(
    obj_in: schemas.ParentUpdate,
    db: Session = Depends(get_db),
    current_user: models.Parent = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Update parent informations
    """
    user = crud.parent.get_parent_guest_by_uuid(db, obj_in.uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    # if obj_in.email and obj_in.email != user.email:
    #     if crud.parent.get_by_email(db, obj_in.email):
    #         raise HTTPException(status_code=409, detail=__("user-email-taken"))

    return crud.parent.update_parent_guest(db ,obj_in)


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


@router.get("/assistants", response_model=schemas.AssistantList)
def get(
    *,
    db: Session = Depends(get_db),
    nurser_uuid: str,
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
    current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    get all with filters
    """
    return crud.owner.get_multi(
        db=db, page=page, per_page=per_page, order=order, order_filed=order_filed,
        keyword=keyword, nurser_uuid=nurser_uuid, role_code="assistant", owner_uuid=current_user.uuid
    )


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


@router.post("/assistants/create", response_model=schemas.Assistant, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.AssistantCreate,
    current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Create assistant
    """
    print(current_user.uuid)
    user = crud.owner.get_by_email(db, obj_in.email)
    if user:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))

    if obj_in.nursery_uuids:
        obj_in.nursery_uuids = list(set(obj_in.nursery_uuids))

        nurseries: list[models.Nursery] = crud.nursery.get_by_uuids(db, obj_in.nursery_uuids, current_user.uuid)
        if len(nurseries) != len(obj_in.nursery_uuids):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if obj_in.avatar_uuid:
        avatar = crud.storage.get(db=db, uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    return crud.owner.create_assistant(db, obj_in, current_user.uuid)


@router.put("/assistants/{uuid}", response_model=schemas.Assistant, status_code=201)
def update(
    uuid: str,
    obj_in: schemas.AssistantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Update assistant
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.role.code != "assistant":
        raise HTTPException(status_code=403, detail=__("user-not-assistant"))

    if not any([nursery.owner_uuid == current_user.uuid for nursery in user.structures]):
        raise HTTPException(status_code=403, detail=__("nursery-owner-not-authorized"))

    if obj_in.nursery_uuids:
        obj_in.nursery_uuids = list(set(obj_in.nursery_uuids))

        nurseries = crud.nursery.get_by_uuids(db, obj_in.nursery_uuids, current_user.uuid)
        if len(nurseries) != len(obj_in.nursery_uuids):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    return crud.owner.update(db, user, obj_in)


@router.put("/assistants/{uuid}/status", response_model=schemas.Assistant, status_code=201)
def update_status(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update assistant status
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.role.code != "assistant":
        raise HTTPException(status_code=403, detail=__("user-not-assistant"))

    if user.status == status:
        return user

    return crud.owner.update(db, user, {"status": status})


@router.get("/assistants/{uuid}", response_model=schemas.Assistant, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Get assistant details
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.role.code != "assistant":
        raise HTTPException(status_code=403, detail=__("user-not-assistant"))

    if not any([nursery.owner_uuid == current_user.uuid for nursery in user.structures]):
        raise HTTPException(status_code=403, detail=__("nursery-owner-not-authorized"))

    return user


@router.delete("/assistants", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    nursery_uuid: str,
    uuids: list[str],
    current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Delete many(or one)
    """
    nursery = crud.nursery.get_by_uuid(db, nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=403, detail=__("nursery-owner-not-authorized"))

    crud.owner.delete_assistants(db, uuids, current_user.uuid, nursery_uuid)
    return {"message": __("user-deleted")}
