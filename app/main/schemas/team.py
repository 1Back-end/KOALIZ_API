from datetime import datetime,date
from typing import Any, List, Optional
from fastapi import HTTPException, Query
from pydantic import BaseModel, EmailStr,ConfigDict,field_validator, model_validator

from app.main.schemas.base import DataList
from app.main.schemas.preregistration import TimeSlotInputSchema
from .file import File
from app.main.models.team import TeamStatusEnum
from app.main.schemas.nursery import NurseryMini
from app.main.schemas.employee import EmployeSlim


class TeamBase(BaseModel):
    name: str
    leader_uuid: str
    description: Optional[str] = None
    status: str = Query(..., enum=[st.value for st in TeamStatusEnum if st.value != TeamStatusEnum.DELETED])

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(TeamBase):
    member_uuid_tab: list[str]

    

class TeamUpdate(TeamBase):
    uuid:str
    member_uuid_tab: list[str]


class TeamInDB(TeamBase):
    uuid: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class EmployeSlim(BaseModel):
    uuid: str
    email: str
    firstname: str
    lastname: str
    avatar: Optional[File] = None
    status: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class TeamResponse(TeamInDB):
    employees: list[EmployeSlim] = []
    leader_uuid: str
    leader: EmployeSlim
    model_config = ConfigDict(from_attributes=True)

class TeamResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data:list[TeamResponse] =[]

    model_config = ConfigDict(from_attributes=True)


class GroupBase(BaseModel):
    title_fr: str
    title_en:str
    description: Optional[str] = None
    code:str
    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    title_fr: str
    title_en:str
    description: Optional[str] = None
    code:str
    model_config = ConfigDict(from_attributes=True)

class GroupCreate(GroupBase):
    team_uuid_tab: Optional[list[str]] = []

class JobCreate(GroupBase):
    employee_uuid_tab: Optional[list[str]] = []
    nursery_uuid_tab: Optional[list[str]] = []
    
class JobUpdate(GroupBase):
    uuid:str
    # status:str
    employee_uuid_tab: Optional[list[str]] = []
    nursery_uuid_tab: Optional[list[str]] = []


class GroupUpdate(GroupBase):
    uuid:str
    # status:str
    team_uuid_tab: Optional[list[str]] = []


class GroupInDB(GroupBase):
    uuid: str
    # status:str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class DeleteTeamFromGroup(BaseModel):
    group_uuid: str
    team_uuid_tab: list[str] = []

class DeleteEmployeeJobs(BaseModel):
    employee_uuid: str
    job_uuid_tab: list[str] = []

class DeleteNurseryJobs(BaseModel):
    nursery_uuid: str
    job_uuid_tab: list[str] = []

class JobInDB(GroupBase):
    uuid: str
    status:str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class Group(GroupInDB):
    group_teams: Optional[list[TeamResponse]] = None
    model_config = ConfigDict(from_attributes=True)

class Job(GroupInDB):
    nursery_list : Optional[list[NurseryMini]]
    employee_list : Optional[list[EmployeSlim]]
    model_config = ConfigDict(from_attributes=True)

class GroupResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data:list[Group] =[]

    model_config = ConfigDict(from_attributes=True)

class JobResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data:list[Job] =[]

    model_config = ConfigDict(from_attributes=True)

class Year(BaseModel):
    uuid: str
    year: int
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class Month(BaseModel):
    uuid: str
    start_date: date
    end_date: date
    year:Year
    date_added: datetime
    date_modified: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Week(BaseModel):
    uuid: str
    start_date: date
    end_date: date
    week_index:int
    month:Month

    model_config = ConfigDict(from_attributes=True)

class Day(BaseModel):
    uuid:str
    day:date
    day_of_week:str
    month:Month
    year:Year
    week:Week

class EmployeePlanningBase(BaseModel):
    nursery_uuid: str
    employee_uuid: str
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class EmployeePlanningCreate(EmployeePlanningBase):
    begin_date: date
    end_date: date
    typical_weeks: list[list[list[TimeSlotInputSchema]]]

    @model_validator(mode='wrap')
    def validate_end_date(self, handler):
        validated_self = handler(self)
        for week in validated_self.typical_weeks:
            for day in week:
                if len(day) > 5:
                    raise HTTPException(status_code=422, detail=("Each week's data list cannot exceed 5 items"))

        begin_date = validated_self.begin_date
        if validated_self.end_date <= begin_date:
            raise ValueError("End date must be after to begin date.")
        return validated_self
    pass


class EmployeePlanningUpdate(EmployeePlanningBase):
    uuid: Optional[str] = None

class EmployeePlanning(BaseModel):
    uuid: Optional[str] = None
    employee: Optional[EmployeSlim] = None
    nursery: Optional[NurseryMini] = None
    day: Any
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeePlanningMini(BaseModel):
    
    uuid: Optional[str] = None
    day:Day
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeePlanningList(DataList):

    data: list[EmployeePlanning] = []


   

