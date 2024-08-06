from datetime import datetime
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, EmailStr,ConfigDict

from .file import File
from app.main.models.team import EmployeStatusEnum

class EmployeBase(BaseModel):
    email:EmailStr
    firstname: str
    lastname: str
    avatar_uuid: Optional[str] = None
    status: str = Query(..., enum=[st.value for st in EmployeStatusEnum if st.value != EmployeStatusEnum.DELETED])
    model_config = ConfigDict(from_attributes=True)


class EmployeCreate(EmployeBase):
    team_uuid_tab: Optional[list[str]] = []
    nursery_uuid_tab: list[str]

class EmployeDelete(BaseModel):
    uuid:str
    nursery_uuid_tab: Optional[list[str]] = []
    team_uuid_tab: Optional[list[str]] = []



class EmployeUpdate(EmployeBase):
    uuid:str
    team_uuid_tab: Optional[list[str]] = []
    nursery_uuid_tab: list[str]


class EmployeSlim(EmployeBase):
    uuid:str
    avatar: Optional[File] = None

class EmployeeInDB(EmployeBase):
    uuid: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class TeamSlim(BaseModel):
    uuid: Optional[str] = None
    name: Optional[str] = None
    leader_uuid: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None 
    date_added: Optional[datetime] = None
    date_modified: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EmployeResponse(EmployeeInDB):
    avatar: Optional[File] = None
    teams : Optional[list[TeamSlim]] = []
    
class EmployeResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data:list[EmployeResponse] =[]

    model_config = ConfigDict(from_attributes=True)

