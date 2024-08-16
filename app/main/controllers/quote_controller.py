from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main import schemas, crud, models
from app.main.core.dependencies import get_db, TokenRequired
from app.main.core.i18n import __


router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/", response_model=schemas.QuoteList)
def get(
        nursery_uuid: str,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_added",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.NurseryStatusType]),
        tag_uuid: Optional[str] = None,
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.quote.get_many(
        db,
        nursery_uuid,
        current_user.uuid,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status,
        tag_uuid
    )


@router.get("/cmg-amount-range", response_model=list[schemas.CMGAmountRange], status_code=200)
def list_cmg_amount_range(
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Get quote cmg range
    """

    return crud.quote.get_cmg_range(db)


@router.put("/cmg-amount-range/{cmg_amount_range_uuid}", response_model=schemas.CMGAmountRange, status_code=200)
def update_cmg_amount_range(
        cmg_amount_range_uuid: str,
        obj_in: schemas.CMGAmountRangeUpdate,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update quote cmg amount range
    """
    # check if cmg amount range exists
    cmg_amount_range = crud.quote.get_cmg_range_by_uuid(db, cmg_amount_range_uuid)
    if not cmg_amount_range:
        raise HTTPException(status_code=404, detail=__("cmg-amount-range-not-found"))

    return crud.quote.update_cmg_amount_range(db, cmg_amount_range, obj_in)


@router.get("/cmg-amount", response_model=list[schemas.CMGAmount], status_code=200)
def list_cmg_amount(
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Get quote cmg amount
    """

    return crud.quote.get_cmg(db)


@router.put("/cmg-amount/{cmg_amount_uuid}", response_model=schemas.CMGAmount, status_code=200)
def update_cmg_amount(
        cmg_amount_uuid: str,
        obj_in: schemas.CMGAmountUpdate,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update quote cmg amount
    """
    # check if cmg amount exists
    cmg_amount = crud.quote.get_cmg_amount_by_uuid(db, cmg_amount_uuid)
    if not cmg_amount:
        raise HTTPException(status_code=404, detail=__("cmg-amount-not-found"))

    return crud.quote.update_cmg_amount(db, cmg_amount, obj_in)



@router.get("/{uuid}", response_model=schemas.QuoteDetails, status_code=200)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
        Get quote details
    """
    quote = crud.quote.get_by_uuid(db, uuid)
    if not quote:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    if current_user.role.code == "owner" and quote.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    return quote


@router.put("/{uuid}/settings", response_model=schemas.Msg, status_code=200)
def update_settings(
        uuid: str,
        obj_in: schemas.QuoteSettingsUpdate,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update quote settings
    """
    quote = crud.quote.get_by_uuid(db, uuid)
    if not quote:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    if quote.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    crud.quote.update_settings(db, quote, obj_in)
    return schemas.Msg(message=__("quote-settings-updated"))


@router.put("/{uuid}/cmg", response_model=schemas.Msg, status_code=200)
def update_settings(
        uuid: str,
        obj_in: schemas.CMGUpdate,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update quote cmg
    """
    quote = crud.quote.get_by_uuid(db, uuid)
    if not quote:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    if quote.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    crud.quote.update_cmg(db, quote, obj_in)
    return schemas.Msg(message=__("quote-cmg-updated"))
