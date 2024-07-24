from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.post("/add-memberships-to-nursery",response_model=schemas.Msg, status_code=201)
def create(
    db: Session = Depends(get_db),
    *,
    obj_in:list[schemas.MembershipCreate],
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    errors =[]
    for membership in obj_in:
        exist_nursery = crud.nursery.get_by_uuid(db, membership.nursery_uuid)
        
        exist_membership = db.query(models.Membership).filter_by(uuid = membership.membership_uuid).first()

        if not exist_membership or not exist_nursery:
            errors.append(f"Membership {membership.membership_uuid} or {membership.nursery_uuid} not found")
        
    if len(errors)>0:
        raise HTTPException(status_code=404, detail=f"{errors}")
    
    nursery_existing_memberships = crud.membership.get_by_nursery_uuid(db, [membership.nursery_uuid for membership in obj_in])
    
    tab_period_to = [membership.period_to for membership in obj_in]
    tab_period_from = [membership.period_from for membership in obj_in]

    
    if nursery_existing_memberships:
        for membership in nursery_existing_memberships:
            for new_period_from, new_period_to in zip(tab_period_from, tab_period_to):

                if crud.membership.is_overlapping(membership.period_from, membership.period_to,new_period_from, new_period_to):
                    raise HTTPException(status_code=400, detail=__("overlapping-periods"))

    crud.membership.create(db,obj_in)
    
    return {"message":__("OK")}

@router.put("/update", response_model=schemas.MembershipResponse, status_code=200)
def update(
    obj_in: schemas.MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update membership
    """
    db_membership = crud.membership.get_by_uuid(db, obj_in.uuid)
    
    exist_nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)

    if not db_membership:
        raise HTTPException(status_code=404, detail=__("membership-not-found"))
    
    if not exist_nursery:
        raise HTTPException(status_code=404, detail=__("not-found"))
    
    
    uuids = [obj_in.nursery_uuid]
    nursery_existing_memberships = crud.membership.get_by_nursery_uuid(db, uuids)

    errors =[]

    if nursery_existing_memberships:
        for membership in nursery_existing_memberships:

            if crud.membership.\
                    is_overlapping(membership.period_from, \
                                   membership.period_to,\
                                    obj_in.period_from, obj_in.period_to):                
                raise HTTPException(status_code=400, detail=__("overlapping-periods"))
        
    obj_in.period_from = db_membership.period_from if not obj_in.period_from else obj_in.period_from
    obj_in.period_to = db_membership.period_to if not obj_in.period_to else obj_in.period_to  
    obj_in.period_unit = db_membership.period_unit if not obj_in.period_unit else obj_in.period_unit

    obj_in.period_from = crud.membership.make_offset_aware(obj_in.period_from)
    obj_in.period_to = crud.membership.make_offset_aware(obj_in.period_to)

    if obj_in.period_from > obj_in.period_to:
        raise HTTPException(status_code=400, detail=__("period-to-cannot-be-less-than-period-from"))
    
    

    return crud.membership.update(db, obj_in)

@router.get("/", response_model=schemas.MembershipResponseList, status_code=200)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    status: str = Query(None, enum =["ACTIVED","UNACTIVED"]),
    period_unit:str = Query(None, enum =["DAY","YEAR","MONTH"]),
    period_from:Optional[str] = None,
    period_to: Optional[str] = None,
    duration:Optional[float] = None,
    keyword:Optional[str] = None,
    # membership_type:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    get membership with all data by passing filters
    """
    
    return crud.membership.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        period_unit,
        period_from,
        period_to,
        duration,
        keyword,
        # membership_type
        # order_filed
    )

@router.put("/status")
def change_status(
    uuid: str,
    db: Session = Depends(get_db),
    status:str = Query(None, enum =["ACTIVED","UNACTIVED","PENDING","SUSPENDED"]),
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator,owner"] ))
):
    """
    Change membership status
    """
    membership = crud.membership.get_by_uuid(db, uuid)
    if not membership:
        raise HTTPException(status_code=404, detail=__("membership-not-found"))

    return crud.membership.update_status(db, uuid, status)





    



