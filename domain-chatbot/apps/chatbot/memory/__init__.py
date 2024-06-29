import os
import json
import logging


from ..config import singleton_sys_config
from ..memory.memory_storage import MemoryStorageDriver
logger = logging.getLogger(__name__)


def lazy_memory_storage(sys_config_json: any, sys_config: any):
    # 加载记忆模块配置
    memory_storage_config = {
        "host": sys_config_json["memoryStorageConfig"]["milvusMemory"]["host"],
        "port": sys_config_json["memoryStorageConfig"]["milvusMemory"]["port"],
        "user": sys_config_json["memoryStorageConfig"]["milvusMemory"]["user"],
        "password": sys_config_json["memoryStorageConfig"]["milvusMemory"]["password"],
        "db_name": sys_config_json["memoryStorageConfig"]["milvusMemory"]["dbName"],
    }
    logger.info(f"=> memory_storage_config:{memory_storage_config}")
    # 加载记忆模块驱动
    return MemoryStorageDriver(memory_storage_config=memory_storage_config, sys_config=sys_config)


memory_storage_driver: any
# 懒加载记忆模块
try:
    memory_storage_driver = lazy_memory_storage(
        sys_config_json=singleton_sys_config.get(), sys_config=singleton_sys_config)
except Exception as e:
    logger.error("lazy memory_storage error: %s" % str(e))
