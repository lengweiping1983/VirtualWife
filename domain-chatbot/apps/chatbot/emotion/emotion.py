import json
import logging

from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)


class EmotionRecognition():
    """情感识别"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    input_prompt: str = """你现在是一名情感识别AI，这是我的文本"{input}"，请识别出它属于哪一种情感分类，我提供了一些常见的情感分类，如果不在常见的情感分类中，你可以自己推理出情感分类。
    常见的情感分类
    ```
    1. 分手或者离婚
    2. 冲突或沟通问题
    3. 面对亲人的离世
    4. 处理宠物的离去
    5. 工作压力和疲倦
    6. 财务担忧和不确定性
    7. 市场压力
    8. 学术压力
    9. 精神和信仰
    10. 焦虑和恐慌
    11. 抑郁和情绪低落
    12. 适应新的工作或角色
    13. 寻找生活的意义和目的
    14. 创伤后应激障碍
    15. 支持所爱的人或朋友
    16. 搬到一个新的城市或国冢
    17. 职业转型
    18. 为人父母和养育子女的烦恼
    19. 自卑或缺乏自信
    20. 对身体形象的不自信或者饮食失调
    21. 文化认同和归属感
    22. 学业压力或压力
    23. 失业或事业受挫
    24. 育儿的挑战和为人父甘的内疚
    25. 兄弟姐妹间的竞争或家庭冲突
    26. 从身体或精神虐待中生存和恢复
    27. 从性侵犯或家庭暴力中康复
    28. 从虐待中康复
    29. 成瘾与康复
    ```
    请严格按照以JSON格式输出结果，输出示例如下：
    
    ```
    {"intent":"你识别的情感分类"}
    ```
    """

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def recognition(self, user_name: str, user_text: str) -> str:
        prompt = self.input_prompt.format(input=user_text)
        result = self.llm_model_driver.chat(
            type=self.llm_model_driver_type,
            prompt=prompt,
            user_name="",
            user_text="", 
            role_name="",
            short_history=[],
            long_history="")
        logger.info(f"=> EmotionRecognition: {result}")
        intent = ""
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                intent = json_data["intent"]
            else:
                logger.warn("=> EmotionRecognition 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> EmotionRecognition error: %s" % str(e))
        return intent


class EmotionRespond():
    """情感响应"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    input_prompt: str = """{user_name}的对话“{user_text}”，
    {user_name}的情感分类“{intent}”，
    关联的上下文“{histroy}”
    请根据上述情况生成你的对话策略，你的对话策略应该简短，最多包含三句话，每句话不超过20个字。
    ```
    """
    output_prompt: str = """
    请严格按照JSON格式输出结果，输出示例如下：
    ```
    {"respond":"你生成的对话策略"}
    ```
    """

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def respond(self, user_name: str, user_text: str, intent: str, long_history: str) -> str:
        prompt = self.input_prompt.format(
            user_name=user_name, user_text=user_text, intent=intent, histroy=long_history) + self.output_prompt
        result = self.llm_model_driver.chat(
            type=self.llm_model_driver_type,
            prompt=prompt,
            user_name="",
            user_text="", 
            role_name="",
            short_history=[],
            long_history="")
        logger.info(f"=> EmotionRespond: {result}")
        intent = ""
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                intent = json_data["respond"]
            else:
                logger.warn("=> EmotionRespond 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> EmotionRespond error: %s" % str(e))
        return intent


class GenerationEmotionRespondChatPropmt():
    """根据响应生成对话propmt"""

    prompt: str = """{character_prompt}
        {user_name}当前的情绪状态：{respond}
        """

    def generation_prompt(self, user_name: str, respond: str, character_prompt: str):
        return self.prompt.format(user_name=user_name, respond=respond, character_prompt=character_prompt)


