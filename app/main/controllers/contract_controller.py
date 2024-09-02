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


# @router.put("", response_model=schemas.Contract, status_code=200)
# def update_contract(
#     obj_in: schemas.ContractUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
# ):
#     """ Update contract for children """

#     contract = crud.contract.get_contract_by_uuid(db, obj_in.uuid)
#     print("contract-updated",contract)
#     if not contract:
#         raise HTTPException(status_code=404, detail=__("contract-not-found"))

#     childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuid_tab)
#     if not childs or len(childs)!=len(obj_in.child_uuid_tab):
#         raise HTTPException(status_code=404, detail=__("child-not-found"))

#     nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
#     if not nursery:
#         raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
#     employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
#     if not employe:
#         raise HTTPException(status_code=404, detail=__("member-not-found"))

#     return crud.contract.update(db=db, obj_in=obj_in, performed_by_uuid=current_user.uuid)


# @router.delete("", response_model=schemas.Msg)
# def delete_contract(
#     *,
#     db: Session = Depends(get_db),
#     uuids: list[str],
#     current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
# ):
#     """ Delete many(or one) """

#     crud.contract.soft_delete(db=db, uuids=uuids, performed_by_uuid=current_user.uuid)
#     return {"message": __("contract-deleted")}


@router.get("", response_model=schemas.ContractList)
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
    status: str = Query(None, enum=["ACCEPTED", "REFUSED", "CANCELLED", "TERMINATED", "BLOCKED", "RUPTURED"]),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.contract.get_multi(
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

@router.get("/{uuid}", response_model=schemas.Contract, status_code=201)
def get_contract_details(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """ Get contract details """

    contract = crud.contract.get_contract_by_uuid(db, uuid)
    if not contract:
        raise HTTPException(status_code=404, detail=__("contract-not-found"))

    return contract
