from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


router = APIRouter(prefix="/helper", tags=["helpers"])

@router.get("/roles", response_model=list[schemas.RoleSchema])
async def get_roles(
    *,
    group: str = None,
    db: Session = Depends(get_db),
    # current_user=Depends(TokenRequired())
) -> list:
    """
    Roles
    """
    return crud.role.get_all(db, group)

@router.get("/meeting-types", response_model=list[schemas.MeetingTypeResponse])
async def get_meeting_types(
    *,
    db: Session = Depends(get_db),
    # current_user=Depends(TokenRequired())
) -> list:
    """
    meeting types
    """
    return db.query(models.MeetingType).all()

@router.get("/activity-reminder-types", response_model=list[schemas.ActivityReminderTypeResponse])
async def get_activity_reminder_types(
    *,
    db: Session = Depends(get_db),
    # current_user=Depends(TokenRequired())
) -> list:
    """
    activity reminder types
    """
    return db.query(models.ActivityReminderType).all()

@router.get("/membership-types", response_model=list[schemas.MembershipTypeSlim])
async def get_membership_types(
    *,
    db: Session = Depends(get_db),
    # current_user=Depends(TokenRequired())
) -> list:
    """
    Membership types
    """
    return crud.membership.get_membership_type(db)

@router.get("/enums", response_model=dict)
async def get_enums(
        *,
        db: Session = Depends(get_db),
        # current_user=Depends(TokenRequired())
) -> dict:
    """
    Enum
    """

    return {
        "status": [t.name for t in models.UserStatusType],
        "gender": [t.name for t in models.Gender],
        "parent_relationship": [t.name for t in models.ParentRelationship],
        "cleanliness": [t.name for t in models.Cleanliness],
        "stool_type": [t.name for t in models.StoolType],
        "additional_care": [t.name for t in models.AdditionalCare],
        "care_type": [t.name for t in models.CareType],
        "medication_type": [t.name for t in models.MedicationType],
        "route": [t.name for t in models.Route],
        "quality": [t.name for t in models.NapQuality],
        "meal_quality": [t.name for t in models.MealQuality],
        # "sites": sites,
        # "groups": groups,
        # "project_status": ["OPEN", "BREAK", "SUFFERING", "CLOSE", "ARCHIVED", "DELETED", "DONE"],
        # "task_status": ["OPEN", "ACCEPTED", "SUFFERING", "REJECTED", "DELETED", "DONE", "IN_PROGRESS", "DUE_THIS_WEEK"],
        # "task_document_status": ["HIDE","DELETED", "AWAITING", "ACCEPTED", "REJECTED"],
        # "reminders": ["2_days_before","1_week_before", "2_week_before", "3_week_before", "4_week_before", "6_week_before"]
    }

