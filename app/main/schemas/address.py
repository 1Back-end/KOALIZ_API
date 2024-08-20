from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AddressBase(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    zipcode: str
    country: str
    apartment_number: Optional[str] = None
    additional_information: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Address(AddressBase):
    uuid: str
    date_added: datetime
    date_modified: datetime


class AddressCreate(AddressBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class AddressUpdate(AddressCreate):
    pass

class AddressSLim(BaseModel):
    uuid: str
    street: str
    city: str
    state: Optional[str] = None
    zipcode: str
    country: str
    
    model_config = ConfigDict(from_attributes=True)





