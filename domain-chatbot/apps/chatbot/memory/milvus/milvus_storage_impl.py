from .milvus_memory import MilvusMemory


class MilvusStorage:
    '''Milvus向量存储记忆模块'''
    milvus_memory: MilvusMemory

    def __init__(self, memory_storage_config: dict[str, str]):
        host = memory_storage_config["host"]
        port = memory_storage_config["port"]
        user = memory_storage_config["user"]
        password = memory_storage_config["password"]
        db_name = memory_storage_config["db_name"]
        self.milvus_memory = MilvusMemory(
            host=host, port=port, user=user, password=password, db_name=db_name)

    def search(self, role_name: str, user_name: str, text: str, limit: int, memories_size: int=10) -> list[str]:
        '''检索记忆,只返回关联性最强的记忆'''
        self.milvus_memory.load()
        expr = f"role_name == '{role_name}' and user_name == '{user_name}'"
        # 查询记忆，并且使用 关联性 + 重要性 + 最近性 算法进行评分
        memories = self.milvus_memory.compute_relevance(text, limit, expr=expr)
        self.milvus_memory.compute_recency(memories)
        self.milvus_memory.normalize_scores(memories)
        self.milvus_memory.release()

        # 排序获得最高分的记忆
        memories = sorted(memories, key=lambda m: m["total_score"], reverse=True)

        if len(memories) > 0:
            memories_text = [item['text'] for item in memories]
            memories_text = memories_text[:memories_size] if len(
                memories_text) >= memories_size else memories_text
            return memories_text
        else:
            return []

    def pageQuery(self, role_name: str, user_name: str, page_num: int, page_size: int) -> list[str]:
        '''分页检索记忆'''
        self.milvus_memory.load()
        expr = f"role_name == '{role_name}' and user_name == '{user_name}'"
        offset = (page_num - 1) * page_size
        limit = page_size
        result = self.milvus_memory.pageQuery(offset=offset, limit=limit, expr=expr)
        self.milvus_memory.release()
        return result

    def save(self, role_name: str, user_name: str, text: str, importance_score: int, pk: int) -> None:
        '''保存记忆'''
        self.milvus_memory.load()
        self.milvus_memory.insert_memory(
            pk=pk, text=text, user_name=user_name, role_name=role_name, importance_score=importance_score)
        self.milvus_memory.release()

    def clear(self, role_name: str) -> None:
        '''清空记忆'''
        self.milvus_memory.load()
        self.milvus_memory.clear(role_name)
        self.milvus_memory.release()
