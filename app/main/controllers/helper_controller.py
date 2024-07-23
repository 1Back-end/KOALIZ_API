from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


router = APIRouter(prefix="/helper", tags=["helpers"])


@router.get("/roles", response_model=list[schemas.RoleSchema])
async def get_roles(
    *,
    group: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(TokenRequired())
) -> list:
    """
    Default data form.
    """
    return crud.role.get_all(db, group)

    # return {
    #     "roles": roles,
    #     "questions": questions,
    #     "status": [t.name for t in models.UserStatusType],
    #     "sites": sites,
    #     "groups": groups,
    #     "project_status": ["OPEN", "BREAK", "SUFFERING", "CLOSE", "ARCHIVED", "DELETED", "DONE"],
    #     "task_status": ["OPEN", "ACCEPTED", "SUFFERING", "REJECTED", "DELETED", "DONE", "IN_PROGRESS", "DUE_THIS_WEEK"],
    #     "task_document_status": ["HIDE","DELETED", "AWAITING", "ACCEPTED", "REJECTED"],
    #     "reminders": ["2_days_before","1_week_before", "2_week_before", "3_week_before", "4_week_before", "6_week_before"]
    # }
    #
