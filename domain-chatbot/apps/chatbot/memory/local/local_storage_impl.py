import datetime
import logging
import jieba
import jieba.analyse
from django.db.models import Q
from typing import Any, Dict, List

from ...utils.chat_message_utils import format_message, format_user_message, format_role_message
from ...models import LocalMemoryModel


logger = logging.getLogger(__name__)


class LocalStorage:

    def __init__(self, memory_storage_config: dict[str, str]):
        logger.info("=> Init LocalStorage Success")

    def search(self, role_name: str, user_name: str, text: str, limit: int) -> list[Dict[str, str]]:
        '''检索记忆,只返回关联性最强的记忆'''
        # 查询结果，并限制数量
        results = LocalMemoryModel.objects.filter(Q(role_name=role_name) & Q(user_name=user_name)).order_by('-timestamp')[:limit]

        result_list = [{"user": result.user_text, "ai": result.role_text} for result in results]
        return result_list

    def pageQuery(self, role_name: str, user_name: str, page_num: int, page_size: int) -> list[Dict[str, str]]:
        '''分页检索记忆'''
        # 计算分页偏移量
        offset = (page_num - 1) * page_size

        # 分页查询，并提取 text 字段
        results = LocalMemoryModel.objects.filter(Q(role_name=role_name) & Q(user_name=user_name)).order_by('-timestamp')[offset:offset + page_size]
        result_list = [{"user": result.user_text, "ai": result.role_text} for result in results]
        return result_list

    def save(self, role_name: str, user_name: str, user_text: str, role_text: str, pk: int) -> None:
        '''保存记忆'''
        # text_words = jieba.cut(text, cut_all=False)
        # text_words_list = list(text_words)
        # text_tags = jieba.analyse.extract_tags(" ".join(text_words_list), topK=20)
        current_timestamp = datetime.datetime.now().isoformat()
        local_memory_model = LocalMemoryModel(
            id=pk,
            user_name=user_name,
            user_text=user_text,
            role_name=role_name,
            role_text=role_text,
            timestamp=current_timestamp
        )
        local_memory_model.save()

    def clear(self, role_name: str) -> None:
        '''清空记忆'''
        # 清除指定 role_name 的记录
        LocalMemoryModel.objects.filter(role_name=role_name).delete()
