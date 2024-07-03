import queue
import threading
import logging
import traceback

from ..llms.base_llm_model import ChatHistroy
from ..utils.chat_message_utils import format_user_message
from ..config import singleton_sys_config
from ..memory import memory_storage_driver
from ..service import portal_user_service


# 创建一个线程安全的优先级队列
chat_history_queue = queue.SimpleQueue()
logger = logging.getLogger(__name__)


class ChatHistoryMessage():
    '''定义聊天历史消息队列'''
    user_name: str
    user_text: str
    role_name: str
    role_text: str
    automatic: int

    def __init__(self, user_name: str, user_text: str, role_name: str, role_text: str, automatic: int) -> None:
        self.user_name = user_name
        self.user_text = user_text
        self.role_name = role_name
        self.role_text = role_text
        self.automatic = automatic

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "user_text": self.user_text,
            "role_name": self.role_name,
            "role_text": self.role_text,
            "automatic": self.automatic
        }


def put_message(message: ChatHistoryMessage):
    global chat_history_queue
    chat_history_queue.put(message)


def send_message():
    global chat_history_queue
    while True:
        try:
            message = chat_history_queue.get()
            if message is not None and message != '':
                # 存储到记忆库中
                memory_storage_driver.save_short_memory(
                    message.user_name, message.user_text, message.role_name, message.role_text, message.automatic)
                
                # # 判断当前记忆的重要性
                # memory = format_user_message(message.user_name, message.user_text)
                # rating = singleton_sys_config.importance_rating.rating(memory)

                # # 如果当前记忆的重要性大于5，进行一次人物画像更新
                # if rating > 5:
                #     portal_user = portal_user_service.get_and_create(message.user_name)
                #     user_id = str(portal_user.id)
                #     channel_id = str(portal_user.id)
                #     user = memory_storage_driver.chat_histroy_service.zep_service.get_user(user_id)
                #     portrait = user.metadata["portrait"]
                #     recently_memory = memory_storage_driver.chat_histroy_service.zep_service.get_memorys(
                #         channel_id=channel_id, limit=10)
                #     recently_memory.reverse()
                #     recently_memory_str = format_histroy(recently_memory)
                #     portrait = singleton_sys_config.portrait_analysis.analysis(message.user_name, portrait,
                #                                                                recently_memory_str)
                #     # 获取最新的人物画像信息，并且进行更新
                #     user = memory_storage_driver.chat_histroy_service.zep_service.get_user(user_id)
                #     user.metadata["portrait"] = portrait
                #     memory_storage_driver.chat_histroy_service.zep_service.update_user(user_id, user.metadata)
                #     logger.info(f"# user_name: {message.user_name} # update metadata => {portrait}")

        except Exception as e:
            traceback.print_exc()


def format_histroy(recently_memory: list[ChatHistroy]) -> str:
    chat_histroy_str = []
    for item in recently_memory:
        chat_histroy_str.append(item.content)
    return "\n".join(chat_histroy_str)


def conversation_end_callback(user_name: str, user_text: str, role_name: str, role_text: str, automatic: int):
    if automatic != 0 and role_text.lower() == "null":
        return
    # 异步存储记忆
    put_message(ChatHistoryMessage(
        user_name=user_name,
        user_text=user_text,
        role_name=role_name,
        role_text=role_text,
        automatic=automatic
    ))


class ChatHistoryMessageQueryJobTask():

    @staticmethod
    def start():
        # 创建后台线程
        background_thread = threading.Thread(target=send_message)
        # 将后台线程设置为守护线程，以便在主线程结束时自动退出
        background_thread.daemon = True
        # 启动后台线程
        background_thread.start()
        logger.info("=> Start ChatHistoryMessageQueryJobTask Success")
