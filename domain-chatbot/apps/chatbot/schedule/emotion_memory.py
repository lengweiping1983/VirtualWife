import logging
import threading
import traceback
from ..utils.chat_message_utils import format_user_message, format_role_message
from ..config import singleton_sys_config
from ..character.character_generation import singleton_character_generation
from ..process import emotion_bot


logger = logging.getLogger(__name__)


def emotion_memory_job():
    character = singleton_character_generation.get_character(singleton_sys_config.character)
    role_name = character.role_name
    for user_name in singleton_sys_config.userNameSet:
        while True:
            try:
                # 拉取最近的记忆和对话上下文
                local_memory = singleton_sys_config.memory_storage_driver.short_memory_storage.pageQuery(
                    role_name=role_name, user_name=user_name,
                    page_num=1, page_size=singleton_sys_config.emotion_memory_num, emotion=0, order="asc")
                if len(local_memory) < singleton_sys_config.emotion_memory_num / 2:
                    break
                local_memory_list = [f"{format_user_message(user_name, item['user'])}\n{format_role_message(role_name, item['assistant'])}" for item in local_memory]
                local_memory_str = '\n'.join(local_memory_list)
                emotion_bot.generation_emotion(user_name=user_name, role_name=role_name, text=local_memory_str)
                singleton_sys_config.memory_storage_driver.short_memory_storage.update_list_emotion(local_memory)
            except Exception as e:
                traceback.print_exc()
                logger.error("emotion error: %s" % str(e))
    print("emotion_memory_job..........")


def run_emotion_memory_job(interval, emotion_memory_job):
    threading.Timer(interval, run_emotion_memory_job, [interval, emotion_memory_job]).start()
    emotion_memory_job()
