from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main.models import Storage, User
import uuid
from app.main.schemas import FileAdd, File
from app.main.utils.file import FileUtils
from app.main import crud


class CRUDFile(CRUDBase[File, User, FileAdd]):

    def store_file(self, db: Session, *, base_64: Any, name: str=None) -> Storage:
        try:

            file_manager = FileUtils(base64=base_64, name=name)
            storage = file_manager.save(db=db)
            return storage
        except Exception as e:
            print(str(e))
            db.rollback()

    def add_file(self, db: Session, *, obj_in: Any) -> User:
        try:

            user = crud.user.get_by_user_uuid(db, uuid=obj_in['uuid'])

            file_manager = FileUtils(base64=obj_in['base_64'])
            storage = file_manager.save(db=db)
            user.avatar_uuid = storage.uuid

            db.commit()
            db.refresh(user)

            return user
        except Exception as e:
            print(str(e))
            db.rollback()

    def real_file_add(self, db: Session, *, file: Any) -> Storage:
        try:

            file_manager = FileUtils(myfile=file)
            return file_manager.save(db=db)
        except Exception as e:
            print(str(e))
            db.rollback()


    def store_file_by_url(self, db: Session, *, url: str) -> Storage:

        file_manager = FileUtils(url=url)
        storage = file_manager.save(db=db)
        return storage

storage = CRUDFile(Storage)
