import datetime
import logging
from typing import Any, Dict, List
from django.db.models import Q


from ...models import LocalMemoryModel


logger = logging.getLogger(__name__)


class LocalStorage:

    def __init__(self, sys_config_json: any):
        logger.info("=> Init LocalStorage Success")

    def pageQuery(self, role_name: str, user_name: str, page_num: int, page_size: int,
                  summary: int=-1, topic: int=-1, emotion: int=-1, automatic: int=0, order: str="desc") -> List[Dict[str, str]]:
        '''分页检索记忆'''
        # 计算分页偏移量
        offset = (page_num - 1) * page_size

        condition = Q(role_name=role_name) & Q(user_name=user_name) & Q(deleted=0)
        if summary >= 0:
            condition = condition & Q(summary=summary)
        if topic >= 0:
            condition = condition & Q(topic=topic)
        if emotion >= 0:
            condition = condition & Q(emotion=emotion)
        if automatic >= 0:
            condition = condition & Q(automatic=automatic)
        order_str = "-timestamp" if order == "desc" else "timestamp"
        results = LocalMemoryModel.objects.filter(condition).order_by(order_str)[offset:offset + page_size]
        result_list = [{"id": result.id, "user": result.user_text, "assistant": result.role_text} for result in results]
        if order == "desc":
            result_list.reverse()
        return result_list

    def save(self, role_name: str, user_name: str, user_text: str, role_text: str, automatic: int, pk: int) -> None:
        '''保存记忆'''
        current_timestamp = datetime.datetime.now().isoformat()
        local_memory_model = LocalMemoryModel(
            id=pk,
            user_name=user_name,
            user_text=user_text,
            role_name=role_name,
            role_text=role_text,
            timestamp=current_timestamp,
            automatic=automatic,
            summary=0,
            topic=0,
            emotion=0,
            deleted=0)
        local_memory_model.save()

    def update_list_summary(self, list: List[Dict[str, str]]) -> None:
        for dict in list:
            self.update_summary(dict.get("id"))

    def update_summary(self, pk: int) -> None:
        if pk:
            obj = LocalMemoryModel.objects.get(id=pk)
            if obj:
                obj.summary = 1
                obj.save()
    
    def update_list_topic(self, list: List[Dict[str, str]]) -> None:
        for dict in list:
            self.update_topic(dict.get("id"))

    def update_topic(self, pk: int) -> None:
        if pk:
            obj = LocalMemoryModel.objects.get(id=pk)
            if obj:
                obj.topic = 1
                obj.save()

    def update_list_emotion(self, list: List[Dict[str, str]]) -> None:
        for dict in list:
            self.update_emotion(dict.get("id"))

    def update_emotion(self, pk: int) -> None:
        if pk:
            obj = LocalMemoryModel.objects.get(id=pk)
            if obj:
                obj.emotion = 1
                obj.save()

    def clear(self, role_name: str) -> None:
        '''清空记忆'''
        # 清除指定 role_name 的记录
        LocalMemoryModel.objects.filter(role_name=role_name).delete()
