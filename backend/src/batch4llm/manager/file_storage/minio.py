from datetime import timedelta
from io import BytesIO
from typing import List, BinaryIO
from urllib.parse import urlparse, urlunparse

from minio import Minio
from .base import FileStorage


class MinIOStorage(FileStorage):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
        public_url: str | None = None,
    ):
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.bucket_name = bucket_name

        if public_url:
            parsed = urlparse(public_url)
            self._presign_client = Minio(
                parsed.netloc,
                access_key=access_key,
                secret_key=secret_key,
                secure=(parsed.scheme == "https"),
            )
            # MinIO always uses us-east-1; pre-populate the region cache so
            # the client doesn't make a real HTTP call to the public host.
            self._presign_client._region_map[bucket_name] = "us-east-1"
            self._presign_path_prefix = parsed.path.rstrip("/")
        else:
            self._presign_client = self.client
            self._presign_path_prefix = ""

        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload(self, file_path: str, content: BinaryIO, length: int = -1) -> bool:
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=content,
                length=length,
                part_size=10 * 1024 * 1024,
            )
            return True
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def download(self, file_path: str) -> BinaryIO:
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return BytesIO(response.read())
        except Exception as e:
            print(f"Download error: {e}")
            raise
        finally:
            response.close()
            response.release_conn()

    def delete(self, file_path: str) -> bool:
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def exists(self, file_path: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, file_path)
            return True
        except Exception:
            return False

    def list(self, prefix: str = "") -> List[str]:
        try:
            objects = self.client.list_objects(
                self.bucket_name, prefix=prefix, recursive=True
            )
            return [obj.object_name for obj in objects]
        except Exception as e:
            print(f"List error: {e}")
            return []

    def get_file_url(
        self,
        file_path: str,
        expires: timedelta = timedelta(hours=1),
        mime_type: str | None = None,
    ) -> str:
        response_headers = {"response-content-disposition": "inline"}
        if mime_type:
            response_headers["response-content-type"] = mime_type
        url = self._presign_client.presigned_get_object(
            self.bucket_name,
            file_path,
            expires=expires,
            response_headers=response_headers,
        )
        if self._presign_path_prefix:
            parsed = urlparse(url)
            url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    self._presign_path_prefix + parsed.path,
                    "",
                    parsed.query,
                    "",
                )
            )
        return url
