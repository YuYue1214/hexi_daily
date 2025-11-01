# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹user相关的组件及其方法

"""
import enum
from typing import Any

import requests

from .common import compose_headers


class UserIdType(enum.Enum):
    OPEN_ID = 'open_id'
    USER_ID = 'user_id'


class DepartmentIdType(enum.Enum):
    DEPARTMENT_ID = 'department_id'
    OPEN_DEPARTMENT_ID = 'open_department_id'


def get_user(
        tenant_access_token: str,
        user_id: str,
        user_id_type: str = UserIdType.USER_ID.value,
        department_id_type: str = DepartmentIdType.DEPARTMENT_ID.value,
) -> requests.Response:
    """获取单个用户信息

    参考 https://open.feishu.cn/document/server-docs/contact-v3/user/get

    :param tenant_access_token: token
    :param user_id: 用户id
    :param user_id_type: id类型
    :param department_id_type: 查询时的department_id的类型
    :return:
    """
    return requests.get(
        url=f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}",
        headers=compose_headers(tenant_access_token),
        params={
            'department_id_type': department_id_type,
            'user_id_type': user_id_type,
        }
    )


class UserShortcut:
    """
    获取用户信息的响应体的一些快捷方式

    :param dct: 如response.json()['data']['user']
    """

    def __init__(self, dct: dict[str, Any]):
        self._dct = dct

    @property
    def user_id(self) -> str:
        return self._dct['user_id']

    @property
    def name(self) -> str:
        return self._dct['name']

    @property
    def department_ids(self) -> list[str]:
        return self._dct['department_ids']


def get_users_from_dept(
        tenant_access_token: str,
        department_id: str,
        user_id_type: str = UserIdType.USER_ID.value,
        department_id_type: str = DepartmentIdType.DEPARTMENT_ID.value,
        page_size: int = 10,
        page_token: str = '',
) -> requests.Response:
    """获取部门直属用户列表

    参考 https://open.feishu.cn/document/server-docs/contact-v3/user/find_by_department

    :param tenant_access_token: 应用token
    :param department_id: 部门id
    :param user_id_type: 返回值的yoghurtid类型
    :param department_id_type: 传参的部门id类型
    :param page_size: 分页大小
    :param page_token: 分页标记
    :return: 响应
    """
    return requests.get(
        url="https://open.feishu.cn/open-apis/contact/v3/users/find_by_department",
        headers={
            "Authorization": f"Bearer {tenant_access_token}"
        },
        params={
            "department_id": department_id,
            "department_id_type": department_id_type,
            "page_size": page_size,
            "page_token": page_token,
            "user_id_type": user_id_type
        }
    )


class UsersFromDeptShortcut:
    """
    `获取部门直属用户列表`响应的快捷方式

    :param data: 源自jsn['data']
    """

    def __init__(self, data: dict):
        self.data = data

    @property
    def has_more(self) -> bool:
        """是否还有更多项"""
        return self.data['has_more']

    @property
    def page_token(self) -> str | None:
        """分页标记，当 has_more 为 true 时，会同时返回新的 page_token，否则不返回 page_token"""
        return self.data['page_token']

    @property
    def items(self) -> list[dict]:
        """用户信息列表"""
        return self.data['items']


class UsersFromDeptItemShortcut:
    """
    `获取部门直属用户列表`响应的快捷方式

    :param item: 源自jsn['data']['items'][i]
    """

    def __init__(self, item: dict):
        self.item = item

    @property
    def name(self) -> str | None:
        return self.item.get('name')

    @property
    def user_id(self) -> str | None:
        return self.item.get('department_id')

    @property
    def mobile(self) -> str | None:
        """手机号"""
        return self.item.get('mobile')

    @property
    def gender(self) -> int | None:
        """性别, 0保密1男2女3其他"""
        return self.item.get('gender')

    @property
    def employee_no(self) -> str | None:
        """工号"""
        return self.item.get('employee_no')

    @property
    def job_title(self) -> str | None:
        """职务"""
        return self.item.get('job_title')
