# from app.main.core.dependencies import get_db, TokenRequired
# from app.main import schemas, models,crud
# from app.main.core.i18n import __
# from app.main.core.config import Config
# from fastapi import APIRouter, Depends, Body, HTTPException, Query
# from sqlalchemy.orm import Session
# from typing import Optional,List
# router = APIRouter(prefix="/nursery-holidays", tags=["nursery-holidays"])

# @router.post("/", response_model=schemas.NurseryHoliday)
# def create_nursery_holiday(holiday: schemas.NurseryHolidayCreate, db: Session = Depends(get_db)):
#     try:
#         return crud.create_nursery_holiday(db, holiday)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/{holiday_uuid}", response_model=schemas.NurseryHoliday)
# def get_nursery_holiday_by_uuids(holiday_uuid: str, db: Session = Depends(get_db)):
#     try:
#         return crud.NuseryHolidayCRUD.get_nursery_holiday_by_uuid(db, holiday_uuid)
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
    
# @router.get("/", response_model=List[schemas.NurseryHoliday])
# def read_nursery_holidays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.NuseryHolidayCRUD.get_nursery_holiday(db, skip=skip, limit=limit)

# @router.put("/{holiday_uuid}", response_model=schemas.NurseryHoliday)
# def update_nursery_holiday(holiday_uuid: str, holiday: schemas.NurseryHolidayUpdate, db: Session = Depends(get_db)):
#     updated_holiday = crud.NuseryHolidayCRUD.update_nursery_holiday(db, holiday_uuid, holiday)
#     if updated_holiday is None:
#         raise HTTPException(status_code=404, detail="Nursery holiday not found")
#     return updated_holiday
# @router.delete("/{holiday_uuid}", response_model=schemas.NurseryHoliday)
# def delete_nursery_holiday(holiday_uuid: str, db: Session = Depends(get_db)):
#     try:
#         deleted_holiday = crud.NuseryHolidayCRUD.delete_nursery_holiday(db, holiday_uuid)
#         return deleted_holiday
#     except HTTPException as e:
#         raise e