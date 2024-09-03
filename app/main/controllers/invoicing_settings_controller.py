from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main import schemas, crud, models
from app.main.core.dependencies import get_db, TokenRequired
from app.main.core.i18n import __


router = APIRouter(prefix="/invoicing-settings", tags=["invoicing-settings"])


@router.post("/", response_model=schemas.QuoteSettingDetails, status_code=201)
def create(
        obj_in: schemas.QuoteSettingCreate,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Create quote settings
    """
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.invoicing_settings.create_quote_settings(db, obj_in)


@router.get("/", response_model=schemas.QuoteSettingList)
def get(
        nursery_uuid: str,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_added",
        is_default: bool = None,
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.invoicing_settings.get_quote_settings(
        db,
        nursery_uuid,
        current_user.uuid,
        page,
        per_page,
        order,
        order_filed,
        is_default,
    )


@router.put("/{uuid}", response_model=schemas.QuoteSettingDetails, status_code=200)
def update(
        uuid: str,
        obj_in: schemas.QuoteSettingUpdate,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update quote settings
    """
    quote_setting = crud.invoicing_settings.get_by_uuid(db, uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.invoicing_settings.update_quote_settings(db, quote_setting, obj_in)

# Set quote settings as default
@router.put("/default/{uuid}", response_model=schemas.QuoteSettingDetails, status_code=200)
def set_default(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Set quote settings as default
    """
    quote_setting = crud.invoicing_settings.get_by_uuid(db, uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    return crud.invoicing_settings.set_default_quote_settings(db, uuid)


@router.get("/{uuid}", response_model=schemas.QuoteSettingDetails)
def get_by_uuid(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get quote settings by uuid
    """
    quote_setting = crud.invoicing_settings.get_by_uuid(db, uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    return quote_setting


@router.delete("/{uuid}", response_model=schemas.Msg, status_code=200)
def delete(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Delete quote settings by uuid
    """
    quote_setting = crud.invoicing_settings.get_by_uuid(db, uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.is_default:
        raise HTTPException(status_code=400, detail=__("default-quote-setting-not-deletable"))

    crud.invoicing_settings.delete_quote_settings(db, uuid)
    return {"message": __("quote-setting-deleted")}


@router.post("/hourly-rate-range", response_model=schemas.HourlyRateRangeDetails, status_code=201)
def create_hourly_rate_range(
        obj_in: schemas.HourlyRateRangeCreate,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Create hourly rate range
    """
    quote_setting = crud.invoicing_settings.get_by_uuid(db, obj_in.quote_setting_uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    # check number_of_day_quote_setting_uuid_unique
    hourly_rate_range = crud.invoicing_settings.get_hourly_rate_range_by_quote_setting_and_number_of_day(
        db, obj_in.quote_setting_uuid, obj_in.number_of_day
    )
    if hourly_rate_range:
        raise HTTPException(status_code=409, detail=__("hourly-rate-range-exists"))

    return crud.invoicing_settings.create_hourly_rate_range(db, obj_in)


@router.put("/hourly-rate-range/{uuid}", response_model=schemas.HourlyRateRangeDetails, status_code=200)
def update_hourly_rate_range(
        uuid: str,
        obj_in: schemas.HourlyRateRangeUpdate,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update hourly rate range
    """
    hourly_rate_range = crud.invoicing_settings.get_hourly_rate_range_by_uuid(db, uuid)
    if not hourly_rate_range:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    if hourly_rate_range.quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    quote_setting = crud.invoicing_settings.get_by_uuid(db, obj_in.quote_setting_uuid)
    if not quote_setting:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    if quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-setting-not-found"))

    hourly_rate_range = crud.invoicing_settings.get_hourly_rate_range_by_quote_setting_and_number_of_day(
        db, obj_in.quote_setting_uuid, obj_in.number_of_day
    )
    if hourly_rate_range and hourly_rate_range.uuid != uuid:
        raise HTTPException(status_code=409, detail=__("hourly-rate-range-exists"))

    return crud.invoicing_settings.update_hourly_rate_range(db, hourly_rate_range, obj_in)


@router.get("/hourly-rate-range/{uuid}", response_model=schemas.HourlyRateRangeDetails, status_code=200)
def get_hourly_rate_range_by_uuid(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get hourly rate range by uuid
    """
    hourly_rate_range = crud.invoicing_settings.get_hourly_rate_range_by_uuid(db, uuid)
    if not hourly_rate_range:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    if hourly_rate_range.quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    return hourly_rate_range


@router.delete("/hourly-rate-range/{uuid}", response_model=schemas.Msg, status_code=200)
def delete_hourly_rate_range(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Delete hourly rate range by uuid
    """
    hourly_rate_range = crud.invoicing_settings.get_hourly_rate_range_by_uuid(db, uuid)
    if not hourly_rate_range:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    if hourly_rate_range.quote_setting.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("hourly-rate-range-not-found"))

    crud.invoicing_settings.delete_hourly_rate_range(db, uuid)
    return {"message": __("hourly-rate-range-deleted")}
