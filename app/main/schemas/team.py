from datetime import datetime
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, EmailStr,ConfigDict
from .file import File
from app.main.models.team import TeamStatusEnum
from app.main.schemas.nursery import NurseryMini


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


   

