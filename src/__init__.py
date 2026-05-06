import os
from typing import Any

import yaml


def get_root_path() -> str:
    """
    取项目根目录绝对地址
    :return:
    """
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


CONFIG_PATH = os.path.join(get_root_path(), 'src', "config.yml")


def get_config(*keys: str) -> Any:
    """
    获取配置文件的内容
    :param keys:
    :return:
    """

    with open(CONFIG_PATH, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    result = data
    for key in keys:
        result = result[key]
    return result
