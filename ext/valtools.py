import decimal
import hashlib
from functools import singledispatch
from typing import Any, Iterable, TypeVar, Iterator, Tuple, Hashable, Sequence, Optional, Callable

__all__ = [
    'integer', 'dcml', 'default', 'combination', 'deduplicate', 'md5'
]

T = TypeVar('T')
K = TypeVar('K', bound=Hashable)


@singledispatch
def integer(v) -> int:
    """转为整数"""
    raise ValueError(f'暂未适配值为"{v}", 类型为{type(v)}的int转化')


@integer.register(int)
def _(v: int):
    return v


@integer.register(str)
def _(v: str):
    v = v.replace(',', '')
    v = v.replace(' ', '')
    if v.endswith('万'):
        v = float(v[:-1]) * 10000
    elif v.endswith('w'):
        v = float(v[:-1]) * 10000
    elif v.endswith('亿'):
        v = float(v[:-1]) * (10 ** 8)
    elif v.endswith('千'):
        v = float(v[:-1]) * 1000
    return int(v)


@singledispatch
def dcml(v) -> decimal.Decimal | None:
    """转为decimal"""
    if v is None:
        return None
    raise ValueError(f'暂未适配值为"{v}", 类型为{type(v)}的decimal转化')


@dcml.register(decimal.Decimal)
def _(v: decimal.Decimal):
    return v


@dcml.register(int)
def _(v: int):
    return decimal.Decimal(v)


@dcml.register(float)
def _(v: float):
    return decimal.Decimal(v)


@dcml.register(str)
def _(v: str):
    v = v.replace(',', '')
    v = v.replace(' ', '')
    if v in ('-', ''):
        return None
    if v[-1] == '万':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10000)
    if v[-1] == '亿':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10 ** 8)
    if v[-1] == 'w':
        return decimal.Decimal(v[:-1]) * decimal.Decimal(10000)
    elif v[-1] == '%':
        return decimal.Decimal(v[:-1]) / decimal.Decimal(100)
    return decimal.Decimal(v)


def default(v, df=None) -> Any:
    """
    设置默认值
    :param v:
    :param df:
    :return:
    """
    if v is None:
        return df
    else:
        return v


def combination(*sequences: Iterable[T]) -> Iterator[Tuple[T, ...]]:
    """数学上的组合"""
    if len(sequences) == 0:
        return None
    if len(sequences) == 1:
        for x in sequences[0]:
            yield (x,)
        return
    for x in sequences[0]:
        for y in combination(*sequences[1:]):
            yield x, *y


def deduplicate(
        sequence: Sequence[T],
        key: Optional[Callable[[T], K]] = None,
) -> list[T]:
    """
    对序列数据进行去重操作

    参数:
        sequence: 要处理的序列数据（list/tuple等）
        key: 去重依据的函数，默认为None（直接比较元素）

    返回:
        去重后的序列，list
    """
    seen: set[K] = set()
    result: list[T] = []

    for item in sequence:
        identifier: K = item if key is None else key(item)
        if identifier not in seen:
            seen.add(identifier)
            result.append(item)

    return result


def md5(text: str | bytes, encode: str = 'utf-8') -> str:
    """
    md5加密
    :param text: 加密文本
    :param encode: 指定编码格式
    :return:
    """
    if isinstance(text, str):
        text = text.encode(encode)
    return hashlib.md5(text).hexdigest()
