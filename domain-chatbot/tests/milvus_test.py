import os
import time
from pymilvus import DataType, FieldSchema, CollectionSchema, Collection, connections


connections.connect(
            host='127.0.0.1',
            port='19530',
            user='user',
            password='Milvus',
            db_name='default',
        )