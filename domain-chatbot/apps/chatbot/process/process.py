import json
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
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)


class ProcessCore():
    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type
        # 加载自定义角色生成模块
        self.singleton_character_generation = singleton_character_generation

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
                user_name=user_name, user_text=user_text, role_name=role_name, limit=singleton_sys_config.short_memory_num)
            long_history = memory_storage_driver.search_long_memory(
                user_name=user_name, user_text=user_text, role_name=role_name, limit=singleton_sys_config.long_memory_num)
            
            current_time = get_current_time_str()
            prompt = prompt.format(long_history=long_history, current_time=current_time)

            # 调用大语言模型流式生成对话
            self.llm_model_driver.chatStream(type=self.llm_model_driver_type,
                                             prompt=prompt,
                                             content=None,
                                             user_name=user_name,
                                             user_text=user_text,
                                             role_name=role_name,
                                             short_history=short_history,
                                             automatic=0,
                                             realtime_callback=realtime_callback,
                                             conversation_end_callback=conversation_end_callback)
        except Exception as e:
            traceback.print_exc()
            logger.error("chat error: %s" % str(e))
            error_message = "出现了问题，请通知开发者来修复！"
            realtime_callback(user_name=user_name, role_name=role_name, content=error_message, automatic=9, end_bool=True)


class EmotionBot():
    """情感机器人"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 情感机器人

        ### Skill
        1. 你是 {role_name} 。
        2. 你需要分析与准确理解 {user_name} 和你之间的对话内容，你需要判断 {user_name} 的情感，并判断是否需要推理出引导性话语。如果需要，请提供简短且有效的引导性话语，帮助 {user_name} 更好地应对当前情感。

        ### Rules
        1. 相关性: 仅回复与对话内容紧密相关的情感。
        2. 准确性: 基于对话内容合理推断，不做无依据的判断。
        3. 尊重隐私: 避免触及用户敏感信息，确保所有分析结果不侵犯用户隐私。
        4. 中立性: 保持中立和客观，不表达偏见或倾向性意见。
        5. 敏感处理: 对潜在敏感或痛苦的情感需特别小心，确保语言温和、不引发二次伤害。

        ### OutputFormat
        1. 以纯文本方式回复，避免特殊字符。
        2. 确保语言流畅、易于理解。
        3. 输出结果应简洁明了，避免冗长和不必要的细节。

        ### Workflow
        1. 接收对话内容：你会仔细阅读并收集 {user_name} 和你之间的对话文本。
        2. 分析对话：你将深入理解对话内容，分析情感倾向和语境。
        3. 评估需求：基于对话内容和情感，你将判断是否需要生成引导性话语。
        4. 生成引导性话语：如果需要，你将提供简短、有效、且针对性强的引导性话语，以帮助 {user_name} 更好地应对当前情感。如果不需要，你将输出“null”。
        5. 输出回复：你将以纯文本形式输出引导性话语，你的回复应该简短，最多包含三句话，每句话不超过20个字。

        你是 {role_name} , 拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 基于对话内容，执行 <Workflow> , 输出结果。
        """
    input_prompt: str = """下面是对话内容：
        {text}
        """
    
    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def generation_emotion(self, user_name: str, role_name: str, text: str):
        prompt=self.prompt.format(user_name=user_name, role_name=role_name)
        content = self.input_prompt.format(text=text)
        logger.info(f"=> EmotionBot content: {content}")
        try:
            # 调用大语言模型流式生成对话
            self.llm_model_driver.chatStream(type=self.llm_model_driver_type,
                                             prompt=prompt,
                                             content=content,
                                             user_name=user_name,
                                             user_text=None,
                                             role_name=role_name,
                                             short_history=None,
                                             automatic=2,
                                             realtime_callback=realtime_callback,
                                             conversation_end_callback=conversation_end_callback)
        except Exception as e:
            traceback.print_exc()
            logger.error("=> EmotionBot error: %s" % str(e))


class TopicBot:
    """话题机器人"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 话题机器人

        ### Skill
        1. 你是 {role_name}。
        2. 你需要分析与准确理解 {user_name} 和你之间的对话内容，你判断是否需要推理出针对性的话题。如果需要，请提供简短且有效的话题，辅助 {user_name} 更深入地讨论。
        3. 准确理解对话内容，快速识别关键词和主题。
        4. 提供与对话紧密相关的讨论话题。
        5. 利用上下文记忆，确保话题的连贯性和相关性。

        ### Rules
        1. 相关性: 必须提供与对话内容紧密相关的话题。
        2. 连贯性: 回复内容必须连贯、相关，并尊重用户隐私。
        3. 敏感处理: 避免触及可能引起争议或不适当的话题，确保所有话题适合当前对话背景。
        4. 中立性: 保持中立和客观，不表达任何偏见或倾向性意见。
        5. 实用性: 提供的话题应具备讨论价值或实用性，能够引导对话深入或提供有效回复。

        ### OutputFormat
        1. 以纯文本方式回复，避免特殊字符。
        2. 确保语言流畅、易于理解。
        3. 输出结果应简洁明了，避免冗长和不必要的细节。

        ### Workflow
        1. 接收对话内容：你会仔细阅读并收集 {user_name} 和你之间的对话文本。
        2. 分析对话: 仔细阅读并理解对话内容，识别主要主题和潜在的讨论点。
        3. 评估需求: 基于对话内容，判断是否需要生成话题。
        4. 生成话题: 如需提供话题，根据对话中的关键词和主题，创造性地提供相关的讨论话题。如果不需要，你将输出“null”。
        5. 输出结果: 你将以纯文本形式输出话题，你的回复应该简短，最多包含三句话，每句话不超过20个字。

        你是 {role_name} , 拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 基于对话内容，执行 <Workflow> , 输出结果。
        """
    input_prompt: str = """下面是对话内容：
        {text}
        """
    
    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def generation_topic(self, user_name: str, role_name: str, text: str):
        prompt=self.prompt.format(user_name=user_name, role_name=role_name)
        content = self.input_prompt.format(text=text)
        logger.info(f"=> TopicBot content: {content}")
        try:
            # 调用大语言模型流式生成对话
            self.llm_model_driver.chatStream(type=self.llm_model_driver_type,
                                             prompt=prompt,
                                             content=content,
                                             user_name=user_name,
                                             user_text=None,
                                             role_name=role_name,
                                             short_history=None,
                                             automatic=1,
                                             realtime_callback=realtime_callback,
                                             conversation_end_callback=conversation_end_callback)
        except Exception as e:
            traceback.print_exc()
            logger.error("=> TopicBot error: %s" % str(e))
