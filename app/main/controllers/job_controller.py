from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/create", response_model=list[schemas.Job], status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:list[schemas.JobCreate],
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create new Job
    """
    employee_errors = []
    nursery_errors   = []
    errors =[]
    for obj in obj_in:
        if obj.employee_uuid_tab:
            employees = crud.employe.get_by_uuids(db,obj.employee_uuid_tab)

            if not employees or len(employees)!= len(obj.employee_uuid_tab):
                employee_errors.append(obj.employee_uuid_tab)
        
        if obj.nursery_uuid_tab:
            nurseries  = crud.nursery.get_by_uuids(db,obj.nursery_uuid_tab,current_user.uuid)
            
            if not nurseries or len(nurseries)!= len(obj.nursery_uuid_tab):
                nursery_errors.append(obj.nursery_uuid_tab)

    errors = employee_errors if employee_errors else nursery_errors
    key_errors = "nursery-not-found" if nursery_errors else "employee-not-found" if employee_errors else []
    if len(errors):
        raise HTTPException(status_code=404, detail=f"{__(key_errors)}:" + ' '+'' .join(errors))    
    
    return crud.job.create(db, obj_in,current_user)

@router.put("/", response_model=schemas.Job, status_code=200)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.JobUpdate,
    current_user:models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Update a Group
    """

    print("nurseries",current_user.nurseries)
    print("employee",current_user.nurseries[0].employees)

    exist_group = crud.job.get_by_uuid(db,obj_in.uuid)

    if not exist_group:
        raise HTTPException(status_code=404, detail=__("job-not-found"))

    if exist_group.added_by_uuid!= current_user.uuid:
        raise HTTPException(status_code=400, detail=__("not-authorized"))
    
    if obj_in.employee_uuid_tab:
        employee = crud.employe.get_by_uuids(db,obj_in.employee_uuid_tab)

        if not employee or len(employee)!= len(obj_in.employee_uuid_tab):
            raise HTTPException(status_code=404, detail=__("member-not-found"))

    if obj_in.nursery_uuid_tab:
        nurseries = crud.nursery.get_by_uuids(db,obj_in.nursery_uuid_tab,current_user.uuid)

        if not nurseries or len(nurseries)!= len(obj_in.nursery_uuid_tab):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    
    
    return crud.job.update(db, obj_in)

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
    groups = crud.job.get_by_uuids(db, uuids)
    if not groups or len(groups)!=len(uuids):
        raise HTTPException(status_code=404, detail=__("job-not-found"))
    
    for group in groups:
        if group.added_by_uuid!= current_user.uuid:
            errors.append(group.uuid)
    
    if len(errors):
        raise HTTPException(status_code=400, detail=f"{__('not-authorized')}")

    crud.job.soft_delete(db, uuids)
    return {"message": __("job-deleted")}


@router.delete("/nursery/delete", response_model=schemas.Msg)
def delete_job_for_nursery(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.DeleteNurseryJobs,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a job for nursery
    """
    
    nursery_owner_errors =[]
                
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    if not obj_in.nursery_uuid in [current_nursery.uuid for current_nursery in current_user.nurseries]:
        nursery_owner_errors.append(obj_in.nursery_uuid)
    
    if nursery_owner_errors:
        raise HTTPException(status_code=400, detail=f"{__('nursery-owner-not-authorized')}")
    
    nursery_jobs = crud.job.get_by_uuids(db, obj_in.job_uuid_tab)
    if not nursery_jobs or len(nursery_jobs)!= len(obj_in.job_uuid_tab):
        raise HTTPException(status_code=404, detail=__("job-not-found"))
    
    crud.job.delete_nursery_job(db, obj_in)
    return {"message": __("job-deleted")}

@router.delete("/employee/delete", response_model=schemas.Msg)
def delete_employee_job(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.DeleteEmployeeJobs,
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    Delete a job for the specified employee
    """
    nursery_owner_errors =[]
    employee = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employee:
        raise HTTPException(status_code=404, detail=__("member-not-found"))
    
    for nursery in current_user.nurseries:
        employee_uuid_tab = [i.uuid for i in nursery.employees]
        
        if not obj_in.employee_uuid in employee_uuid_tab:
            nursery_owner_errors.append(obj_in.employee_uuid)
    
    if nursery_owner_errors:
        raise HTTPException(status_code=400, detail=f"{__('nursery-owner-not-authorized')}")
    
    jobs = crud.job.get_by_uuids(db, obj_in.job_uuid_tab)
    if not jobs or len(jobs)!= len(obj_in.job_uuid_tab):
        raise HTTPException(status_code=404, detail=__("job-not-found"))
    
    crud.job.delete_employee_job(db, obj_in)
    return {"message": __("job-deleted")}

@router.get("/", response_model=schemas.JobResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["asc","desc"]),
    job_uuid:Optional[str] = None,
    status: str = Query(None, enum =["CREATED","UNACTIVED","SUSPENDED"]),
    keyword:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    """
    get Job with all data by passing filters
    """
    
    return crud.job.get_multi(
        db, 
        page, 
        per_page, 
        order,
        status,
        job_uuid,
        keyword
    )
    