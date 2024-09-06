from datetime import datetime, timedelta,timezone
import math
from typing import Optional, Union
from sqlalchemy import or_
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload,contains_eager 
from app.main import schemas, models,crud
import uuid as py_uuid



class CRUDJob(CRUDBase[models.Job, schemas.JobCreate,schemas.JobUpdate]):
    

    @classmethod
    def is_in_employee_job(cls,db:Session,employee_uuid:str,job_uuid:str):
        return db.query(models.JobEmployees).\
            filter(models.JobEmployees.job_uuid == job_uuid).\
                filter(models.JobEmployees.employee_uuid == employee_uuid).\
                    first()
    
    @classmethod
    def is_job_in_nursery(cls,db:Session,nursery_uuid:str,job_uuid:str):
        return db.query(models.NurseryJobs).\
            filter(models.NurseryJobs.job_uuid == job_uuid).\
                filter(models.NurseryJobs.nursery_uuid == nursery_uuid).\
                    first()
    
    @classmethod
    def get_by_uuids(cls, db: Session, uuids: list[str]) -> Optional[list[models.Job]]:
        return db.query(models.Job).\
                filter(models.Job.uuid.in_(uuids)).\
                    all()
    
    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Union[models.Job, None]:
        return db.query(models.Job).filter(models.Job.uuid == uuid,models.Job.status!="DELETED").\
            first()
    
    @classmethod
    def create(cls, db: Session, obj_in: list[schemas.JobCreate],added_by:models.Owner) -> list[models.Job]:
                
        
        job_list = [] 
        for obj in obj_in: 
            db_obj = models.Job(
                uuid= str(py_uuid.uuid4()),
                title_fr= obj.title_fr,
                title_en= obj.title_en,
                code = obj.code,
                description = obj.description,
                added_by_uuid = added_by.uuid
            )
            db.add(db_obj)
            db.flush()

            for employee_uuid in obj.employee_uuid_tab:
                job_employee = cls.is_in_employee_job(db,employee_uuid,db_obj.uuid)
                if not job_employee:
                    job_employee = models.JobEmployees(
                        uuid= str(py_uuid.uuid4()),
                        job_uuid = db_obj.uuid,
                        employee_uuid = employee_uuid,
                    )
                    db.add(job_employee)
                    db.flush()

            for nursery_uuid in obj.nursery_uuid_tab:
                job_nursery = cls.is_job_in_nursery(db,nursery_uuid,db_obj.uuid)
                if not job_nursery:
                    job_nursery = models.NurseryJobs(
                        uuid= str(py_uuid.uuid4()),
                        job_uuid = db_obj.uuid,
                        nursery_uuid = nursery_uuid
                    )
                    db.add(job_nursery)
                    db.flush()

        job_list.append(db_obj)
        db.commit()
        db.refresh(db_obj)
    
        return job_list
    
    @classmethod
    def update(cls, db: Session,obj_in: schemas.JobUpdate) -> models.Job:
        db_obj = cls.get_by_uuid(db, obj_in.uuid)
        
        db_obj.title_en = obj_in.title_en if obj_in.title_en else db_obj.title_en 
        db_obj.title_fr = obj_in.title_fr if obj_in.title_fr else db_obj.title_fr 
        db_obj.code = obj_in.code if obj_in.code else db_obj.code 
        
        db_obj.description = obj_in.description if obj_in.description else db_obj.description

        db.flush()
        for employee_uuid in obj_in.employee_uuid_tab:
            job_employee = cls.is_in_employee_job(db,employee_uuid,db_obj.uuid)
            if not job_employee:
                job_employee = models.JobEmployees(
                    uuid= str(py_uuid.uuid4()),
                    job_uuid = db_obj.uuid,
                    employee_uuid = db_obj.uuid,
                )
                db.add(job_employee)
                db.flush()
        
        for nursery_uuid in obj_in.nursery_uuid_tab:
            job_nursery = cls.is_job_in_nursery(db,nursery_uuid,db_obj.uuid)
            if not job_nursery:
                job_nursery = models.NurseryJobs(
                    uuid= str(py_uuid.uuid4()),
                    job_uuid = db_obj.uuid,
                    nursery_uuid = nursery_uuid
                )
                db.add(job_nursery)
                db.flush()

        db.commit()    
        db.refresh(db_obj)
        
        return db_obj
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str]):
        db_objs = cls.get_by_uuids(db, uuids)

        for db_obj in db_objs:
            db_obj.status = models.EmployeStatusEnum.DELETED
            db.commit()
    
    @classmethod
    def delete_nursery_job(cls,db:Session, obj_in:schemas.DeleteNurseryJobs):
        for job_uuid in obj_in.job_uuid_tab:
            db_obj = cls.is_job_in_nursery(db, obj_in.nursery_uuid,job_uuid)

            if db_obj and db_obj.status!= "DELETED":
                db_obj.status ="DELETED"
                db.commit()

    @classmethod
    def delete_employee_job(cls,db:Session, obj_in:schemas.DeleteEmployeeJobs):
        for job_uuid in obj_in.job_uuid_tab:
            db_obj = cls.is_in_employee_job(db, obj_in.employee_uuid,job_uuid)

            if db_obj and db_obj.status!= "DELETED":
                db_obj.status ="DELETED"
                db.commit()
    
    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        job_uuid:Optional[str] = None,
        keyword:Optional[str]= None,
        # order_filed:Optional[str] = None   
    ):
        
        record_query = db.query(models.Job).\
            filter(models.Job.status !="DELETED").\
                outerjoin(models.JobEmployees,models.Job.uuid == models.JobEmployees.job_uuid).\
                outerjoin(models.Employee, models.JobEmployees.employee_uuid == models.Employee.uuid).\
                    filter(models.Employee.status!="DELETED").\
                        options(contains_eager(models.Job.employees))

        
        # if order_filed:
        #     record_query = record_query.order_by(getattr(models.Team, order_filed))
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Job.title_fr.ilike('%' + str(keyword) + '%'),
                    models.Job.title_en.ilike('%' + str(keyword) + '%'),
                    models.Job.code.ilike('%' + str(keyword) + '%'),
                    models.Job.description.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Job.status == status)
        
        if order and order== "asc":
            record_query = record_query.order_by(models.Job.date_added.asc())
        
        elif order and order== "desc":
            record_query = record_query.order_by(models.Job.date_added.desc())

        if job_uuid:
            record_query = record_query.filter(models.Job.uuid == job_uuid)

        total = len(record_query.all())

        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.JobResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
job = CRUDJob(models.Job)





