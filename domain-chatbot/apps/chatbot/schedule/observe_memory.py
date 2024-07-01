import json
import logging
import threading

from ..config import singleton_sys_config
from ..memory import memory_storage_driver
from ..character.character_generation import singleton_character_generation
from ..llms.function import TopicBot
from ..process import process_core


logger = logging.getLogger(__name__)


def observe_memory_job():
    topic_bot = TopicBot()
    character = singleton_character_generation.get_character(singleton_sys_config.character)
    role_name = character.role_name
    user_name = singleton_sys_config.user_name

    # 拉取最近的记忆和对话上下文
    local_memory = memory_storage_driver.search_short_memory(user_name=user_name, user_text=None, role_name=role_name)
    local_memory_list = [f"{item['user']}\n{item['ai']}" for item in local_memory]
    local_memory_str = '\n'.join(local_memory_list)
    topic = topic_bot.generation_topic(local_memory_str)
    if topic != "":
        process_core.chat(user_name=user_name, user_text=f"{role_name}需要基于该建议`{topic}`回复内容")
    print("observe_memory_job..........")


def run_observe_memory_job(interval, observe_memory_job):
    threading.Timer(interval, run_observe_memory_job, [interval, observe_memory_job]).start()
    observe_memory_job()
