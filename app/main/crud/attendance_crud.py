import math
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Attendance
from app.main.schemas import AttendanceCreate, AttendanceUpdate, AttendanceList, AttendanceMini


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: AttendanceCreate) -> Attendance:

        attendance_record = db.query(Attendance).filter_by(
            child_uuid=obj_in.child_uuid,
            date=obj_in.date,
            nursery_uuid=obj_in.nursery_uuid
        ).first()
        if attendance_record:
            attendance_record.arrival_time = obj_in.arrival_time
            attendance_record.departure_time = obj_in.departure_time
        else:
            attendance_record = Attendance(
                uuid=str(uuid.uuid4()),
                date=obj_in.date,
                arrival_time=obj_in.arrival_time,
                departure_time=obj_in.departure_time,
                added_by_uuid=obj_in.employee_uuid,
                child_uuid=obj_in.child_uuid,
                nursery_uuid=obj_in.nursery_uuid
            )
            db.add(attendance_record)
        db.commit()
        db.refresh(attendance_record)
        return attendance_record
    
    @classmethod
    def get_attendance_by_uuid(cls, db: Session, uuid: str) -> Optional[AttendanceMini]:
        return db.query(Attendance).filter(Attendance.uuid == uuid).first()
    
    @classmethod
    def update(cls, db: Session, obj_in: AttendanceUpdate) -> AttendanceMini:
        attendance = cls.get_attendance_by_uuid(db, obj_in.uuid)
        attendance.arrival_time = obj_in.arrival_time if obj_in.arrival_time else attendance.arrival_time
        attendance.departure_time = obj_in.departure_time if obj_in.departure_time else attendance.departure_time
        attendance.date = obj_in.date if obj_in.date else attendance.date
        db.commit()
        db.refresh(attendance)
        return attendance
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> AttendanceMini:
        db.query(Attendance).filter(Attendance.uuid.in_(uuids)).delete()
        db.commit()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        employee_uuid:Optional[str] = None,
        nursery_uuid:Optional[str] = None,
        child_uuid:Optional[str] = None,
        order_field:Optional[str] = 'date_added',
        keyword:Optional[str]= None,
    ):
        record_query = db.query(Attendance)

        # if keyword:
        #     record_query = record_query.filter(
        #         or_(
        #             Attendance.observation.ilike('%' + str(keyword) + '%')
        #         )
        #     )

        if child_uuid:
            record_query = record_query.filter(Attendance.child_uuid == child_uuid)
        if nursery_uuid:
            record_query = record_query.filter(Attendance.nursery_uuid == nursery_uuid)
        if employee_uuid:
            record_query = record_query.filter(Attendance.added_by_uuid == employee_uuid)

        if order == "asc":
            record_query = record_query.order_by(getattr(Attendance, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Attendance, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return AttendanceList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

attendance = CRUDAttendance(Attendance)
