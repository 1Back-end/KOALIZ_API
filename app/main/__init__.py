import os
import secrets
import time

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.main.controllers.router import api_router
from app.main.core.config import Config
from app.main.core.i18n import add_process_language_header
from app.main.core.security import decode_access_token
from app.main.models.db.session import SessionLocal
from app.main.schedulers import scheduler


security = HTTPBasic()

protocol = HTTPBearer(auto_error=False, scheme_name="Bearer")

description = '''This is BDE MICRO CRECHE API. All request in regards to the application can be found here,
    in general most of the methods require you being as an active user to be able to access
'''

app = FastAPI(
    title=Config.PROJECT_NAME,
    description=description,
    version=f"{Config.PROJECT_VERSION}",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.include_router(api_router, prefix=Config.API_STR)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(EventHandlerASGIMiddleware, handlers=[local_handler])
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_language_header)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, Config.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, Config.ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get(f"{Config.API_STR}/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url=f"{Config.API_STR}/openapi.json", title="docs")


@app.get(f"{Config.API_STR}/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url=f"{Config.API_STR}/openapi.json", title="docs")


@app.get(f"{Config.API_STR}/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes, description=app.description)


app.add_middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)+ " s"
    return response


@app.get(f"/", response_class=HTMLResponse)
async def welcome():
    with open('{}/app/main/templates/html/index.html'.format(os.getcwd())) as f:
        return str(f.read())


@app.on_event("startup")
def startup_event():
    scheduler.start()
