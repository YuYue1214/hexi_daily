import enum
import mimetypes
from io import BytesIO

import boto3
from botocore.client import BaseClient, Config
from botocore.exceptions import ClientError

__all__ = [
    'ContentType', 'OSS'
]


def _client(access_key: str, secret_key: str, endpoint: str) -> BaseClient:
    """
    获取client实例
    :return:
    """
    session: boto3.Session = boto3.session.Session()
    client: BaseClient = session.client(
        service_name='s3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint,
        config=Config(
            signature_version='s3v4',
            connect_timeout=180,
            read_timeout=180,
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
    )
    return client


class ContentType(enum.Enum):
    TEXT = 'text/plain'
    PNG = 'image/png'
    JPEG = 'image/jpeg'
    JSON = 'application/json'
    BINARY = 'binary/octet-stream'
    XML = 'application/xml'
    CSV = 'text/csv'
    HTML = 'text/html'
    MP4 = 'video/mp4'
    AVI = 'video/x-msvideo'
    MOV = 'video/quicktime'
    WEBM = 'video/webm'
    # 通用视频类型
    GENERIC_VIDEO = 'video/*'


class OSS:
    """
    oss操作

    oss参数样例
        access_key: "xxxx"
        secret_key: "xxxxxxx"
        endpoint: "https://oss.fandow.com/"
        bucket: "public-sentiment-analysis"
    """

    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint: str,
            bucket: str,
    ):
        self.endpoint = endpoint.strip('/')
        self.bucket = bucket.strip('/')
        self._client = _client(access_key, secret_key, endpoint)
        pass

    def upload(self, key: str, path: str, typ: ContentType | None = None) -> str:
        """
        上传文件到oss
        :param key: 指定上传后的key
        :param path: 本地文件路径
        :param typ: 文件类型
        :return:
        """
        if typ is not None:
            content_type = typ.value
        else:
            content_type, _ = mimetypes.guess_type(path)
            if content_type is None:
                content_type = 'application/octet-stream'

        self._client.upload_file(path, self.bucket, key, ExtraArgs={'ContentType': content_type})
        return f"{self.endpoint}/{self.bucket}/{key}"

    def url(self, key: str) -> str:
        """
        组装oss全链接
        :param key:
        :return:
        """
        return f"{self.endpoint}/{self.bucket}/{key}"

    def download(self, key: str, path: str) -> None:
        """
        下载文件
        :param key: 在桶中的文件名
        :param path:
        :return:
        """
        self._client.download_file(self.bucket, key, path)

    def exist(self, key: str) -> bool:
        """
        查询桶内是否存在该文件
        :param key:
        :return:
        """
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def download_as_bytes(self, key: str) -> BytesIO:
        """
        下载指定key的文件，以字节流的形式
        :param key:
        :return:
        """
        obj: BytesIO = BytesIO()
        self._client.download_fileobj(self.bucket, key, obj)
        return obj

    def upload_as_bytes(self, key: str, data: BytesIO, typ: ContentType | str = ContentType.BINARY) -> str:
        """
        上传字节流
        :param key:
        :param data:
        :param typ:
        :return:
        """
        if isinstance(typ, ContentType):
            typ = typ.value
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=typ
        )
        return self.url(key)
