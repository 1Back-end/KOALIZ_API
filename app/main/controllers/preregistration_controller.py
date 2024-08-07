from datetime import time, date

from fastapi.encoders import jsonable_encoder

from app.main.core import dependencies
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/pre-registrations", tags=["pre-registrations"])


@router.post("/create", response_model=schemas.ChildDetails, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.PreregistrationCreate,
    background_task: BackgroundTasks,
):
    """
    Create preregistration
    """

    return crud.preregistration.create(db, obj_in, background_task=background_task)


@router.post("/create/owner", response_model=schemas.ChildDetails, status_code=201)
def create_by_owner(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.PreregistrationCreate,
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Owner create preregistration
    """

    return crud.preregistration.create(db, obj_in, current_user.uuid)



@router.put("/{uuid}/transfer", response_model=schemas.Msg, status_code=200)
def transfer(
    *,
    uuid: str,
    db: Session = Depends(get_db),
    obj_in: schemas.TransferPreRegistration,
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Transfer a preregistration
    """

    crud.preregistration.transfer(db, uuid, obj_in, current_user.uuid)
    return schemas.Msg(message=__("nursery-transfer-successfully"))


@router.get("/{uuid}", response_model=Optional[schemas.PreregistrationDetails], status_code=200)
def get_special_folder(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Get a special folder """

    return crud.preregistration.get_by_uuid(db, uuid)

@router.get("/detail/{uuid}", response_model=schemas.PreregistrationDetails, status_code=200)
def get_special_folder_without_permission(
    uuid: str,
    db: Session = Depends(get_db),
):
    """ Get a special folder without authentication"""

    return crud.preregistration.get_by_uuid(db, uuid)


@router.put("/status", response_model=schemas.PreregistrationDetails, status_code=200)
def change_status_of_special_folder(
    uuid: str,
    status: str = Query(..., enum=[st.value for st in models.PreRegistrationStatusType if st.value != models.PreRegistrationStatusType.PENDING]),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Change status of a special folder """

    return crud.preregistration.change_status_of_a_special_folder(db, folder_uuid=uuid, status=status, performed_by_uuid=current_user.uuid)

# 4cdb3f7f-8f7d-4113-95b8-35521d55d76c owner uuid
@router.put("", response_model=schemas.ChildDetails, status_code=200)
def update_special_folder(
    obj_in: schemas.PreregistrationUpdate,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Update a special folder """

    return crud.preregistration.update(db, obj_in=obj_in, performed_by_uuid=current_user.uuid)

@router.put("/update", response_model=schemas.ChildDetails, status_code=200)
def update_special_folder_without_permission(
    obj_in: schemas.PreregistrationUpdate,
    db: Session = Depends(get_db),
):
    """ Update a special folder without authentication """

    return crud.preregistration.update_pre_registration(db, obj_in=obj_in)


@router.put("/note", response_model=schemas.PreregistrationDetails, status_code=200)
def add_note_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add note to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="NOTE", performed_by_uuid=current_user.uuid)

@router.put("/document", response_model=schemas.PreregistrationDetails, status_code=200)
def add_document_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add document to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="DOCUMENT", performed_by_uuid=current_user.uuid)

@router.put("/meeting", response_model=schemas.PreregistrationDetails, status_code=200)
def add_meeting_to_special_folder(
    *,
    obj_in: schemas.MeetingType=Body(...),
    db: Session = Depends(get_db),
    # current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add meeting to special folder """

    obj_in = jsonable_encoder(obj_in)
    meeting_type = db.query(models.MeetingType).\
        filter(models.MeetingType.uuid == obj_in["meeting_type_uuid"]).\
            first()
    if not meeting_type:
        raise HTTPException(status_code=400, detail=__("meeting-type-not-found"))
    
    obj_in["meeting_type"] = {
        "uuid": meeting_type.uuid,
        "title_fr": meeting_type.title_fr,
        "title_en": meeting_type.title_en
    }
    # print("obj_in112:",obj_in["preregistration_uuid"])

    obj= schemas.TrackingCase(
        preregistration_uuid=obj_in["preregistration_uuid"],
        details = obj_in
    )
    # print("obj1",obj)

    return crud.preregistration.add_tracking_case(db, obj_in=obj, interaction_type="MEETING", performed_by_uuid="current_user.uuid")

@router.put("/activity-reminder", response_model=schemas.PreregistrationDetails, status_code=200)
def add_activity_reminder_to_special_folder(
    *,
    obj_in:schemas.ActivityReminder=Body(...),
    db: Session = Depends(get_db),
    # current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add activity reminder to special folder """

    obj_in = jsonable_encoder(obj_in)
    activity_reminder_type = db.query(models.ActivityReminderType).\
        filter(models.ActivityReminderType.uuid == obj_in["activity_reminder_type_uuid"]).\
            first()
    if not activity_reminder_type:
        raise HTTPException(status_code=400, detail=__("activity-reminder-type-not-found"))
    
    obj_in["activity_reminder_type"] = {
        "uuid": activity_reminder_type.uuid,
        "title_fr": activity_reminder_type.title_fr,
        "title_en": activity_reminder_type.title_en
    }
    # print("obj_in11:",obj_in)

    obj= schemas.TrackingCase(
        preregistration_uuid=obj_in["preregistration_uuid"],
        details = obj_in
    )
    # print("obj1",obj)

    return crud.preregistration.add_tracking_case(db, obj_in=obj, interaction_type="ACTIVITY_REMINDER", performed_by_uuid="current_user.uuid")

@router.put("/call", response_model=schemas.PreregistrationDetails, status_code=200)
def add_call_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add call to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="CALL", performed_by_uuid=current_user.uuid)

@router.get("", response_model=schemas.PreRegistrationList, status_code=200)
def get_many(
        nursery_uuid: str,
        tag_uuid: str = None,
        status: str = None,
        begin_date: date = None,
        end_date: date = date.today(),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_field: str = "date_added",
        keyword: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get nursery details
    """
    return crud.preregistration.get_many(
        db,
        nursery_uuid,
        status,
        begin_date,
        end_date,
        page,
        per_page,
        order,
        order_field,
        keyword,
        tag_uuid
    )
@router.get("/transmission/child/{uuid}", response_model=schemas.Transmission, status_code=200)
def get_child_transmission(
        uuid: str,
        nursery_uuid: str,
        page: int = 1,
        per_page: int = 30,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(dependencies.TeamTokenRequired())
):
    """
    Get child transmission
    """
    if current_team_device.nursery_uuid!=nursery_uuid:
        raise HTTPException(status_code=403, detail=__("not-authorized"))
    
    return crud.preregistration.get_transmission(
        uuid,
        page,
        per_page,
        db
    )

# 8d54df37-9954-44a3-8733-9be1f9f5a148
@router.delete("/{uuid}", response_model=schemas.Msg, status_code=200)
def delete_special_folder(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Delete a special folder """

    crud.preregistration.delete_a_special_folder(db, folder_uuid=uuid, performed_by_uuid=current_user.uuid)

    return {"message": __("folder-deleted")}
