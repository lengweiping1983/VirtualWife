import re
import logging
import queue
import threading
import traceback
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..utils.chat_message_utils import format_chat_text
from ..llms.function import GenerationEmote


# 聊天消息通道
chat_channel = "chat_channel"
# 创建一个线程安全的队列
chat_queue = queue.SimpleQueue()
logger = logging.getLogger(__name__)


class RealtimeMessage():
    type: str
    user_name: str
    content: str
    emote: str
    action: str
    expand: str

    def __init__(self, type: str, user_name: str, content: str, emote: str,
                 action: str = None, expand: str = None) -> None:
        self.type = type
        self.user_name = user_name
        self.content = content
        self.emote = emote
        self.action = action
        self.expand = expand

    def to_dict(self):
        return {
            "type": self.type,
            "user_name": self.user_name,
            "content": self.content,
            "emote": self.emote,
            "action": self.action,
            "expand": self.expand
        }


def put_message(message: RealtimeMessage):
    global chat_queue
    chat_queue.put(message)


def send_message():
    global chat_queue
    channel_layer = get_channel_layer()
    send_message_exe = async_to_sync(channel_layer.group_send)

    while True:
        try:
            message = chat_queue.get()
            if message is not None and message != '':
                chat_message = {"type": "chat_message", "message": message.to_dict()}
                send_message_exe(chat_channel, chat_message)
        except Exception as e:
            traceback.print_exc()


def realtime_callback(user_name: str, role_name: str, content: str, end_bool: bool):
    if not hasattr(realtime_callback, "message_buffer"):
        realtime_callback.message_buffer = ""

    realtime_callback.message_buffer += content
    # 如果 content 以结束标点符号或结束符结尾，打印并清空缓冲区
    message_text = ""
    if end_bool:
        message_text = realtime_callback.message_buffer
        realtime_callback.message_buffer = ""
    else:
        match = re.match(r"^(.+[。．！？\n]|.{10,}[、,])", realtime_callback.message_buffer)
        if match:
            message_text = match.group()
            realtime_callback.message_buffer = realtime_callback.message_buffer[len(message_text):]
        else:
            return
    if message_text != "":
        message_text = format_chat_text(user_name, role_name, message_text)
        if message_text != "":
            # 生成人物表情
            generation_emote = GenerationEmote()
            emote = generation_emote.generation_emote(text=message_text)

            # 发送文本消息
            put_message(RealtimeMessage(type="user", user_name=user_name, content=message_text, emote=emote))


class RealtimeMessageQueryJobTask():

    @staticmethod
    def start():
        # 创建后台线程
        background_thread = threading.Thread(target=send_message)
        background_thread.daemon = True
        # 启动后台线程
        background_thread.start()
        logger.info("=> Start RealtimeMessageQueryJobTask Success")
