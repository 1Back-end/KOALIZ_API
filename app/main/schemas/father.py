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


class FatherBase(BaseModel):
    email:EmailStr
    firstname: str
    lastname: str
    role_uuid:str

class FatherCreate(FatherBase):
    avatar_uuid:Optional[str] = None
    password:str

class FatherUpdate(BaseModel):
    uuid: str
    firstname: Optional[str]=None
    lastname: Optional[str]=None
    email: Optional[EmailStr]= None
    avatar_uuid: Optional[str]=None


class FatherDelete(BaseModel):
    uuid:str

class FatherResponse(FatherBase):
    uuid:str
    status:str
    avatar : Optional[Avatar] = None
    role: Roleslim
    added_by: Optional[AddedBy2] = None
    date_added: Any
    date_modified: Any

    model_config = ConfigDict(from_attributes=True)

class FatherResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[FatherResponse]

    model_config = ConfigDict(from_attributes=True)


class Father(BaseModel):
    uuid: Optional[str] = None
    email: EmailStr
    firstname: str
    lastname: str
    is_new_user: Optional[bool] = False
    avatar: Optional[File]= None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)


class FatherAuthentication(UserAuthentication):
    user: Father

    model_config = ConfigDict(from_attributes=True)
