from datetime import date, datetime, time

from app.main.core.dependencies import TeamTokenRequired, get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.main.schemas.preregistration import ChildResponse


router = APIRouter(prefix="/nurseries", tags=["nurseries"])


@router.post("/create", response_model=schemas.Nursery, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NurseryCreate,
    current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Create nursery
    """
    if current_user.role.group == "administrators" and not obj_in.owner_uuid:
        raise HTTPException(status_code=400, detail=__("owner-required"))

    current_user_uuid = current_user.uuid
    if current_user.role.code == "owner":
        obj_in.owner_uuid = current_user.uuid
        current_user_uuid = None

    return crud.nursery.create(db, obj_in, current_user_uuid)


@router.put("/actived", response_model=schemas.Nursery, status_code=200)
def update_active_nursery(
    *,
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Update active nursery
    """
    exist_nursery = crud.nursery.get(db=db, uuid=uuid)
    if not exist_nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    exist_nursery.is_actived=True
    db.commit()

    nurseries = db.query(models.Nursery)\
        .filter(models.Nursery.owner_uuid == current_user.uuid)\
        .filter(models.Nursery.uuid != uuid)\
        .all()
    
    for nursery in nurseries:
        print(nursery.uuid)
        nursery.is_actived=False
        db.commit()

    return exist_nursery


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
        owner_uuid: str = None,
        current_user=Depends(TokenRequired(roles=["administrator", "edimester", "accountant", "owner"]))
):
    """
    get all with filters
    """

    return crud.nursery.get_many(
        db,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status,
        total_places,
        current_user.uuid if current_user.role.code == "owner" else owner_uuid
    )


@router.get("/all-children", response_model=list[schemas.ChildMini3])
def read_all_nursery_children(
    *,
    nursery_uuid: str,
    db: Session = Depends(get_db),
    current_user: models.TeamDevice = Depends(TokenRequired(roles=["owner"]))
):
    nursery = crud.nursery.get_by_uuid(db,nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    # Trouver toutes les préinscriptions acceptées pour la crèche spécifiée
    accepted_preregistrations = db.query(models.PreRegistration).filter(
        models.PreRegistration.nursery_uuid == nursery_uuid,
        models.PreRegistration.status == models.PreRegistrationStatusType.ACCEPTED
    ).all()

    # Récupérer les UUIDs des enfants acceptés
    child_uuids = [preregistration.child_uuid for preregistration in accepted_preregistrations if preregistration.child_uuid]

    # Filtrer les enfants par UUID et is_accepted
    children = db.query(models.Child).filter(models.Child.uuid.in_(child_uuids), models.Child.is_accepted == True).all()

    return children

@router.get("/children", response_model=list[schemas.Transmission])
def read_children_by_nursery(
    *,
    nursery_uuid:str,
    child_uuid: Optional[str] = None,
    # page: int = 1,
    # per_page: int = 30,
    # order: str = Query("desc", enum=["asc", "desc"]),
    # order_filed: str = "date_added",
    # keyword: Optional[str] = None,
    filter_date:Optional[date] = None,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    nursery = crud.nursery.get_by_uuid(db,nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if current_team_device.nursery_uuid!=nursery_uuid:
        raise HTTPException(status_code=403, detail=__("not-authorized"))

    return crud.nursery.get_children_by_nursery(
        db=db, 
        nursery_uuid=nursery_uuid,
        child_uuid=child_uuid,
        filter_date=filter_date
        # page=page,
        # per_page=per_page,
        # order=order,
        # order_filed=order_filed,
        # keyword=keyword
        )


@router.get("/all/slim", response_model=list[schemas.OtherNurseryByGuest], status_code=200)
def get_all_without_filter(
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get all nurseries
    """
    return crud.nursery.get_all_uuids_of_same_owner(db, current_user.uuid)


@router.get("/employee/{nursery_uuid}/home", response_model=schemas.EmployeeHomePageList)
def get_employee_home_page(
    nursery_uuid: str,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    nursery_details = crud.nursery.get_employee_home_page(
        db=db,
        nursery_uuid=nursery_uuid
    )
    return nursery_details


@router.get("/{uuid}/opening_hours", response_model=schemas.OpeningHoursList)
async def get_opening_hours(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):

    nursery = crud.nursery.get(db, uuid)
    if not nursery or nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return nursery


@router.post("/{uuid}/opening_hours", response_model=schemas.OpeningHoursList)
async def create_opening_hours(
        opening_hours: list[schemas.OpeningHoursInput],
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    if len(opening_hours) > 7:
        raise HTTPException(status_code=422, detail="Opening hours data list cannot exceed 7 items")
    nursery = crud.nursery.get(db, uuid)
    if not nursery or nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.nursery.add_update_opening_hours(db, nursery, opening_hours)


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


@router.get("/{uuid}", response_model=schemas.Nursery, status_code=200)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["administrator", "edimester", "accountant", "owner"]))
):
    """
    Get nursery details
    """
    nursery = crud.nursery.get_by_uuid(db, uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if current_user.role.code == "owner" and nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return nursery


@router.put("/{uuid}", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        obj_in: schemas.NurseryUpdateBase,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["administrator", "edimester", "owner"]))
):
    """
    Update nursery
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if current_user.role.code == "owner" and nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.nursery.update(db, nursery, obj_in)


@router.put("/{uuid}/status", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.NurseryStatusType if
                                       st.value != models.NurseryStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator", "edimester"]))
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


@router.get("/{uuid}/dashboard/statistics", status_code=200, response_model=schemas.DashboardStatistics)
def get_statistics(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
    Get statistics
    """
    nursery = crud.nursery.get_by_uuid(db, uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if current_user.role.code == "owner" and nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    children_per_day = crud.nursery.get_number_children_per_day_in_current_week(db, nursery)

    invoice_statistics = crud.invoice.get_nursery_statistic(db, nursery.uuid)

    return {
        "children_per_day": children_per_day,
        "invoice_statistics": invoice_statistics,
        "children_per_hour": {}
    }
