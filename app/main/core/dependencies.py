from typing import Generator, Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, BackgroundTasks

from app.main import models, crud
from app.main.core.i18n import __
from app.main.core.security import decode_access_token


def get_db(request: Request) -> Generator:
    return request.state.db


class AuthUtils():
    @staticmethod
    def verify_role(roles, user) -> bool:
        has_a_required_role = False
        if user.role_uuid:
            if isinstance(roles, str):
                if roles.lower() == user.role.code.lower():
                    has_a_required_role = True
            else:
                for role in roles:
                    if role.lower() == user.role.code.lower():
                        has_a_required_role = True
                        break
        return has_a_required_role


class TokenRequired(HTTPBearer):

    def __init__(self, token: Optional[str] = Query(None), roles=None, auto_error: bool = True, let_new_user: bool = False):
        if roles is None:
            roles = []
        elif isinstance(roles, str):
            roles = [roles]
        self.roles = roles
        self.token = token
        self.let_new_user = let_new_user
        super(TokenRequired, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        required_roles = self.roles
        code_groups = []
        for required_role in required_roles:
            code_group = crud.role.get_by_code(db=db, code=required_role)
            if code_group:
                code_groups.append(code_group.group)
        credentials: HTTPAuthorizationCredentials = await super(TokenRequired, self).__call__(request)

        if not credentials and self.token:
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))
            token_data = decode_access_token(credentials.credentials)
            if not token_data:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            if models.BlacklistToken.check_blacklist(db, credentials.credentials):
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            current_user = None
            if code_groups:
                if "administrators" in code_groups:
                    current_user = crud.administrator.get_by_uuid(db=db, uuid=token_data["sub"])
                else:
                    current_user = crud.user.get_by_uuid(db=db, uuid=token_data["sub"])

            else:
                current_user = crud.administrator.get_by_uuid(db=db, uuid=token_data["sub"])
                if not current_user:
                    current_user = crud.user.get_by_uuid(db=db, uuid=token_data["sub"])

            if not current_user:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            if current_user.status != models.UserStatusType.ACTIVED:
                raise HTTPException(status_code=405, detail=__("user-not-active"))

            if current_user.is_new_user and not self.let_new_user:
                raise HTTPException(status_code=403, detail=__("change-password-required"))

            if required_roles:
                if not AuthUtils.verify_role(roles=required_roles, user=current_user):
                    raise HTTPException(status_code=403,
                                        detail=__("dependencies-access-unauthorized"))

            return current_user
        else:
            raise HTTPException(status_code=403, detail=__("dependencies-access-unauthorized"))
        db.close()
