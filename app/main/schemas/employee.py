from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr,ConfigDict
from .file import File

class EmployeBase(BaseModel):
    email:EmailStr
    firstname: str
    lastname: str
    avatar_uuid: Optional[str] = None
    team_uuid_tab: Optional[list[str]] = []
    nursery_uuid: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class EmployeCreate(EmployeBase):
    pass
    

class EmployeUpdate(EmployeCreate):
    uuid:str

class EmployeSlim(EmployeBase):
    pass

class EmployeeInDB(EmployeBase):
    uuid: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)


class EmployeResponse(EmployeeInDB):
    avatar: Optional[File] = None

class EmployeResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data:list[EmployeResponse] =[]

    model_config = ConfigDict(from_attributes=True)

