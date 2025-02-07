from typing import Generator, Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException

from app.main import models, crud
from app.main.core.i18n import __
from app.main.core.security import decode_access_token


def get_db(request: Request) -> Generator:
    return request.state.db


class AuthUtils():

    @staticmethod
    def verify_jwt(token: str) -> bool:

        isTokenValid: bool = False

        try:
            payload = jwt.decode(
                token, Config.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
            return token_data
        except (jwt.InvalidTokenError, ValidationError) as e:
            print(e)
            payload = None

        if payload:
            isTokenValid = True
        return isTokenValid

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
        required_roles = set(self.roles)
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
                if "administrators" in code_groups and "owners" in code_groups:
                    current_user = (crud.owner.get_by_uuid(db=db, uuid=token_data["sub"]) or
                                    crud.administrator.get_by_uuid(db=db, uuid=token_data["sub"]))
                else:
                    if "administrators" in code_groups:
                        current_user = crud.administrator.get_by_uuid(db=db, uuid=token_data["sub"])
                    elif "owners" in code_groups:
                        current_user = crud.owner.get_by_uuid(db=db, uuid=token_data["sub"])
                    elif "parents" in code_groups:
                        current_user = crud.parent.get_by_uuid(db=db, uuid=token_data["sub"])

            else:
                current_user = crud.administrator.get_by_uuid(db=db, uuid=token_data["sub"])
                if not current_user:
                    owner = crud.owner.get_by_uuid(db=db, uuid=token_data["sub"])
                    parent = crud.parent.get_by_uuid(db=db, uuid=token_data["sub"])  
                    current_user = owner if owner else parent

            if not current_user:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            if current_user.status != models.UserStatusType.ACTIVED:
                print("-------------",current_user)
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


class TeamTokenRequired(HTTPBearer):

    def __init__(self, roles: list = [], token: Optional[str] = Query(None), auto_error: bool = True):
        self.token = token
        self.roles = roles
        super(TeamTokenRequired, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(TeamTokenRequired, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))
            token_data = decode_access_token(credentials.credentials)
            if not token_data:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            if models.BlacklistToken.check_blacklist(db, credentials.credentials):
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            current_team_device = crud.team_device.get_by_team_device_uuid(db=db, device_uuid=token_data["sub"])
            if not current_team_device:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            return current_team_device
        else:
            raise HTTPException(status_code=403, detail=__("dependencies-access-unauthorized"))
        db.close()

class SocketTokenRequired(HTTPBearer):

    def __init__(self, token: str, roles: list = [], auto_error: bool = True):
        self.roles = roles
        self.token = token
        super(SocketTokenRequired, self).__init__(auto_error=auto_error)

    async def __call__(self, db: Session, ):
        required_roles = self.roles
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token)

        if credentials:
            if not credentials.scheme == "Bearer":
                return False

            token_data = AuthUtils.verify_jwt(credentials.credentials)
            if not token_data:
                return False

            if models.BlacklistToken.check_blacklist(db, credentials.credentials):
                return False

            current_user = crud.administrator.get_by_uuid(db=db, uuid=token_data.sub)
            if not current_user:
                owner = crud.owner.get_by_uuid(db=db, uuid=token_data.sub)
                parent = crud.parent.get_by_uuid(db=db, uuid=token_data.sub)
                current_user = owner if owner else parent

            if not current_user:
                return False

            if required_roles:
                if not AuthUtils.verify_role(roles=required_roles, user=current_user):
                    return False
            return current_user
        else:

            return False