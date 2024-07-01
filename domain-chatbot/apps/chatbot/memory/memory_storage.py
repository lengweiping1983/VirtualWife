import json
import logging
import traceback
from typing import Any, Dict, List

from ..utils.chat_message_utils import format_message, format_user_message, format_role_message
from ..utils.snowflake_utils import SnowFlake
from ..config.sys_config import SysConfig
from .local.local_storage_impl import LocalStorage
from .milvus.milvus_storage_impl import MilvusStorage
from ..llms.function import Summary, ImportanceRating


logger = logging.getLogger(__name__)


class MemoryStorageDriver:
    snow_flake: SnowFlake = SnowFlake(data_center_id=5, worker_id=5)
    sys_config: SysConfig
    short_memory_storage: LocalStorage
    long_memory_storage: MilvusStorage

    def __init__(self, memory_storage_config: dict[str, str], sys_config: SysConfig) -> None:
        self.sys_config = sys_config
        self.short_memory_storage = LocalStorage(memory_storage_config)
        if sys_config.enable_longMemory:
            self.long_memory_storage = MilvusStorage(memory_storage_config)

    def search_short_memory(self, user_name: str, user_text: str, role_name: str, limit: int = 10) -> list[Dict[str, str]]:
        local_memory = self.short_memory_storage.pageQuery(role_name=role_name, user_name=user_name,
                                                           page_num=1, page_size=limit)
        return local_memory

    def search_long_memory(self, user_name: str, user_text: str, role_name: str, limit: int = 10) -> str:
        # 是否开启长期记忆
        if self.sys_config.enable_longMemory:
            try:
                long_history = ""
                # 获取长期记忆
                long_memory = self.long_memory_storage.search(role_name=role_name, user_name=user_name,
                                                              text=user_text, limit=limit)
                if len(long_memory) > 0:
                    long_history = "\n".join(long_memory)
                return long_history
            except Exception as e:
                traceback.print_exc()
                logger.error("search long memory error: %s" % str(e))
        return ""

    def save(self, user_name: str, user_text: str, role_name: str, role_text: str) -> None:
        # 存储短期记忆
        pk = self.get_current_entity_id()
        self.short_memory_storage.save(role_name=role_name, user_name=user_name, user_text=user_text, role_text=role_text, pk=pk)
        # 是否开启长期记忆
        if self.sys_config.enable_longMemory:
            # 将当前对话语句生成摘要
            history = format_message(user_name=user_name, user_text=user_text, role_name=role_name, role_text=role_text)
            importance_score = 3
            if self.sys_config.enable_summary:
                summary = Summary()
                history = summary.summary(text=history)
                importance_rating = ImportanceRating()
                importance_score = importance_rating.importance(text=history)
            self.long_memory_storage.save(role_name=role_name, user_name=user_name, text=history, importance_score=importance_score, pk=pk)

    def clear(self, role_name: str) -> None:
        self.long_memory_storage.clear(role_name)
        self.short_memory_storage.clear(role_name)

    def get_current_entity_id(self) -> int:
        '''生成唯一标识'''
        return self.snow_flake.task()
