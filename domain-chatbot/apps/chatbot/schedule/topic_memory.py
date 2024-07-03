import logging
import threading
import traceback

from ..utils.chat_message_utils import format_user_message, format_role_message
from ..config import singleton_sys_config
from ..memory import memory_storage_driver
from ..character.character_generation import singleton_character_generation
from ..process import topic_bot


logger = logging.getLogger(__name__)


def topic_memory_job():
    character = singleton_character_generation.get_character(singleton_sys_config.character)
    role_name = character.role_name
    user_name = singleton_sys_config.user_name

    try:
        # 拉取最近的记忆和对话上下文
        local_memory = memory_storage_driver.short_memory_storage.pageQuery(role_name=role_name, user_name=user_name,
                                                                            page_num=1, page_size=singleton_sys_config.topic_memory_num, topic=0)
        if len(local_memory) < singleton_sys_config.topic_memory_num / 2:
            return
        local_memory_list = [f"{format_user_message(user_name, item['user'])}\n{format_role_message(role_name, item['assistant'])}" for item in local_memory]
        local_memory_str = '\n'.join(local_memory_list)
        topic_bot.generation_topic(user_name=user_name, role_name=role_name, text=local_memory_str)
        memory_storage_driver.short_memory_storage.update_list_topic(local_memory)
    except Exception as e:
            traceback.print_exc()
            logger.error("topic error: %s" % str(e))
    print("topic_memory_job..........")


def run_topic_memory_job(interval, topic_memory_job):
    threading.Timer(interval, run_topic_memory_job, [interval, topic_memory_job]).start()
    topic_memory_job()
