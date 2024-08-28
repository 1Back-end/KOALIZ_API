from typing import Any

from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

from app.main import schemas, crud, models
from app.main.core import dependencies
from app.main.core.dependencies import TokenRequired
from app.main.utils.uploads import get_file_url
from starlette.responses import RedirectResponse
from app.main.core.i18n import __


router = APIRouter(
    prefix="/storages",
    tags=["storages"]
)


@router.post("/upload", status_code=200)
def upload_file(
        *,
        db: Session = Depends(dependencies.get_db),
        obj_in: schemas.FileUpload = Body(...),
        current_user=Depends(TokenRequired())


) -> Any:
    """
    Upload a file.
    """

    # Check if file is a good base 64
    if obj_in.base_64 and len(obj_in.base_64.split(",")) != 2:
        raise HTTPException(
            status_code=400,
            detail=__("Invalid-image")
        )

    # Get file and store it to database
    storage = crud.storage.store_file(db=db, base_64=obj_in.base_64, name=obj_in.file_name)
    return {"url": storage.url, "uuid": storage.uuid, "file_name": storage.file_name, "minio_file_name": storage.minio_file_name}


@router.get("/get/{file_name}", status_code=200)
def get_file(
        file_name: str,
) -> Any:
    """
    Get file from S3
    """
    try:
        url = get_file_url(file_name)
        print(url)
        return RedirectResponse(url=url)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=404,
            detail=__("file-not-found")
        )
