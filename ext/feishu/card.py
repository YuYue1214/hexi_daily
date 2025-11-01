# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹卡片相关的组件及其方法

"""
import json

import requests


def patch_card(
        tenant_access_token: str,
        message_id: str,
        template_id: str,
        template_version_name: str,
        template_variable: dict[str, str] | None = None,
) -> requests.Response:
    """更新已发送的消息卡片

    参考 https://open.feishu.cn/document/server-docs/im-v1/message-card/patch

    :param tenant_access_token: 应用token
    :param message_id: 目标消息id
    :param template_id: 模板id
    :param template_version_name: 模板版本
    :param template_variable: 模板变量
    :return: 响应
    """
    return requests.patch(
        url=f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}",
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {tenant_access_token}',
        },
        json={
            'content': json.dumps({
                "type": "template",
                "data": {
                    "template_id": template_id,
                    "template_version_name": template_version_name,
                    "template_variable": template_variable or {}
                }
            })
        }
    )
