# -*- coding: utf-8 -*-
"""
@Author   : xwq
@Desc     : 飞书API重试机制

"""
import logging
import time
from typing import Callable, ParamSpec

import requests


class RetryTooMuch(Exception):
    """重试次数过多异常"""
    pass


def _pass():
    pass


_P = ParamSpec('_P')


def retry_feishu_api(
        api: Callable[_P, requests.Response],
        args: list[_P.args],
        interrupt: Callable[[], None] = _pass,
) -> dict:
    """重试飞书api

    :param api: 飞书api执行函数
    :param args: 顺序传参
    :param interrupt: 在发起api请求前执行一次中断
    :return: 飞书反馈
    """
    
    logging.info(f'{api.__name__} >> 开始执行飞书API调用')
    common_retry_limit = 3
    qps_retry_limit = 10
    while True:
        if common_retry_limit <= 0 or qps_retry_limit <= 0:
            raise RetryTooMuch(f'{api.__name__} >> 重试过多')

        interrupt()
        response = api(*args)
        if 200 <= response.status_code < 300:
            result = response.json()
            logging.info(f'{api.__name__} >> 飞书API调用成功')
            return result

        try:
            jsn = response.json()
        except requests.JSONDecodeError:
            logging.error(f'{api.__name__} >> api响应无法json解析: {response.status_code}, {response.text}')
            time.sleep(1)
            common_retry_limit -= 1
            continue

        if not isinstance(jsn, dict):
            logging.error(f'{api.__name__} >> api响应非dict: {response.status_code}, {response.text}')
            time.sleep(1)
            common_retry_limit -= 1
            continue

        code = jsn.get('code', -1)
        if code == 230020:
            logging.warning(f'{api.__name__} >> 触发频率限制')
            time.sleep(1)
            qps_retry_limit -= 1
            continue

        logging.error(f'{api.__name__} >> 未知响应: {response.status_code}, {response.text}')
        time.sleep(1)
        common_retry_limit -= 1
        continue

