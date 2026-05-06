# -*- coding: utf-8 -*-  
"""
@Date     :
@Author   : xwq
@Desc     : 统筹消息类型相关的组件及其方法

"""

msgtypes = {
    '文本': 'text',
    '富文本': 'post',
    '图片': 'image',
    '卡片': 'interactive',
    '分享群名片': 'share_chat',
    '分享个人名片': 'share_user',
    '语音': 'audio',
    '视频': 'media',
    '文件': 'file',
    '表情包': 'sticker',
    '系统消息': 'system',
}


def get_msgtype(*, en: str | None = None, ch: str | None = None) -> str | None:
    """获取消息类型

    :param en: 英文转中文时使用
    :param ch: 中文转英文时使用
    :return: 对应类型名称
    """
    if ch:
        return msgtypes.get(ch)
    elif en:
        reverse_msgtypes = {v: k for k, v in msgtypes.items()}
        return reverse_msgtypes.get(en)
    else:
        return None
