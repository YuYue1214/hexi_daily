# -*- coding: utf-8 -*-
"""
@Author   : hcq
@Desc     : 多维表格

"""
import requests
from typing import Any


def bitable_create_record(
        tenant_access_token: str,
        app_token: str,
        table_id: str,
        fields: dict[str, Any]
) -> requests.Response:
    """创建多维表格记录

    参考文档: https://open.feishu.cn/document/server-docs/bitable-v1/app-table-record/create

    :param tenant_access_token: tenant_access_token，如 t-g10462dQ2RU6GPHNQPRWQNYS74X2ZRHKKSRT6SZP
    :param app_token: 多维表格 app_token，如 GNsabO4Cpa7YRHseHZpczLRBnce
    :param table_id: 表格 table_id，如 tblkfxSZDvjLL1fA
    :param fields: 字段数据，例如:
        {
            "物品名称": "雨伞",
            "借用数量": 1,
            "是否为长期借用": "否",
            "部门": "AI效率流程部",
            "申请人": "何昌庆"
        }
    :return: 飞书 API 响应
    """
    url = (f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?"
           f"user_id_type=user_id")
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {"fields": fields}
    response = requests.request("POST", url, headers=headers, json=payload)
    return response


class BitableCreateRecordShortcut:
    """
    `创建多维表格记录`响应的快捷方式

    :param record: 源自 jsn['data']['record']
    """

    def __init__(self, record: dict[str, Any]):
        self.record = record

    @property
    def record_id(self) -> str:
        """新增记录的ID"""
        return self.record['record_id']

    @property
    def fields(self) -> dict[str, Any]:
        """成功新增的记录的数据"""
        return self.record.get('fields', {})


def search_app_table_record(
        tenant_access_token: str,
        app_token: str,
        table_id: str,
        view_id: str,
        field_names: list[str] | None = None,
        filter: dict[str, Any] | None = None,
        page_size: int = 200,
        page_token: str | None = None,
        user_id_type: str = "user_id"
) -> requests.Response:
    """搜索多维表格记录

    参考文档: https://open.feishu.cn/document/server-docs/bitable-v1/app-table-record/search

    :param tenant_access_token: tenant_access_token，如 t-g10462dQ2RU6GPHNQPRWQNYS74X2ZRHKKSRT6SZP
    :param app_token: 多维表格 app_token，如 AlmWbvs49aXDgCsKaiIcExeAnog
    :param table_id: 表格 table_id，如 tbl380GCCQACvor4
    :param view_id: 视图 ID，如 vewWkvxziJ，可选
    :param field_names: 需要返回的字段名列表，如 ["申请人", "物品名称", "是否领取"]，可选
    :param filter: 筛选条件，例如:
        {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "实际申请人 (人员 )",
                    "operator": "is",
                    "value": ["fc1425cf"]
                }
            ]
        }
    :param page_size: 分页大小，默认 200
    :param page_token: 分页标记，用于获取下一页数据，可选
    :param user_id_type: 用户 ID 类型，默认 "user_id"
    :return: 飞书 API 响应
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    params = {
        "user_id_type": user_id_type,
        "page_size": page_size
    }
    if page_token:
        params["page_token"] = page_token

    request_body: dict[str, Any] = {"view_id": view_id}
    if field_names is not None:
        request_body["field_names"] = field_names
    if filter is not None:
        request_body["filter"] = filter

    response = requests.request("POST", url, headers=headers, params=params, json=request_body)
    return response


class SearchAppTableRecordItemShortcut:
    """
    `搜索多维表格记录`响应中单个记录的快捷方式

    :param item: 源自 jsn['data']['items'] 中的一个元素
    """

    def __init__(self, item: dict[str, Any]):
        self.item = item

    @property
    def record_id(self) -> str:
        """记录ID"""
        return self.item['record_id']

    @property
    def fields(self) -> dict[str, Any]:
        """记录字段"""
        return self.item.get('fields', {})


class SearchAppTableRecordResponseShortcut:
    """
    `搜索多维表格记录`响应的快捷方式

    :param data: 源自 jsn['data']
    """

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @property
    def items(self) -> list[SearchAppTableRecordItemShortcut]:
        """记录列表"""
        return [SearchAppTableRecordItemShortcut(item) for item in self.data.get('items', [])]

    @property
    def has_more(self) -> bool:
        """是否还有更多项"""
        return self.data.get('has_more', False)

    @property
    def page_token(self) -> str | None:
        """分页标记，当 has_more 为 true 时，会同时返回新的 page_token，否则不返回 page_token"""
        return self.data.get('page_token')

    @property
    def total(self) -> int:
        """记录总数"""
        return self.data.get('total', 0)


def delete_app_table_record(
        tenant_access_token: str,
        app_token: str,
        table_id: str,
        record_id: str
) -> requests.Response:
    """删除多维表格记录

    参考文档: https://open.feishu.cn/document/server-docs/bitable-v1/app-table-record/delete

    :param tenant_access_token: tenant_access_token，如 t-g10462dQ2RU6GPHNQPRWQNYS74X2ZRHKKSRT6SZP
    :param app_token: 多维表格 app_token，如 AlmWbvs49aXDgCsKaiIcExeAnog
    :param table_id: 表格 table_id，如 tbl380GCCQACvor4
    :param record_id: 记录 ID，如 recuZLOJmkvnLK
    :return: 飞书 API 响应
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    response = requests.request("DELETE", url, headers=headers)
    return response
