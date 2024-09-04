from datetime import datetime
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, models,crud
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional,List

router = APIRouter(prefix="/copy_parameters", tags=["copy_parameters"])

@router.post("/copy-parameters")
def copy_parameters_between_nurseries(
    request: schemas.CopyParametersRequest, 
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    try:
        result = crud.copy_parameters.copy_parameters_between_nurseries(
            db=db,
            source_nursery_uuid=request.source_nursery_uuid,
            target_nursery_uuid=request.target_nursery_uuid,
            owner_uuid=current_user.uuid,
            elements_to_copy=request.elements_to_copy
        )
        return {"message": "Selected elements successfully duplicated"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

