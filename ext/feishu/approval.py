# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹审批相关的组件及其方法

"""
import enum
import json

import requests


def get_approval_definition(
        tenant_access_token: str,
        approval_code: str,
        locale: str = "zh-CN",
        user_id_type: str = 'user_id',
        with_admin_id: bool = False,
):
    """查看指定审批定义

    参考 https://open.feishu.cn/document/server-docs/approval-v4/approval/get

    :param tenant_access_token: 应用token
    :param approval_code: 审批定义 Code
    :param locale: 语言可选值，默认为审批定义配置的默认语言
    :param user_id_type: 用户 ID 类型
    :param with_admin_id: 是否返回有数据管理权限的审批流程管理员 ID 列表（即响应参数 approval_admin_ids）
    :return:
    """
    return requests.get(
        url=f"https://open.feishu.cn/open-apis/approval/v4/approvals/{approval_code}",
        params={
            'locale': locale,
            'user_id_type': user_id_type,
            'with_admin_id': with_admin_id,
        },
        headers={'Authorization': f'Bearer {tenant_access_token}'}
    )


def create_feishu_approval_instance(token: str, approval_code: str, user_id: str, form_data: list):
    """
    创建飞书审批实例

    :param token: 飞书 tenant_access_token（字符串）
    :param approval_code: 审批模板 code
    :param user_id: 发起审批的用户 user_id
    :param form_data: 表单数据（Python 列表）
    :return: 接口响应对象
    """
    url = "https://open.feishu.cn/open-apis/approval/v4/instances"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    form_str = json.dumps(form_data)

    payload = {
        "approval_code": approval_code,
        "form": form_str,
        "user_id": user_id
    }

    response = requests.post(url, headers=headers, json=payload)
    return response


def cancel_feishu_approval_instance(token, approval_code, instance_code, user_id):
    """
    撤销（取消）飞书审批实例

    :param token: 飞书 tenant_access_token（字符串）
    :param approval_code: 审批模板 code
    :param instance_code: 审批实例 code
    :param user_id: 操作用户 user_id
    :return: 接口响应对象
    """
    url = "https://open.feishu.cn/open-apis/approval/v4/instances/cancel?user_id_type=user_id"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "approval_code": approval_code,
        "instance_code": instance_code,
        "user_id": user_id
    }

    response = requests.post(url, headers=headers, json=payload)
    return response


def get_feishu_approval_instance(token, instance_code, locale="zh-CN", user_id_type="user_id"):
    """
    查询飞书审批实例详情

    :param token: 飞书 tenant_access_token（字符串）
    :param instance_code: 审批实例 code
    :param locale: 语言（默认 zh-CN）
    :param user_id_type: 用户 ID 类型（默认 user_id）
    :return: 接口响应对象
    """
    url = f"https://open.feishu.cn/open-apis/approval/v4/instances/{instance_code}"
    params = {
        "locale": locale,
        "user_id_type": user_id_type
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers, params=params)
    return response


class ApprovalInstanceStatusEnum(enum.Enum):
    """审批实例状态"""
    PENDING = {'key': 'PENDING', 'value': '审批中'}
    APPROVED = {'key': 'APPROVED', 'value': '通过'}
    REJECTED = {'key': 'REJECTED', 'value': '拒绝'}
    CANCELED = {'key': 'CANCELED', 'value': '撤回'}
    FAILED = {'key': 'DELETED', 'value': '删除'}

    @classmethod
    def get_value(cls, key: str) -> str:
        """根据key返回中文value"""
        for item in cls:
            if item.value['key'] == key:
                return item.value['value']
        return '未知状态'


class ApprovalInstanceShortCut:
    """
    `获取审批实例`响应的快捷方式

    :param data: 源自jsn['data']
    """

    def __init__(self, data: dict):
        self.data = data

    @property
    def status(self) -> str:
        """审批实例状态"""
        return self.data['status']
