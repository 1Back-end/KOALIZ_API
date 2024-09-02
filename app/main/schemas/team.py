from datetime import datetime
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, EmailStr,ConfigDict
from .file import File
from app.main.models.team import TeamStatusEnum

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

class GroupCreate(GroupBase):
    team_uuid_tab: Optional[list[str]] = []

class GroupUpdate(GroupBase):
    uuid:str
    # status:str
    team_uuid_tab: Optional[list[str]] = []


class GroupInDB(GroupBase):
    uuid: str
    status:str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class Group(GroupInDB):
    model_config = ConfigDict(from_attributes=True)


   

