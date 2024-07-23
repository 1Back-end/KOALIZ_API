from datetime import time

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/pre-registrations", tags=["pre-registrations"])


@router.post("/create", response_model=schemas.ChildDetails, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.PreregistrationCreate,
):
    """
    Create preregistration
    """

    return crud.preregistration.create(db, obj_in, "dfd")


@router.get("/{uuid}", response_model=schemas.PreregistrationDetails, status_code=200)
def get_special_folder(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Get a special folder """

    return crud.preregistration.get_by_uuid(db, uuid)


@router.delete("/{uuid}", response_model=schemas.Msg, status_code=200)
def delete_special_folder(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Delete a special folder """

    crud.preregistration.delete_a_special_folder(db, uuid)

    return {"message": __("folder-deleted")}

@router.put("/status", response_model=schemas.PreregistrationDetails, status_code=200)
def change_status_of_special_folder(
    uuid: str,
    status: str = Query(..., enum=[st.value for st in models.PreRegistrationStatusType if st.value != models.PreRegistrationStatusType.PENDING]),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Change status of a special folder """

    return crud.preregistration.change_status_of_a_special_folder(db, uuid=uuid, status=status)


@router.put("", response_model=schemas.ChildDetails, status_code=200)
def update_special_folder(
    obj_in: schemas.PreregistrationUpdate,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Update a special folder """

    return crud.preregistration.update(db, obj_in)


@router.put("/note", response_model=schemas.PreregistrationDetails, status_code=200)
def add_note_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add note to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="NOTE")

@router.put("/document", response_model=schemas.PreregistrationDetails, status_code=200)
def add_document_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add document to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="DOCUMENT")

@router.put("/meeting", response_model=schemas.PreregistrationDetails, status_code=200)
def add_meeting_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add meeting to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="MEETING")

@router.put("/action", response_model=schemas.PreregistrationDetails, status_code=200)
def add_action_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add action to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="MEETING")


@router.put("/call", response_model=schemas.PreregistrationDetails, status_code=200)
def add_call_to_special_folder(
    *,
    obj_in: schemas.TrackingCase=Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add call to special folder """

    return crud.preregistration.add_tracking_case(db, obj_in=obj_in, interaction_type="CALL")
