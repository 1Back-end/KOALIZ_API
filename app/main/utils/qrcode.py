import qrcode
import os
import uuid
from app.main.models.storage import Storage
from app.main.core.config import Config
from PIL import Image
from base64 import b64decode
from app.main.utils.uploads import upload_file
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.main.core.i18n import t, get_language

def rreplace(s, old, new, occurrence):
  li = s.rsplit(old, occurrence)
  return new.join(li)

class CreateQrcode(object):

    def __init__(self, code: str):

        qr = qrcode.QRCode(version=6, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        self.blob_name = "{}-qrcode.png".format(uuid.uuid1())
        self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
        img.save(self.path_file)
        self.mimetype = "image/png"

        self.size = os.stat(self.path_file).st_size
        self.is_image = True
        self.thumbnail = {}
        self.medium = {}
        self.width = 0
        self.height = 0


    def __repr__(self):
        return '<CreateQrcode: blob_name: {} path_file: {} mimetype: {} is_image: {} width: {} height: {}/>'.format(self.blob_name, self.path_file, self.mimetype, self.is_image, self.width, self.height)

    def __generate_cropped_image(self):

      #medium size
      self.image_pillow.thumbnail((Config.IMAGE_MEDIUM_WIDTH, Config.IMAGE_MEDIUM_WIDTH), Image.ANTIALIAS)
      self.image_pillow.save(rreplace(self.path_file, '.', '_medium.', 1))
      self.medium = {
        "width": self.image_pillow.size[0],
        "height": self.image_pillow.size[1],
        "size":  os.stat(rreplace(self.path_file, '.', '_medium.', 1)).st_size,
        "url": "",
        "file_name": rreplace(self.blob_name, '.', '_medium.', 1) 
      }  

      #Thumbnail
      self.image_pillow.thumbnail((Config.IMAGE_THUMBNAIL_WIDTH, Config.IMAGE_THUMBNAIL_WIDTH), Image.ANTIALIAS)
      self.image_pillow.save(rreplace(self.path_file, '.', '_thumbnail.', 1))
      self.thumbnail = {
        "width": self.image_pillow.size[0],
        "height": self.image_pillow.size[1],
        "size":  os.stat(rreplace(self.path_file, '.', '_thumbnail.', 1)).st_size,
        "url": "",
        "file_name": rreplace(self.blob_name, '.', '_thumbnail.', 1) 
      }  


    def __get_image_info(self):
      self.image_pillow = Image.open(r"{}".format(self.path_file))
      self.width, self.height = self.image_pillow.size 

    def save(self, db: Session):
      print(self.is_image)
      if self.is_image:
        self.__get_image_info()
        self.__generate_cropped_image()

      url, minio_file_name, test = upload_file(self.path_file, self.blob_name, content_type=self.mimetype)
      os.remove(self.path_file)

      if "file_name" in self.thumbnail:
        url_thumbnail, test = upload_file(rreplace(self.path_file, '.', '_thumbnail.', 1), self.thumbnail["file_name"], content_type=self.mimetype)
        self.thumbnail["url"] = url_thumbnail
        os.remove(rreplace(self.path_file, '.', '_thumbnail.', 1))

      if "file_name" in self.medium:
        url_medium, minio_file_name, test = upload_file(rreplace(self.path_file, '.', '_medium.', 1), self.medium["file_name"], content_type=self.mimetype)
        self.medium["url"] = url_medium
        os.remove(rreplace(self.path_file, '.', '_medium.', 1))

      storage = Storage(
        file_name=self.blob_name,
        url=url,
        mimetype=self.mimetype,
        width=self.width,
        height=self.height,
        size=self.size,
        thumbnail=self.thumbnail,
        medium=self.medium,
        uuid=str(uuid.uuid4())
      )
      db.add(storage)
      db.commit()

      return storage