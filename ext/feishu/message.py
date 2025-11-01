# -*- coding: utf-8 -*-
"""
@Author   : xwq
@Desc     : 统筹消息相关的组件及其方法

"""
import enum
import json
from typing import Any

import requests

from .common import compose_headers


class MsgType(enum.Enum):
    TEXT = 'text'
    POST = 'post'
    FILE = 'file'
    INTERACTIVE = 'interactive'


class ReceiveIdType(enum.Enum):
    USER_ID = 'user_id'
    OPEN_ID = 'open_id'
    CHAT_ID = 'chat_id'


def compose_text_content(content: str) -> dict:
    """组装文本消息所需的content

    :param content: 文本
    :return: content内容
    """
    return {"text": content}


class Post:
    """
    飞书的富文本
    原型支持中英双版，这里仅直接提供中文
    [原型](https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json#45e0953e)
    """

    def __init__(self):
        self._title: str | None = None
        self._content: list[list[dict]] = []
        self._i: int = -1

    def set_title(self, title: str) -> 'Post':
        """
        设置标题
        :param title: 标题
        """
        self._title = title
        return self

    def add_line(self) -> 'Post':
        self._content.append([])
        self._i += 1
        return self

    def add_text(self, text: str, un_escape: bool = None, style: list[str] = None) -> 'Post':
        """
        添加文本
        :param text: 文本
        :param un_escape: 是否 unescape 解码
        :param style: 格式, 如 bold加粗, italic斜线, underline下划线, lineThrough删除线
        """
        dct = {"tag": "text", "text": text}
        if un_escape is not None:
            dct['un_escape'] = un_escape
        if style is not None:
            dct['style'] = style
        self._content[self._i].append(dct)
        return self

    def add_a(self, text: str, href: str, style: list[str] = None):
        """
        超链接标签
        :param text:
        :param href:
        :param style: bold加粗, italic斜线, underline下划线, lineThrough删除线
        :return:
        """
        dct = {"tag": "a", "text": text, "href": href}
        if style is not None:
            dct['style'] = style
        self._content[self._i].append(dct)
        return self

    def add_at(self, user_id: str, style: list[str] = None) -> 'Post':
        """
        添加@
        :param user_id: 用户id, 传入的值可以是用户的 user_id、open_id、union_id, 如需 @ 所有人，则该参数需要传入 all
        :param style: 格式, 如 bold加粗, italic斜线, underline下划线, lineThrough删除线
        """
        dct = {"tag": "at", "user_id": user_id}
        if style is not None:
            dct['style'] = style
        self._content[self._i].append(dct)
        return self

    def add_img(self, image_key: str) -> 'Post':
        """
        添加图片
        :param image_key: 图片的 key
        """
        dct = {"tag": "img", "image_key": image_key}
        self._content[self._i].append(dct)
        return self

    def add_media(self, file_key, image_key: str = None) -> 'Post':
        """
        添加视频文件
        :param file_key: 视频文件的 Ke
        :param image_key: 视频封面图片的 Key
        """
        dct = {"tag": "media", "file_key": file_key}
        if image_key is not None:
            dct['image_key'] = image_key
        self._content[self._i].append(dct)
        return self

    def add_emotion(self, emoji_type: str) -> 'Post':
        """
        表情标签
        [表情文案说明](https://open.feishu.cn/document/server-docs/im-v1/message-reaction/emojis-introduce)
        :param emoji_type:
        :return:
        """
        dct = {"tag": "emotion", "emoji_type": emoji_type}
        self._content[self._i].append(dct)
        return self

    def add_code_block(self, text: str, language: str = None) -> 'Post':
        """
        代码块标签
        :param language: 代码块的语言类型。可选值有 PYTHON、C、CPP、GO、JAVA、KOTLIN、SWIFT、PHP、RUBY、RUST、JAVASCRIPT、TYPESCRIPT、BASH、SHELL、SQL、JSON、XML、YAML、HTML、THRIFT 等
        :param text:
        :return:
        """
        dct = {"tag": "code_block", "text": text}
        if language is not None:
            dct['language'] = language
        self._content[self._i].append(dct)
        return self

    def add_hr(self) -> 'Post':
        """
        分割线标签
        """
        dct = {"tag": "hr"}
        self._content[self._i].append(dct)
        return self

    def add_md(self, text: str) -> 'Post':
        """
        Markdown 标签
        :param text:
        :return:

        [注意]
        md 标签会独占一个或多个段落，不能与其他标签在同一行
        md 标签仅支持发送，获取消息内容时将不再包含此标签，会根据 md 中的内容转换为其他相匹配的标签
        """
        dct = {"tag": "md", "text": text}
        if len(self._content[self._i]) > 0:
            self.add_line()
        self._content[self._i].append(dct)
        self.add_line()
        return self

    def as_json(self, en: bool = False) -> dict:
        """
        转为json
        :param en: 是否将语言标记为英文
        :return:
        """
        lang = 'en_us' if en else 'zh_cn'
        dct = {"content": self._content}
        if self._title is not None:
            dct['title'] = self._title
        return {lang: dct}


def send_message(
        receive_id: str,
        msg_type: str,
        content: dict | list,
        tenant_access_token: str,
        receive_id_type: str = ReceiveIdType.USER_ID.value,
) -> requests.Response:
    """发送消息

    参考 https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create

    :param receive_id: 目标id
    :param msg_type: 常见类型, text文本, post富文本
    :param content: 消息内容
    :param receive_id_type: 目标id类型
    :param tenant_access_token: 应用token
    """
    return requests.post(
        url=f"https://open.feishu.cn/open-apis/im/v1/messages",
        headers=compose_headers(tenant_access_token),
        json={
            "content": json.dumps(content, ensure_ascii=False),
            "msg_type": msg_type,
            "receive_id": receive_id
        },
        params={
            'receive_id_type': receive_id_type,
        }
    )


def send_text(
        receive_id: str,
        content: str,
        tenant_access_token: str,
        receive_id_type: str = ReceiveIdType.USER_ID.value,
) -> requests.Response:
    """发送文本消息

    :param receive_id: 目标id
    :param content: 消息内容
    :param receive_id_type: 目标id类型
    :param tenant_access_token:
    """
    return send_message(
        receive_id=receive_id,
        msg_type=MsgType.TEXT.value,
        content=compose_text_content(content),
        tenant_access_token=tenant_access_token,
        receive_id_type=receive_id_type
    )


def send_post(
        receive_id: str,
        content: Post,
        tenant_access_token: str,
        receive_id_type: str = ReceiveIdType.USER_ID.value,
) -> requests.Response:
    """发送富文本消息

    :param receive_id: 目标id
    :param content: 消息内容
    :param receive_id_type: 目标id类型
    :param tenant_access_token:
    """
    return send_message(
        receive_id=receive_id,
        msg_type=MsgType.POST.value,
        content=content.as_json(),
        tenant_access_token=tenant_access_token,
        receive_id_type=receive_id_type
    )


def send_file(
        receive_id: str,
        file_key: str,
        tenant_access_token: str,
        receive_id_type: str = ReceiveIdType.USER_ID.value,
) -> requests.Response:
    """发送文本消息

    :param receive_id: 目标id
    :param file_key: file_key
    :param receive_id_type: 目标id类型
    :param tenant_access_token:
    """
    return send_message(
        receive_id=receive_id,
        msg_type=MsgType.FILE.value,
        content={'file_key': file_key},
        tenant_access_token=tenant_access_token,
        receive_id_type=receive_id_type
    )


def send_interactive(
        receive_id: str,
        template_id: str,
        template_version_name: str,
        template_variable: dict[str, str],
        tenant_access_token: str,
        receive_id_type: str = ReceiveIdType.USER_ID.value,
) -> requests.Response:
    """发送卡片消息

    :param receive_id: 目标id
    :param template_id: 模板id
    :param template_version_name: 模板版本，如1.0.0
    :param template_variable: 模板变量
    :param receive_id_type: 目标id类型
    :param tenant_access_token:
    """
    return send_message(
        receive_id=receive_id,
        msg_type=MsgType.INTERACTIVE.value,
        content={
            "type": "template",
            "data": {
                "template_id": template_id,
                "template_version_name": template_version_name,
                "template_variable": template_variable
            }
        },
        tenant_access_token=tenant_access_token,
        receive_id_type=receive_id_type
    )


class SendMessageResponseShortcut:
    """
    发送消息的响应的快捷方式
    """

    def __init__(self, data: dict[str, Any]):
        """

        :param data: 来自jsn['data']
        """
        self.data = data

    @property
    def message_id(self) -> str:
        return self.data['message_id']

    @property
    def msg_type(self) -> str:
        return self.data['msg_type']

    @property
    def parent_id(self) -> str | None:
        return self.data.get('parent_id')

    @property
    def chat_id(self) -> str:
        return self.data['chat_id']

    @property
    def create_time(self) -> str:
        return self.data['create_time']