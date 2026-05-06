# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹图片相关的组件及其方法

"""
import enum
import os.path

import requests


class ImageType(enum.Enum):
    # 用于发送消息
    MESSAGE = 'message'
    # 用于设置头像
    AVATAR = 'avatar'


def upload_image(
        image: str | bytes,
        tenant_access_token: str,
        image_type: ImageType = ImageType.MESSAGE,
) -> requests.Response:
    """上传图片

    参考 https://open.feishu.cn/document/server-docs/im-v1/image/create

    :param image: str=本地图片绝对路径,
    :param tenant_access_token: 应用token
    :param image_type: 图片类型
    :return:
    :raises: FileNotFoundError,TypeError
    """
    if isinstance(image, str):
        if not (os.path.exists(image) and os.path.isfile(image)):
            raise FileNotFoundError(f'图片文件不存在: {image}')
        else:
            files = [('image', ('file', open(image, 'rb'), 'application/octet-stream'))]
    elif isinstance(image, bytes):
        files = [('image', ('file', image, 'application/octet-stream'))]
    else:
        raise TypeError('image参数类型错误')
    return requests.post(
        url='https://open.feishu.cn/open-apis/im/v1/images',
        headers={'Authorization': f'Bearer {tenant_access_token}'},
        data={'image_type': image_type.value},
        files=files
    )
