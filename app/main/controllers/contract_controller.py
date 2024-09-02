from sqlalchemy import or_
from app.main.core.dependencies import TokenRequired, get_db
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/contracts", tags=["contracts"])

# @router.post("",response_model =schemas.Contract ,status_code=201)
# def create_contract(
#     *,
#     db: Session = Depends(get_db),
#     obj_in: schemas.ContractCreate,
#     current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))

# ):
#     """ Create contract for children """

#     nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
#     if not nursery:
#         raise HTTPException(status_code=404, detail=__("nursery-not-found"))

#     child = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuid_tab)
#     if not child or len(child)!=len(obj_in.child_uuid_tab):
#         raise HTTPException(status_code=404, detail=__("child-not-found"))

#     employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
#     if not employe:
#         raise HTTPException(status_code=404, detail=__("member-not-found"))

#     return crud.contract.create(db=db, obj_in=obj_in, performed_by_uuid=current_user.uuid)


@router.put("", response_model=schemas.Contract, status_code=200)
def update_contract(
    obj_in: schemas.ContractUpdate,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """ Update contract for children """

    contract = crud.contract.get_contract_by_uuid(db, obj_in.uuid)
    print("contract-updated",contract)
    if not contract:
        raise HTTPException(status_code=404, detail=__("contract-not-found"))

    return crud.contract.update(db=db, obj_in=obj_in, performed_by_uuid=current_user.uuid)

@router.put("/client-account", response_model=schemas.Contract, status_code=200)
def update_client_account(
    obj_in: schemas.ClientAccountContractUpdate,
    db: Session = Depends(get_db),
    current_user: models.Parent = Depends(TokenRequired(roles=["owner"] ))
):
    """
    Update client account
    """

    contract = crud.contract.get_contract_by_uuid(db, obj_in.uuid)
    print("contract-updated",contract)
    if not contract:
        raise HTTPException(status_code=404, detail=__("contract-not-found"))

    client_account = crud.contract.get_client_account_by_uuid(db, obj_in.uuid)
    if not client_account:
        raise HTTPException(status_code=404, detail=__("client-account-not-found"))

    crud.contract.update_client_account(db=db, obj_in=obj_in, performed_by_uuid=current_user.uuid)

    return contract


@router.put("/extend", response_model=schemas.Contract, status_code=200)
def extend_the_contract(
    obj_in: schemas.ProlongeContract,
    db: Session = Depends(get_db),
    current_user: models.Parent = Depends(TokenRequired(roles=["owner"]))
):
    """
        Extend the contract
    """

    contract = crud.contract.get_contract_by_uuid(db, obj_in.uuid)
    print("contract-updated",contract)
    if not contract:
        raise HTTPException(status_code=404, detail=__("contract-not-found"))
    
    child = db.query(models.Child).filter(models.Child.uuid == obj_in.child_uuid).first()
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    if obj_in.end_date <= contract.begin_date:
        raise HTTPException(status_code=404, detail="End date must be after to begin date.")

    crud.contract.extend_the_contract(db=db, obj_in=obj_in, performed_by_uuid=current_user.uuid)

    return contract

# @router.put("/publish/{contract_uuid}", response_model=schemas.Contract, status_code=200)
# def publish_the_contract(
#     contract_uuid: str,
#     db: Session = Depends(get_db),
#     current_user: models.Parent = Depends(TokenRequired(roles=["owner"]))
# ):
#     """
#         Publish the contract
#     """

#     exist_contract = crud.contract.get_contract_by_uuid(db, contract_uuid)
#     print("contract-updated",contract)
#     if not exist_contract:
#         raise HTTPException(status_code=404, detail=__("contract-not-found"))
    

#     contract = crud.contract.publish_the_contract(db=db, contract_uuid=contract_uuid, performed_by_uuid=current_user.uuid)

#     return contract


@router.delete("", response_model=schemas.Msg)
def delete_contract(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """ Delete many(or one) """

    crud.contract.soft_delete(db=db, uuids=uuids, performed_by_uuid=current_user.uuid)
    return {"message": __("contract-deleted")}


@router.get("", response_model=schemas.ContractSlimList)
def get_contracts(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_field: str = "date_added",
    tag_uuid: Optional[str] = None,
    nursery_uuid: str,
    child_uuid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: str = Query(None, enum=["ACCEPTED", "TERMINATED", "RUPTURED"]),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    query = crud.contract.get_multi(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        tag_uuid=tag_uuid,
        nursery_uuid=nursery_uuid,
        child_uuid=child_uuid,
        order_field=order_field,
        keyword=keyword,
        status=status,
        # owner_uuid=current_user.uuid
    )

    for r in query.data:
        for parent in r.parents:
            exist_parent = db.query(models.ParentGuest).\
                filter(models.ParentGuest.uuid == parent.uuid).\
                filter(or_(models.ParentGuest.status != "DELETED", models.ParentGuest.status.is_(None))).\
                first()
            if not exist_parent:
                raise HTTPException(status_code=404, detail=__("parent-not-found"))
                        
            parent_child = db.query(models.ParentChild).\
                filter(models.ParentChild.parent_uuid == exist_parent.uuid).\
                    first()
            pickup_parent = db.query(models.PickUpParentChild).\
                filter(models.PickUpParentChild.parent_uuid == exist_parent.uuid).\
                    first()
            
            # Update the boolean flags based on the query results
            has_pickup_child_authorization = bool(pickup_parent)
            has_app_authorization = bool(parent_child)

            # Update the parent object in the parents list
            parent.has_pickup_child_authorization = has_pickup_child_authorization
            parent.has_app_authorization = has_app_authorization

    return query

@router.get("/{uuid}", response_model=schemas.Contract, status_code=201)
def get_contract_details(
    uuid: str,
    db: Session = Depends(get_db),
    # current_user: models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """ Get contract details """

    contract = crud.contract.get_contract_by_uuid(db, uuid)
    if not contract:
        raise HTTPException(status_code=404, detail=__("contract-not-found"))

    return contract
