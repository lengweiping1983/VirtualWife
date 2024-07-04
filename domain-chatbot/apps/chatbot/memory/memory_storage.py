import logging
import traceback
from typing import Any, Dict, List

from ..utils.snowflake_utils import SnowFlake
from .local.local_storage_impl import LocalStorage
from .milvus.milvus_storage_impl import MilvusStorage
from pymilvus import DataType, FieldSchema, CollectionSchema, Collection, connections


logger = logging.getLogger(__name__)


class MemoryStorageDriver:
    snow_flake: SnowFlake = SnowFlake(data_center_id=5, worker_id=5)
    short_memory_storage: LocalStorage
    long_memory_storage: MilvusStorage

    def __init__(self, sys_config_json: any) -> None:
        milvus_memory_storage_config = sys_config_json["memoryStorageConfig"]["milvusMemory"]
        host = milvus_memory_storage_config["host"]
        port = milvus_memory_storage_config["port"]
        user = milvus_memory_storage_config["user"]
        password = milvus_memory_storage_config["password"]
        db_name = milvus_memory_storage_config["dbName"]

        print(milvus_memory_storage_config)
        connections.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
        )
        self.short_memory_storage = LocalStorage(sys_config_json)
        self.long_memory_storage = MilvusStorage(sys_config_json)

    def search_short_memory(self, user_name: str, user_text: str, role_name: str, limit: int=15) -> list[Dict[str, str]]:
        local_memory = self.short_memory_storage.pageQuery(role_name=role_name, user_name=user_name,
                                                           page_num=1, page_size=limit, summary=0)
        return local_memory

    def search_long_memory(self, user_name: str, user_text: str, role_name: str, limit: int=10) -> str:
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

    def save_short_memory(self, user_name: str, user_text: str, role_name: str, role_text: str, automatic: int) -> None:
        # 存储短期记忆
        pk = self.get_current_entity_id()
        self.short_memory_storage.save(role_name=role_name, user_name=user_name, user_text=user_text, role_text=role_text, automatic=automatic, pk=pk)
    
    def save_long_memory(self, user_name: str, role_name: str, text: str, importance_score: int) -> None:
        # 存储长期记忆
        pk = self.get_current_entity_id()
        self.long_memory_storage.save(role_name=role_name, user_name=user_name, text=text, importance_score=importance_score, pk=pk)

    def clear(self, role_name: str) -> None:
        self.long_memory_storage.clear(role_name)
        self.short_memory_storage.clear(role_name)

    def get_current_entity_id(self) -> int:
        '''生成唯一标识'''
        return self.snow_flake.task()
