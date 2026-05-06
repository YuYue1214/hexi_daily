# -*- coding: utf-8 -*-  
"""
@Author   : xwq
@Desc     : 统筹电子表格相关组件及其方法

"""
from typing import Any

import requests


def spreadsheet_append(
        tenant_access_token: str, spreadsheet_token: str, sheet_id: str, values: list[Any]
) -> requests.Response:
    """追加一行数据
    
    参考 https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/append-data
    表格链接形式参考 https://jqx28l0j4lx.feishu.cn/sheets/NPZBs5HrVhtXA0tqPNLc30hunvh?sheet=759ac0
    
    :param tenant_access_token: tenant_access_token,如 t-g10462dQ2RU6GPHNQPRWQNYS74X2ZRHKKSRT6SZP
    :param spreadsheet_token: 如 NPZBs5HrVhtXA0tqPNLc30hunvh
    :param sheet_id: 如759ac0
    :param values: 数据
    :return: 飞书的响应
    """
    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_append'
    headers = {'Authorization': f'Bearer {tenant_access_token}', 'Content-Type': 'application/json; charset=utf-8'}
    value_range = {'valueRange': {'range': sheet_id, 'values': [values]}}
    response = requests.post(url, headers=headers, json=value_range)
    return response


def _get_letter(n: int) -> str:
    """取对应序列为的字符

    序列规律如 A、B、...、AA、AB、AC、...、AAA、AAB、...

    :param n: 对应位置
    :return: 对应位置字符串
    """
    result = []
    while n > 0:
        n -= 1  # 因为A对应1而不是0
        remainder = n % 26
        result.append(chr(ord('A') + remainder))
        n = n // 26
    return ''.join(reversed(result))


def spreadsheet_lappend(
        tenant_access_token: str, spreadsheet_token: str, sheet_id: str, values: list[Any]
) -> requests.Response:
    """左追加一行数据

    参考 https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/prepend-data
    表格链接形式参考 https://jqx28l0j4lx.feishu.cn/sheets/NPZBs5HrVhtXA0tqPNLc30hunvh?sheet=759ac0

    :param tenant_access_token: tenant_access_token,如 t-g10462dQ2RU6GPHNQPRWQNYS74X2ZRHKKSRT6SZP
    :param spreadsheet_token: 如 NPZBs5HrVhtXA0tqPNLc30hunvh
    :param sheet_id: 如759ac0
    :param values: 数据
    :return: 飞书的响应
    """
    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_prepend'
    headers = {'Authorization': f'Bearer {tenant_access_token}', 'Content-Type': 'application/json; charset=utf-8'}
    value_range = {'valueRange': {'range': f'{sheet_id}!A2:{_get_letter(len(values[0]))}2', 'values': [values]}}
    response = requests.post(url, headers=headers, json=value_range)
    return response
