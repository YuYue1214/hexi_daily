# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹token相关的组件及其方法

"""
import requests


def get_tenant_access_token(app_id: str, app_secret: str) -> requests.Response:
    """获取 tenant_access_token

    参考 https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal

    :param app_id: App ID
    :param app_secret: App Secret
    :return: 响应
    """
    return requests.post(
        url='https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={"app_id": app_id, "app_secret": app_secret},
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
