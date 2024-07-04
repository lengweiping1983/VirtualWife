import os
import time
from pymilvus import DataType, FieldSchema, CollectionSchema, Collection, connections


_COLLECTION_NAME = "virtualwife"


class MilvusMemory():

    schema: CollectionSchema
    collection: Collection

    def __init__(self, host: str, port: str, user: str, password: str, db_name: str):

        connections.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
        )

        # 定义记忆Stream集合Schema、创建记忆Stream集合
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="user_name", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="role_name", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="timestamp", dtype=DataType.DOUBLE),
            FieldSchema(name="importance_score", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),  # 文本embedding向量
        ]
        self.schema = CollectionSchema(fields, _COLLECTION_NAME)
        self.collection = Collection(_COLLECTION_NAME, self.schema)

        # 创建索引
        index = {
            "index_type": "IVF_SQ8",
            "metric_type": "L2",
            "params": {"nlist": 1536},
        }
        self.collection.create_index("embedding", index)

    def get_embedding(self, text: str):
        from ...config import singleton_sys_config
        # 使用语言模型获得文本embedding向量
        embedding = singleton_sys_config.llm_model_driver.get_embedding(type=singleton_sys_config.conversation_llm_model_driver_type,
                                                                        text=text)
        return embedding

    def insert_memory(self, pk: int, text: str, user_name: str, role_name: str, importance_score: int):
        '''定义插入记忆对象函数'''
        timestamp = time.time()
        embedding = self.get_embedding(text)
        data = [[pk], [text], [user_name], [role_name], [timestamp],
                [importance_score], [embedding]]
        self.collection.insert(data)

    def compute_relevance(self, text: str, limit: int, expr: str=None):
        '''定义计算相关性分数函数'''
        # 搜索表达式
        search_result = self.search_memory(text, limit, expr)
        hits = []
        for hit in search_result:
            memory = {
                "id": hit.entity.id,
                "text": hit.entity.text,
                "user_name": hit.entity.user_name,
                "role_name": hit.entity.role_name,
                "timestamp": hit.entity.timestamp,
                "importance_score":  hit.entity.importance_score
            }
            memory["relevance"] = 1 - hit.distance
            hits.append(memory)

        return hits

    def search_memory(self, text: str, limit: int, expr: str=None):
        embedding = self.get_embedding(text)
        search_params = {"metric_type": "L2", "params": {"nprobe": 30}}

        vector_hits = None
        if expr is not None:
            vector_hits = self.collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=["id", "text", "user_name", "role_name",
                               "timestamp", "importance_score"]
            )
        else:
            vector_hits = self.collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=["id", "text", "user_name", "role_name",
                               "timestamp", "importance_score"]
            )

        return vector_hits[0]
    
    def pageQuery(self, offset: int, limit: int, expr: str):
        vector_hits = self.collection.query(
            offset=offset,
            limit=limit,
            expr=expr,
            output_fields=["id", "text", "user_name", "role_name",
                           "timestamp", "importance_score"]
        )
        return vector_hits

    def compute_recency(self, memories):
        '''定义计算最近性分数函数'''
        current_time = time.time()
        for memory in memories:
            time_diff = current_time - memory["timestamp"]
            memory["recency"] = 0.99 ** (time_diff / 3600)  # 指数衰减

    def normalize_scores(self, memories):
        for memory in memories:
            memory["total_score"] = memory["relevance"] + memory["importance_score"] + memory["recency"]

    def load(self):
        self.collection.load()

    def release(self):
        self.collection.release()

    def clear(self, role_name: str):
        ids_result = self.collection.query(
            offset=0,
            limit=100,
            expr=f"role_name == '{role_name}'",
            output_fields=["id"])
        ids = [item['id'] for item in ids_result]
        ids_expr = f"id in {ids}"
        self.collection.delete(ids_expr)
