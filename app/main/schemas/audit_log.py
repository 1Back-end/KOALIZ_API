from typing import Optional, Any

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.main.schemas.base import DataList
from app.main.schemas.user import AddedBy


class AuditLogSchema(BaseModel):
    uuid: str
    entity_type: str
    entity_id: str
    action: str
    before_changes: Any
    after_changes: Any
    # performed_by: Optional[AddedBy]=None
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogCreate(BaseModel):
    before_changes: Any
    after_changes: Any
    entity_type: str
    entity_id: str
    action: str
    performed_by_uuid: str

    model_config = ConfigDict(from_attributes=True)


class AuditLogUpdate(AuditLogCreate):
    uuid: str

class AuditLogList(DataList):
    data: list[AuditLogSchema]

    model_config = ConfigDict(from_attributes=True)