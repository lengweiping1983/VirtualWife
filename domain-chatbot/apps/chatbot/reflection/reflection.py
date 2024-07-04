import json
import logging

from ..config import singleton_sys_config
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)





# class ReflectionGeneration():
#     reflection_template: ReflectionTemplate

#     def __init__(self) -> None:
#         self.reflection_template = ReflectionTemplate()

#     def generation(self, role_name: str) -> None:
#         timestamp = time.time()
#         expr = f'timestamp <= {timestamp}'
#         result = memory_storage_driver.pageQuery(
#             1, 100, expr)

#         result = [item['text'] for item in result]
#         prompt = self.reflection_template.format(result)

#         reflection_result = memory_storage_driver.chat(type=singleton_sys_config.reflection_llm_model_driver_type,
#                                                                             prompt=prompt,
#                                                                             user_name="",
#                                                                             user_text="",
#                                                                             role_name=role_name, 
#                                                                             short_history="")
#         reflection_result_arr = self.reflection_template.output_format(reflection_result)

#         # 批量写入到向量数据库中
#         for i in range(len(reflection_result_arr)):
#             item = reflection_result_arr[i].strip()
#             pk = memory_storage_driver.get_current_entity_id()
#             memory_storage_driver.save(pk, item, role_name)





class PortraitObservation:
    """用户画像实体识别"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 用户画像实体识别AI

        ## Profile
        - Assistant Name: Profile Entity Recognition AI
        - Description: 根据对话文本识别文本中包含的用户画像实体。

        ### Skill
        1. 从对话文本中识别用户画像实体。
        2. 输出用户画像实体名称。

        ### Rules
        1. 请只输出结果，不需要输出推理过程。
        2. 请识别文本中包含的用户画像实体，并且只输出实体名称。
        3. 输出应简洁，避免不必要的解释或描述。

        ## OutputFormat
        1. 请严格按照JSON数组格式输出结果。
        2. 如果识别到多个实体，应按照文本中出现的顺序列出。
        3. 输出示例如下: {"entitys":["你识别的实体名称"]}

        ## Example
        示例1：
        - Text:
        你知道张三吗？我记得李四和他关系不好
        - Output:
        {
        "entitys":["张三","李四"]
        }

        示例2：
        - Text:
        最近科比好像和奥尼尔吵架，他们在纽约时代广场打起来了呢
        - Output:
        {
        "entitys":["科比","奥尼尔"]
        }

        ## Workflow
        1. 仔细阅读用户输入，识别文本中的用户画像实体。
        2. 输出用户画像实体名称。

        作为用户画像实体识别AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入，执行<Workflow>，输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def observation(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> PortraitObservation content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            content=content，
                                            user_name=None,
                                            user_text=None,
                                            role_name=None,
                                            short_history=[])
        logger.info(f"=> PortraitObservation: {result}")
        entitys = []
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                entitys = json_data["entitys"]
            else:
                logger.warn("=> PortraitObservation 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> PortraitObservation error: %s" % str(e))
        return entitys
