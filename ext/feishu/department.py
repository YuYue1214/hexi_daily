# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹部门相关的组件及其方法

"""
import enum

import requests


class UserIdType(enum.Enum):
    OPEN_ID = 'open_id'
    USER_ID = 'user_id'


class DepartmentIdType(enum.Enum):
    DEPARTMENT_ID = 'department_id'
    OPEN_DEPARTMENT_ID = 'open_department_id'


def get_sub_departments(
        tenant_access_token: str,
        department_id: str,
        user_id_type: str = UserIdType.USER_ID.value,
        department_id_type: str = DepartmentIdType.DEPARTMENT_ID.value,
        fetch_child: bool = False,
        page_size: int = 10,
        page_token: str = '',
) -> requests.Response:
    """获取子部门列表

    参考 https://open.feishu.cn/document/server-docs/contact-v3/department/children

    :param tenant_access_token: 应用token
    :param department_id: 部门 ID, 根部门为0
    :param user_id_type: 返回值的用户 ID 类型
    :param department_id_type: 返回值的部门 ID 类型
    :param fetch_child: 是否递归获取子部门
    :param page_size: 分页大小
    :param page_token: 分页标记
    :return: 响应
    """
    return requests.get(
        url=f"https://open.feishu.cn/open-apis/contact/v3/departments/{department_id}/children",
        params={
            "department_id_type": department_id_type,
            "fetch_child": fetch_child,
            "page_size": page_size,
            "page_token": page_token,
            "user_id_type": user_id_type,
        },
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {tenant_access_token}'
        }
    )


class SubDepartmentsShortcut:
    """
    `获取子部门列表`响应的快捷方式

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
        """部门列表"""
        return self.data['items']


class SubDepartmentsItemShortcut:
    """
    `获取子部门列表`响应的快捷方式

    :param item: 源自jsn['data']['items'][i]
    """

    def __init__(self, item: dict):
        self.item = item

    @property
    def name(self) -> str | None:
        """部门名称"""
        return self.item.get('name')

    @property
    def department_id(self) -> str | None:
        """自定义部门 ID。后续可以使用该 ID 删除、修改、查询部门信息。"""
        return self.item.get('department_id')

    @property
    def open_department_id(self) -> str | None:
        """自定义部门 ID。后续可以使用该 ID 删除、修改、查询部门信息。"""
        return self.item.get('open_department_id')

    @property
    def parent_department_id(self) -> str | None:
        """父部门ID 当该员工所对应的部门没有出现'-'时需要去查找其父部门的相应信息"""
        return self.item.get('parent_department_id')
