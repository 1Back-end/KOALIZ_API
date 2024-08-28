import uuid
from datetime import date, datetime, timedelta
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main.core.mail import send_account_confirmation_email
from app.main.core.security import generate_code


router = APIRouter(prefix="/parents", tags=["parents"])


@router.get("/children-transmissions", response_model=list[schemas.ParentTransmission], status_code=200)
def get_children_transmissions(
    nursery_uuid: Optional[str] = None,
    child_uuid: Optional[str] = None,
    date: date = None,
    db: Session = Depends(get_db),
    current_parent: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """ Get children transmissions """


    return crud.parent.get_children_transmissions(
        db=db, 
        current_parent=current_parent, 
        filter_date=date,
        nursery_uuid=nursery_uuid,
        child_uuid= child_uuid
    )


@router.get("/children", response_model=schemas.ChildDetailsList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    filter_date:date = None,
    contrat_uuid: Optional[str] = None,
    nursery_uuid:Optional[str] = None,
    child_uuid : Optional[str] = None,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
    current_user: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """
    get children with filters
    """
    return crud.parent.get_children(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        order_filed=order_filed,
        keyword=keyword,
        nursery_uuid = nursery_uuid,
        child_uuid = child_uuid,
        contrat_uuid = contrat_uuid,
        filter_date=filter_date,
        parent_uuid=current_user.uuid
    )

@router.get("/media", response_model=schemas.MediaList)
def get(
    *,
    nursery_uuid:Optional[str] = None,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    filter_date:date = None,
    order_filed: str = "date_added",
    media_type: str = Query(None, enum=[st.value for st in models.MediaType]),
    keyword: Optional[str] = None,
    current_user: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """
    get children media with filters
    """
    return crud.parent.get_children_media(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        order_filed=order_filed,
        keyword=keyword,
        parent_uuid=current_user.uuid,
        media_type=media_type,
        filter_date=filter_date,
        nursery_uuid = nursery_uuid
    )

@router.get("/invoices", response_model=schemas.InvoiceList)
def get(*,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("asc", enum=["asc", "desc"]),
        order_filed: str = "date_to",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.InvoiceStatusType]),
        month: Optional[int] = None,
        year: Optional[int] = None,
        reference: Optional[str] = None,
        contract_uuid: Optional[str] = None,
        nursery_uuid :Optional[str] = None,
        child_uuid: Optional[str] = None,
        current_user: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """
    get invoices with filters
    """
    return crud.parent.get_invoices(
        db=db, 
        page=page, 
        per_page=per_page, 
        order=order,
        order_filed=order_filed, 
        keyword=keyword, 
        status=status, 
        reference=reference, 
        month=month, 
        year=year,
        contract_uuid = contract_uuid,
        child_uuid=child_uuid,
        nursery_uuid=nursery_uuid,
        parent_uuid=current_user.uuid
    )


@router.post("",response_model =schemas.Parent ,status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ParentCreate,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))

):
    """
    Create parent for  owners
    """
    if obj_in.avatar_uuid:
        avatar = crud.storage.get(db,obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
        
    parent = crud.parent.get_by_email(db, obj_in.email)
    
    code = generate_code(length=12)
    code= str(code[0:6])
    
    if parent:
        if crud.parent.is_active(parent):
            raise HTTPException(status_code=400, detail=__("user-email-taken"))
        
        user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.user_uuid == parent.uuid)

        if user_code.count()>0:
            user_code.delete()

        print("user_code1:")
        db_code = models.ParentActionValidation(
            uuid=str(uuid.uuid4()),
            code=code,
            user_uuid=parent.uuid,
            value=code,
            expired_date=datetime.now() + timedelta(minutes=30)
        )

        db.add(db_code)
        db.commit()
        send_account_confirmation_email(email_to=obj_in.email, name=(obj_in.firstname+obj_in.lastname),token=code,valid_minutes=30)

    return parent

@router.put("", response_model=schemas.Parent, status_code=200)
def update(
    obj_in: schemas.ParentUpdate,
    db: Session = Depends(get_db),
    current_user: models.Parent = Depends(TokenRequired(roles =["parent"] ))
):
    """
    Update parent
    """
    user = crud.parent.get_by_uuid(db, obj_in.uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
    
    if obj_in.email and obj_in.email != user.email:
        if crud.parent.get_by_email(db, obj_in.email):
            raise HTTPException(status_code=409, detail=__("user-email-taken"))

    return crud.parent.update(db ,obj_in)


@router.put("/status", response_model=schemas.Parent, status_code=201)
def update(
    *,
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """
    Update parent status
    """
    user = crud.parent.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.status == status:
        return user

    return crud.parent.update_status(db,user,status)


@router.get("/{uuid}", response_model=schemas.Parent, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Parent = Depends(TokenRequired(roles=["parent"]))
):
    """
    Get parent details
    """
    user = crud.parent.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return user


@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Parent = Depends(TokenRequired(roles =["parent"]))
):
    """
    Delete many(or one)
    """
    crud.parent.delete(db, uuids)
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
    current_user: models.Parent = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.parent.get_multi(
        db,
        page,
        per_page,
        order,
        status,
        parent_uuid,
        order_filed,
        keyword
    )
