# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹文件相关的组件及其方法

"""
import enum
import os.path

import requests


class FileType(enum.Enum):
    OPUS = 'opus'
    MP4 = 'mp4'
    PDF = 'pdf'
    DOC = 'doc'
    XLS = 'xls'
    PPT = 'ppt'
    STREAM = 'stream'


def upload_file(
        file: str | bytes,
        tenant_access_token: str,
        file_type: FileType,
        duration: int | None = None,
        file_name: str | None = None,
) -> requests.Response:
    """上传文件

    参考 https://open.feishu.cn/document/server-docs/im-v1/file/create

    :param file: str=本地文件绝对路径, bytes=文件流
    :param tenant_access_token: 应用token
    :param file_type: 文件类型
    :param duration: 文件的时长（视频、音频），单位：毫秒。不传值时无法显示文件的具体时长。
    :param file_name: 带后缀的文件名, file为str是为none，会默认取路径名；file为bytes时必传
    :return:
    :raises: FileNotFoundError,TypeError
    """
    payload = {'file_type': file_type.value}
    if duration:
        payload['duration'] = duration
    if file_name:
        payload['file_name'] = file_name

    if isinstance(file, str):
        if not (os.path.exists(file) and os.path.isfile(file)):
            raise FileNotFoundError(f'文件不存在: {file}')
        else:
            files = [('file', ('file', open(file, 'rb'), 'application/octet-stream'))]
            if file_name is None:
                payload['file_name'] = os.path.basename(file)
    elif isinstance(file, bytes):
        files = [('file', ('file', file, 'application/octet-stream'))]
        if file_name:
            payload['file_name'] = file_name
        else:
            raise TypeError('file为bytes时file_name为必传参数')
    else:
        raise TypeError('file参数类型错误')

    return requests.post(
        url='https://open.feishu.cn/open-apis/im/v1/files',
        headers={'Authorization': f'Bearer {tenant_access_token}'},
        data=payload,
        files=files
    )


class ResourceType(enum.Enum):
    IMAGE = 'image'
    FILE = 'file'


def download_resource(
        tenant_access_token: str,
        message_id: str,
        file_key: str,
        resource_type: str = ResourceType.FILE.value,
) -> requests.Response:
    """获取消息中的资源文件

    参考 https://open.feishu.cn/document/server-docs/im-v1/message/get-2

    :param tenant_access_token: 应用token
    :param message_id: 消息id
    :param file_key: 文件key
    :param resource_type: 资源类型
    :return: 响应
    """
    return requests.get(
        url=f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{file_key}?type={resource_type}",
        headers={'Authorization': f'Bearer {tenant_access_token}'}
    )


def upload_file_for_approval(
        tenant_access_token: str,
        file: str | bytes,
        file_name: str,
        file_type: str,
) -> requests.Response:
    """上传文件, 到审批系统

    参考 https://open.feishu.cn/document/server-docs/approval-v4/file/upload-files

    :param tenant_access_token: 应用token
    :param file: 文件内容
    :param file_name: 文件名
    :param file_type: 文件类型，image（图片） 或 attachment（附件）
    :return: 响应
    """
    if isinstance(file, str):
        if not (os.path.exists(file) and os.path.isfile(file)):
            raise FileNotFoundError(f'文件不存在: {file}')
        else:
            files = [('file', ('file', open(file, 'rb'), 'application/octet-stream'))]
    elif isinstance(file, bytes):
        files = [('file', ('file', file, 'application/octet-stream'))]
    else:
        raise TypeError('file参数类型错误')

    return requests.post(
        url='https://www.feishu.cn/approval/openapi/v2/file/upload',
        headers={'Authorization': f'Bearer {tenant_access_token}'},
        data={
            'name': file_name,
            'type': file_type
        },
        files=files
    )
