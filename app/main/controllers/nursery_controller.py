from datetime import time

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/nurseries", tags=["nurseries"])


@router.post("/create", response_model=schemas.Nursery, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NurseryCreate,
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Create nursery
    """

    return crud.nursery.create(db, obj_in, current_user.uuid)


@router.put("/{uuid}", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        obj_in: schemas.NurseryUpdateBase,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.nursery.update(db, nursery, obj_in)


@router.put("/{uuid}/status", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.NurseryStatusType if
                                       st.value != models.NurseryStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery owner status
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if nursery.status == status:
        return nursery

    return crud.nursery.update_status(db, nursery, status)


@router.get("/{uuid}", response_model=schemas.Nursery, status_code=200)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Get nursery details
    """
    nursery = crud.nursery.get_by_uuid(db, uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return nursery


@router.delete("", response_model=schemas.Msg)
def delete(
        *,
        db: Session = Depends(get_db),
        uuids: list[str],
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Delete many(or one)
    """
    crud.nursery.delete(db, uuids)
    return {"message": __("nursery-deleted")}


@router.get("/", response_model=schemas.NurseryList)
def get(
        *,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_added",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.NurseryStatusType]),
        total_places: int = None,
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    get all with filters
    """

    return crud.nursery.get_multi(
        db,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status,
        total_places
    )


@router.put("/{uuid}/opening-hour", response_model=schemas.NurseryOpeningTime, status_code=200)
def update_opening_hour(
        uuid: str,
        data: schemas.OpeningTime,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery owner status
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    try:
        open_from = time.fromisoformat(data.open_from)
        open_to = time.fromisoformat(data.open_to)
    except ValueError:
        raise HTTPException(status_code=400, detail=__("invalid-time-format"))

    if open_from >= open_to:
        raise HTTPException(status_code=400, detail=__("to-not-greater-from"))

    return crud.nursery.update_opening_hour(db, nursery, data)


@router.get("/guest/{slug}", response_model=schemas.NurseryByGuest, status_code=200)
def get_by_slug_guest(
        slug: str,
        db: Session = Depends(get_db)
):
    """
    Get nursery by slug and return all nurseries of the same owner
    """
    nursery = crud.nursery.get_by_slug(db, slug)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    other_nurseries = crud.nursery.get_all_uuids_of_same_owner(db, nursery.owner_uuid, [nursery.uuid])

    nursery.others = other_nurseries

    return nursery


@router.post("/opening_hours/{nursery_uuid}", response_model=schemas.OpeningHoursList, include_in_schema=False)
async def create_opening_hours(opening_hours: schemas.OpeningHoursInput, nursery_uuid: str, db: Session = Depends(get_db)):

    nursery = crud.nursery.get(db, nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    try:
        from_time = time.fromisoformat(opening_hours.hours.from_time)
        to_time = time.fromisoformat(opening_hours.hours.to_time)
    except ValueError:
        raise HTTPException(status_code=400, detail=__("invalid-time-format"))

    if from_time >= to_time:
        raise HTTPException(status_code=400, detail=__("to-not-greater-from"))

    new_opening_hours = models.NurseryOpeningHour(
        day_of_week=opening_hours.day_of_week,
        from_time=opening_hours.hours.from_time,
        to_time=opening_hours.hours.to_time,
        nursery_uuid=nursery_uuid
    )
    db.add(new_opening_hours)
    db.commit()

    return nursery


@router.get("/opening_hours/{nursery_uuid}", response_model=schemas.OpeningHoursList, include_in_schema=False)
async def get_opening_hours(nursery_uuid: str, db: Session = Depends(get_db)):

    nursery = crud.nursery.get(db, nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    # Retrieve opening hours associated with the business
    opening_hours = db.query(models.NurseryOpeningHour).filter(models.NurseryOpeningHour.nursery_uuid == nursery.uuid).all()
    # opening_hours_data = [oh.dict() for oh in opening_hours]  # Convert to dictionaries

    return nursery
    return {"nursery": business.id, "opening_hours": opening_hours_data}
