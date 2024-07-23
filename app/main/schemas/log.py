from typing import Optional, Any

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.main.schemas.user import AddedBy


class LogSchema(BaseModel):
    uuid: str
    before_details: Any
    after_details: Any
    added_by: Optional[AddedBy]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)