from typing import Optional,Any
from pydantic import BaseModel,ConfigDict,EmailStr
from datetime import datetime

from app.main.schemas.base import UserAuthentication
from app.main.schemas.file import File

class AddedBy2(BaseModel):
    uuid: str
    email: EmailStr
    firstname: Optional[str]
    lastname: str

    model_config = ConfigDict(from_attributes=True)

class Avatar(BaseModel):
    uuid:str
    file_name:str
    url:str
    mimetype:str
    width:int
    height:int
    size:int
    thumbnail:Any
    medium:Any
    date_added:Any
    date_modified:Any

class Roleslim(BaseModel):
    uuid:str
    title_fr:str
    title_en: str
    code:str

    model_config = ConfigDict(from_attributes=True)


class AdministratorBase(BaseModel):
    email:EmailStr
    firstname: str
    lastname: str
    role_uuid:str

class AdministratorCreate(AdministratorBase):
    avatar_uuid:Optional[str] = None
    # password:str

class AdministratorUpdate(AdministratorBase):
    uuid:str
    email:Optional[EmailStr]=None
    firstname: Optional[str]=None
    lastname: Optional[str]=None
    role_uuid: Optional[str]=None
    avatar_uuid: Optional[str]=None


class AdministratorDelete(BaseModel):
    uuid:str

class AdministratorResponse(AdministratorBase):
    uuid:str
    status:str
    avatar : Optional[Avatar] = None
    role: Roleslim
    added_by: Optional[AddedBy2] = None
    date_added: Any
    date_modified: Any

    model_config = ConfigDict(from_attributes=True)

class AdministratorResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[AdministratorResponse]

    model_config = ConfigDict(from_attributes=True)


class Administrator(BaseModel):
    uuid: Optional[str] = None
    email: EmailStr
    firstname: str
    lastname: str
    is_new_user: Optional[bool] = False
    avatar: Optional[File]
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class AdministratorAuthentication(UserAuthentication):
    user: Administrator

    model_config = ConfigDict(from_attributes=True)
