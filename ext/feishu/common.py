# -*- coding: utf-8 -*-
"""
@Author   : xwq
@Desc     : 统筹部分通用组件及其方法

"""


def compose_headers(tenant_access_token: str) -> dict[str, str]:
    """组合请求头

    :param tenant_access_token:
    :return:
    """
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}'
    }
