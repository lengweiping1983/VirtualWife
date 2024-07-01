import json
import logging

from ..llms.llm_model_strategy import LlmModelDriver
from ..memory import memory_storage_driver

logger = logging.getLogger(__name__)


class PortraitAnalysis:
    """用户画像分析"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 用户画像分析AI

    ## Profile
    - Description: 根据记忆推理和更新用户画像
    
    ### Skill
    1. 根据记忆推理和更新用户画像
    
    ### Rules
    1. 请只输出结果，不需要输出推理过程
    2. 用户画像的信息不能出现重复
    3. 请使用中文输出用户画像数据
    4. 只输出当前用户的画像数据
    5. 输出的用户画像数据，严格遵循用户画像的数据结构
    6. <Example>中的Text和Personas仅提供参考，请不要作为你进行用户画像分析的参数

    ## OutputFormat
    1. 请严格以JSON数组格式输出结果。
    2. 输出示例如下:
    {
        "personas": {
            "Persona": "描述用户的职业，如果没有设置为未知",
            "Fictional name": "描述用户的名称，如果没有设置为未知",
            "Sex": "描述用户的性别，如果没有设置为未知",
            "Job title/major responsibilities": "描述用户的职责和工作内容，如果没有设置为未知",
            "Demographics": "描述用户的人际关系，家庭关系，如果没有设置为未知",
            "Goals and tasks": "描述用户最近目标和想法，如果没有设置为未知",
            "hobby": "描述用户的爱好，如果没有设置为未知",
            "promise": "描述用户与别人的约定，如果没有设置为未知",
            "topic": "描述用户喜欢聊什么话题，如果没有设置为未知"
        }
    }
    
    ## Example:
    示例1：
    - Text:
    张三说我最近和朋友吵架了
    爱莉说没关系，你和我说说
    张三说他说想玩LOL，可我已经不喜欢玩LOL了，所以吵架了
    爱莉说哦，我觉得这个是小事呀
    - Personas:
    {
      "Persona": "软件工程师",
      "Fictional name": "张三",
      "Sex":"男",
      "Job title/major responsibilities": "人工智能专家",
      "Demographics": "人工智能博士",
      "Goals and tasks": "专注人工智能领域;",
      "hobby": "他喜欢玩游戏和电竞，比如LoL、泰拉瑞亚",
      "promise": "和爱莉约好周末去吃烧烤",
      "topic": "喜欢聊动漫的话题"
    }
    - Output:
    {
    "personas": {
        "Persona": "软件工程师",
        "Fictional name": "张三",
        "Sex":"男",
        "Job title/major responsibilities": "人工智能专家",
        "Demographics": "人工智能博士",
        "Goals and tasks": "专注人工智能领域;",
        "hobby": "他喜欢玩游戏和电竞，比如泰拉瑞亚",
        "promise": "和爱莉约好周末去吃烧烤",
        "topic": "喜欢聊动漫的话题"
    }
    }
    
    ## Workflow
    1. 推理和分析输入Text和Personas, 分析出需要新增和更新的用户画像信息
    2. 输出最终的用户画像信息

    你作为用户画像分析AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入, 执行<Workflow>, 输出结果。
    下面是输入：
    - Text
    {text}
    - Personas
    {portrait}
    """

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def analysis(self, text: str, portrait: str) -> str:
        content = self.prompt.format(text=text, portrait=portrait)
        logger.info(f"=> PortraitAnalysis content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=None,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
        logger.info(f"=> PortraitAnalysis: {result}")
        personas = ""
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                personas = json_data["personas"]
            else:
                logger.warn("=> PortraitAnalysis 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> PortraitAnalysis error: %s" % str(e))
        return personas


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
#                                                                             short_history="",
#                                                                             long_history="")
#         reflection_result_arr = self.reflection_template.output_format(reflection_result)

#         # 批量写入到向量数据库中
#         for i in range(len(reflection_result_arr)):
#             item = reflection_result_arr[i].strip()
#             pk = memory_storage_driver.get_current_entity_id()
#             memory_storage_driver.save(pk, item, role_name)