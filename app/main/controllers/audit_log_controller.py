from app.main.core.dependencies import get_db, TokenRequired
from app.main import crud, models, schemas
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/audit_logs", tags=["audit_logs"])


@router.get("", response_model=schemas.AuditLogList)
def get_all_audit_logs(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query("DESC", enum =["ASC","DESC"]),
    entity_id:Optional[str] = None,
    keyword:Optional[str] = None,
    order_filed: Optional[str] = "date_added",
    current_user: models.Owner = Depends(TokenRequired(roles =["owner"] ))
):
    
    """ Get all logs """

    return crud.audit_log.get_multi(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        entity_id=entity_id,
        order_filed=order_filed,
        keyword=keyword
    )
