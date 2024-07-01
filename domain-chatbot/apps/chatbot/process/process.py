import logging
import traceback
from rest_framework.generics import get_object_or_404

from ..models import RolePackageModel
from ..character import role_dialogue_example
from ..character.character_generation import singleton_character_generation
from ..config import singleton_sys_config
from ..memory import memory_storage_driver
from ..utils.datatime_utils import get_current_time_str
from ..output.realtime_message_queue import realtime_callback
from ..output.chat_history_queue import conversation_end_callback
from ..llms.function import PortraitObservation
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)


class ProcessCore():
    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    portrait_observation: PortraitObservation

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type
        # 加载自定义角色生成模块
        self.singleton_character_generation = singleton_character_generation

        # 加载用户画像识别模块
        self.portrait_observation = PortraitObservation()

    def chat(self, user_name: str, user_text: str):
        # 生成角色prompt
        character = self.singleton_character_generation.get_character(singleton_sys_config.character)
        role_name = character.role_name
        try:
            # 判断是否有角色安装包？如果有动态获取对话示例
            if character.role_package_id != -1:
                db_role_package_model = get_object_or_404(RolePackageModel, pk=character.role_package_id)
                character.examples_of_dialogue = role_dialogue_example.generate(user_name, user_text,
                                                                                db_role_package_model.dataset_json_path,
                                                                                db_role_package_model.embed_index_idx_path,
                                                                                role_name)
            prompt = self.singleton_character_generation.output_prompt(character)

            # 检索关联的短期记忆和长期记忆
            short_history = memory_storage_driver.search_short_memory(
                user_name=user_name, user_text=user_text, role_name=role_name)
            long_history = memory_storage_driver.search_long_memory(
                user_name=user_name, user_text=user_text, role_name=role_name)
            
            current_time = get_current_time_str()
            prompt = prompt.format(long_history=long_history, current_time=current_time)

            # 调用大语言模型流式生成对话
            self.llm_model_driver.chatStream(type=self.llm_model_driver_type,
                                             prompt=prompt,
                                             user_name=user_name,
                                             user_text=user_text,
                                             role_name=role_name,
                                             history=short_history,
                                             realtime_callback=realtime_callback,
                                             conversation_end_callback=conversation_end_callback)
        except Exception as e:
            traceback.print_exc()
            logger.error("chat error: %s" % str(e))
            error_message = "出现了问题，请通知开发者修复我！"
            realtime_callback(user_name=user_name, role_name=role_name, content=error_message, end_bool=True)
