from minio import Minio

from minio.error import S3Error

from app.main.core.config import Config

minioClient = Minio(Config.MINIO_URL,
                    access_key=Config.MINIO_ACCESS_KEY,
                    secret_key=Config.MINIO_SECRET_KEY,
                    secure=Config.MINIO_SECURE)


def upload_file(path, file_name, content_type):
    try:
        minioClient.make_bucket(Config.MINIO_BUCKET)
    except S3Error as err:
        print(err)
        raise
    finally:
        # Upload the image
        try:
            minioClient.fput_object(Config.MINIO_BUCKET, file_name, path, content_type=content_type)
            url = minioClient.presigned_get_object(Config.MINIO_BUCKET, file_name)
            return Config.MINIO_API_URL + file_name, file_name
        except S3Error as err:
            return err


def get_file_url(file_name):
    try:
        return minioClient.presigned_get_object(Config.MINIO_BUCKET, file_name)
    except S3Error as err:
        print(err)
        return err
