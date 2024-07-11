import hashlib
import os
import uuid
from base64 import b64decode
from mimetypes import MimeTypes
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.main.core.config import Config
from app.main.models.storage import Storage
from app.main.utils.uploads import upload_file

CHUNK_SIZE = 1024 * 1024  # adjust the chunk size as desired


def convert_data(file_name):
    with open(file_name, 'rb') as file:
        binary_data = file.read()
    return binary_data


def hash_files(filename: str):
    file = filename  # Location of the file (can be set a different way)
    block_size = 65536  # The size of each read from the file

    # Create the hash object, can use something other than `.sha256()` if you wish
    file_hash = hashlib.sha256()
    with open(file, 'rb') as f:  # Open the file to read it's bytes
        # Read from the file. Take in the amount declared above
        fb = f.read(block_size)
        while len(fb) > 0:  # While there is still data being read from the file
            file_hash.update(fb)  # Update the hash
            fb = f.read(block_size)  # Read the next block from the file
    print(file_hash.hexdigest())  # Get the hexadecimal digest of the hash
    return file_hash.hexdigest()


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


class FileUtils(object):
    def __init__(self, my_file: UploadFile = None, base64: str = None, streaming_content: any = None, name: str = None):
        if (not my_file and not base64 and not streaming_content) or (my_file and base64 and streaming_content):
            raise Exception("Provide only file or base64 or streaming content")
        if base64:
            if len(base64.split(",")) != 2:
                raise Exception("Invalid base 64")
            info = base64.split(",")[0].split(";")[0].split(":")[1]
            uuid_file_name = uuid.uuid1()
            self.blob_name = "{}{}".format(uuid_file_name,
                                           "-{}".format(name.replace(" ", "-")) if name else ".{}".format(
                                               info.split("/")[1]))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            self.mimetype = info
            byte = b64decode(base64.split(",")[1], validate=True)
            print(f"...................print image:{self.path_file}")
            try:
                print(f"...................try_upload:{self.path_file}")
                f = open(self.path_file, 'wb')
                f.write(byte)
                f.close()
            except OSError as error:
                print(f"...................image:{self.path_file}")
                print(f"....................the error: {error}")
                print(f"...............No mimetype")
                file_ext = name.rsplit('.', 1)[1] if name else info.split("/")[1]
                print(f"...............No mimetype :{file_ext}")
                self.blob_name = f"{uuid_file_name}.{file_ext}"
                self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
                f = open(self.path_file, 'wb')
                f.write(byte)
                f.close()
            except Exception as e:
                raise Exception(f"Error in upload file: {str(e)}")

        elif my_file:
            self.blob_name = "{}-{}".format(uuid.uuid1(), my_file.filename.replace(" ", "-"))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            with open(self.path_file, 'wb') as out_file:
                contents = my_file.file.read()
                out_file.write(contents)
            self.mimetype = my_file.content_type

        else:
            uuid_file_name = uuid.uuid1()
            self.blob_name = "{}{}".format(uuid_file_name, "-{}".format(name.replace(" ", "-")))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            # stream.stream_response_to_file(streaming_content, path=self.path_file)

            self.mimetype = MimeTypes().guess_type(os.path.basename(self.path_file))[0]
            if not self.mimetype:
                # print("...............No mimetype")
                file_ext = name.rsplit('.', 1)[1]
                if file_ext and file_ext.lower() == "msg":
                    self.mimetype = "application/octet-stream"
                if file_ext and file_ext.lower() == "docx":
                    self.mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if file_ext and file_ext.lower() == "doc":
                    self.mimetype = "application/msword"

        self.size = os.stat(self.path_file).st_size
        self.is_image = False
        self.thumbnail = {}
        self.medium = {}
        self.width = 0
        self.height = 0
        if self.mimetype.split("/")[0] in ["image"]:
            self.is_image = True

    def __repr__(self):
        return '<FileUtils: blob_name: {} path_file: {} mimetype: {} is_image: {} width: {} height: {}/>'.format(
            self.blob_name, self.path_file, self.mimetype, self.is_image, self.width, self.height)

    def save(self, db: Session):

        url, test = upload_file(self.path_file, self.blob_name, content_type=self.mimetype)
        os.remove(self.path_file)

        if "file_name" in self.thumbnail:
            url_thumbnail, test = upload_file(rreplace(self.path_file, '.', '_thumbnail.', 1),
                                              self.thumbnail["file_name"], content_type=self.mimetype)
            self.thumbnail["url"] = url_thumbnail
            os.remove(rreplace(self.path_file, '.', '_thumbnail.', 1))

        if "file_name" in self.medium:
            url_medium, test = upload_file(rreplace(self.path_file, '.', '_medium.', 1), self.medium["file_name"],
                                           content_type=self.mimetype)
            self.medium["url"] = url_medium
            os.remove(rreplace(self.path_file, '.', '_medium.', 1))

        db_obj = Storage(
            uuid=str(uuid.uuid4()),
            file_name=self.blob_name,
            url=url,
            width=self.width,
            height=self.height,
            size=self.size,
            thumbnail=self.thumbnail,
            medium=self.medium,
            mimetype=self.mimetype
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj
