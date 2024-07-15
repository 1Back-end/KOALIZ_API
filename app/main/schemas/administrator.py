from typing import Optional,Any
from pydantic import BaseModel,ConfigDict,EmailStr
import datetime

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
    password:str

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
    avatar : Optional[Avatar] = None
    role: Roleslim
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





