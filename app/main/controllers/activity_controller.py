from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/type_activity", tags=["type_activity"])

@router.post("/create", response_model=schemas.ActivityResponse, status_code=201)
def create_type_activity(
    *,
    activity_create: schemas.ActivityCreate, 
    db: Session = Depends(get_db)):
    db_activity = crud.activity.create_activity(db, activity_create)
    return db_activity
