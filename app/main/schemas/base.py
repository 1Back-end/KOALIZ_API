

from pydantic import BaseModel, ConfigDict, RootModel
from typing import Any, List, Optional, Dict

class Items(RootModel):
    root: Dict[str, Any]

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserAuthentication(BaseModel):
    user: Any
    token: Optional[Token] = None
    model_config = ConfigDict(from_attributes=True)


class DataList(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int
    data: List[Any] = []

    model_config = ConfigDict(from_attributes=True)

