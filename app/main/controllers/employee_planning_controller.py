from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi.encoders import jsonable_encoder
from app.main.core.config import Config
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/employee-planning", tags=["employee-planning"])


@router.post("/create", response_model=schemas.Msg, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:list[schemas.EmployeePlanningCreate],
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create planning for a given employee
    """
    employee_errors = []
    nursery_errors   = []

    nursery_employee_errors = []

    response = []
    errors =[]
    for obj in obj_in:
        
        employee = crud.employe.get_by_uuid(db,obj.employee_uuid)
        if not employee:
            employee_errors.append(obj.employee_uuid)  
        
        nursery  = crud.nursery.get_by_uuid(db,obj.nursery_uuid)
        if not nursery: 
            nursery_errors.append(obj.nursery_uuid) 
        

    print("erorrs:",nursery_errors,employee_errors)

    errors = employee_errors if employee_errors else nursery_errors
    
    print("erorrs:",errors)

    key_errors = "nursery-not-found" if nursery_errors else "employee-not-found"
    if len(errors):
        raise HTTPException(status_code=404, detail=f"{__(key_errors)}:" + ' '+'' .join(errors))    
    
    for obj in obj_in:
        exist_nursery_employee = crud.employe.is_in_nursery_employees(db,obj.employee_uuid,obj.nursery_uuid)
        if not exist_nursery_employee:
            nursery_employee_errors.append(f"{obj.employee_uuid}-{obj.nursery_uuid}")

    for obj in obj_in:
        employee = crud.employe.get_by_uuid(db,obj.employee_uuid)
        employee.begin_date = obj.begin_date
        employee.end_date = obj.end_date
        employee.typical_weeks = jsonable_encoder(obj.typical_weeks)
        nursery  = crud.nursery.get_by_uuid(db,obj.nursery_uuid)
        crud.employee_planning.insert_planning_for_employee(nursery,employee,db)
    
    
    return {"message":__("planning-created")}

# @router.put("/", response_model=schemas.Job, status_code=200)
# def update(
#     *,
#     db: Session = Depends(get_db),
#     obj_in:schemas.EmployeePlanningUpdate,
#     current_user:models.Owner = Depends(TokenRequired(roles =["owner"] ))
# ):
#     """
#     Update a Group
#     """

#     exist_planning = db.query(models.EmployeePlanning).\
#         filter(models.EmployeePlanning.uuid == obj_in.uuid).\
#             first()
    
#     employee = crud.employe.get_by_uuid(db,obj_in.employee_uuid)
#     nursery = crud.nursery.get_by_uuid(db,obj_in.nursery_uuid)

#     if not nursery:
#         raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
#     if not exist_planning:
#         raise HTTPException(status_code=404, detail=__("planning-not-found"))
    
#     if not employee: 
#         raise HTTPException(status_code=404, detail=__("member-not-found"))
    
#     employee.begin_date = obj_in.begi
   
#     exist_planning.nursery_uuid = obj_in.nursery_uuid
#     exist_planning.employee_uuid = obj_in.employee_uuid
    
    
#     return crud.job.update(db, obj_in)

@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    
    """
    Delete a Job
    """
    errors =[]

    for uuid in uuids:
        exist_planning = crud.employee_planning.get_by_uuid(db,uuid)
        if not exist_planning:
            errors.append(uuid)
    
    if errors:
        raise HTTPException(status_code=404, detail=f"{__('planning-not-found')}")
   
    db.query(models.EmployeePlanning).\
        filter(models.EmployeePlanning.uuid.in_(uuids)).\
            delete()
    
    db.commit()

    
    return {"message": __("planning-deleted")}


@router.get("/", response_model=schemas.EmployeePlanningList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["asc","desc"]),
    nursery_uuid:Optional[str] = None,
    employee_uuid:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    get Job with all data by passing filters
    """
    
    return crud.employee_planning.get_multi(
        db, 
        page, 
        per_page, 
        employee_uuid,
        nursery_uuid,
        order
    )

@router.get("/{planning_uuid}/details", response_model=schemas.EmployeePlanningMini)
def get(
    *,
    db: Session = Depends(get_db),
    planning_uuid:str,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    get Job with all data by passing filters
    """
    
    exist_planning = crud.employee_planning.get_by_uuid(db,planning_uuid)
    if not exist_planning:
        raise HTTPException(status_code=404, detail=__("planning-not-found"))
    
    return exist_planning
    