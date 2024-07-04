import json
import logging
import traceback
from typing import Any, Dict, List

from ..config import singleton_sys_config
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)


class Summary:

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 摘要

        ## Skill
        1. 你是 {role_name} 。
        2. 你需要分析与准确理解 {user_name} 和你之间的对话内容，快速识别并提取对话中的关键信息和主要观点，生成简洁的摘要，帮助 {user_name} 快速掌握对话的核心要点。

        ## Rules
        1. 提供与对话紧密相关的摘要内容。
        2. 摘要应准确反映对话的核心意义，不改变对话的观点和结论。
        3. 避免包含对话中的不必要细节或次要信息。
        4. 保持摘要的客观性和准确性，不添加主观解释或总结。

        ## OutputFormat
        1. 严格按照 JSON 格式输出结果，确保语言清晰、准确。
        2. 输出示例: {output_example}
        3. 摘要应简洁明了，通常不超过原对话内容的 10% 长度。

        ## Workflow
        1. 接收对话内容：你会仔细阅读并收集 {user_name} 和你之间的对话文本。
        2. 阅读并理解对话的主要内容和结构。
        3. 识别对话中的关键信息和主要观点。
        4. 将这些关键信息整合成连贯的摘要。
        5. 输出摘要，遵循 JSON 格式。

        你是 {role_name} , 拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 基于对话内容, 执行 <Workflow> , 输出结果。
        """
    output_example: str = """{"summary": "这里是你提取的精炼摘要。"}"""
    input_prompt: str = """下面是对话内容：
        {text}
        """
    
    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def summary(self, user_name: str, role_name: str, text: str) -> str:
        prompt=self.prompt.format(user_name=user_name, role_name=role_name, output_example=self.output_example)
        content = self.input_prompt.format(text=text)
        logger.info(f"=> Summary content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=prompt,
                                            content=content,
                                            user_name=None,
                                            user_text=None,
                                            role_name=None,
                                            short_history=[])
        logger.info(f"=> Summary: {result}")
        summary = text
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                summary = json_data["summary"]
            else:
                logger.warn("=> Summary 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> Summary error: %s" % str(e))
        return summary


class ImportanceRating:

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 重要性评分

        ## Skill
        1. 理解描述的记忆事件，评估其重要性并给出评分，评分范围为1到10，其中1代表日常琐事，10代表极其重要的事件。
        2. 根据事件的性质和影响评估其重要性。
        3. 给出符合评分标准的分数。

        ## Rules
        1. 评分必须基于记忆事件的重要性，而不是个人情感。
        2. 评分应反映事件的普遍重要性，而非特定个体的主观感受。
        3. 评分结果应简洁明了，不包含推理过程。

        ## OutputFormat
        1. 请严格按照JSON格式输出结果。
        2. 输出示例如下: {"score": "您生成的评分结果"}

        ## Example
        示例1：
        - Text:
        记得每天早上刷牙。
        - Output:
        {
            "score": "1"
        }

        示例2：
        - Text
        收到你梦想中的大学的录取通知书。
        - Output:
        {
            "score": "10"
        }

        你拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 参考<Example>, 基于输入, 执行 <Workflow> , 输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type
    
    def importance(self, text: str) -> int:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> ImportanceRating content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            content=content,
                                            user_name=None,
                                            user_text=None,
                                            role_name=None,
                                            short_history=[])
        logger.info(f"=> ImportanceRating: {result}")
        score = 3
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                score = int(json_data["score"])
            else:
                logger.warn("=> ImportanceRating 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> ImportanceRating error: %s" % str(e))
        return score


class GenerationEmote():
    """生成人物表情"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 情感表达

        ## Skill
        1. 根据输入的文本，识别文本中的情感色彩，推测并表达文本所要传达的情感。
        2. 将文本情感与预定义的情感类型相对应。

        ## Rules
        1. 必须根据输入的文本推测情感，并只输出结果。
        2. 识别的情感类型仅限于五种："neutral", "happy", "angry", "sad", "relaxed"。
        3. 输出结果应为小写字母。
        4. 不需要输出推理过程。
        5. 确保输出的情感类型与文本的情感色彩一致，避免矛盾。

        ## OutputFormat
        1. 严格按照JSON格式输出结果。
        2. 输出示例：{"emote":"your reasoning emotions"}
        3. 输出结果应仅包含情感类型，不应包含其他信息。

        ## Example
        - Text:
        我对假期感到非常兴奋！
        - Output:
        {"emote":"happy"}

        ## Workflow
        1. 接收输入的文本。
        2. 分析文本，识别情感色彩。
        3. 匹配情感色彩与预定义的情感类型。
        4. 确定文本所表达的情感类型。
        5. 输出情感类型的结果，遵循JSON格式。

        你拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 参考 <Example> , 基于输入的文本，执行 <Workflow> , 输出结果。
        """

    input_prompt: str = """下面是输入的文本：
        - Text
        {text}
        """

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def generation_emote(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> GenerationEmote content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            content=content,
                                            user_name=None,
                                            user_text=None,
                                            role_name=None,
                                            short_history=[],
                                            model_name="gpt-3.5-turbo")
        logger.info(f"=> GenerationEmote: {result}")
        emote = "neutral"
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                emote = json_data["emote"]
            else:
                logger.warn("=> GenerationEmote 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> GenerationEmote error: %s" % str(e))
        return emote


class PortraitAnalysis:
    """用户画像分析"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 用户画像分析

        ## 角色设定
        - 你是 {role_name}，一个专业的用户画像分析师。

        ## Skill
        1. 你需要分析与准确理解 {user_name} 和你之间的对话内容。
        2. 根据对话内容和记忆推理，更新用户画像。

        ## Rules
        1. 只输出用户画像的结果，不包括推理过程。
        2. 用户画像信息应避免重复。
        3. 使用中文输出用户画像数据。
        4. 只输出当前用户的画像数据。
        5. 严格遵循用户画像的数据结构。
        6. 下面<Example> 部分仅供格式参考，不作为分析参数。

        ## OutputFormat
        1. 以JSON数组格式输出结果。
        2. 示例格式：
           {output_example}
        3. 画像数据应简洁明了，避免冗长和不必要的细节。

        ## Example
        示例1：
        ### {user_name} 之前的用户画像：
        {example1_input}

        ### {user_name} 和你的对话内容：
        张三：我最近和朋友吵架了
        你：没关系，你和我说说
        张三：他说想玩LOL，可我已经不喜欢玩LOL了，所以吵架了
        你：哦，我觉得这个是小事呀

        ### 输出结果：
        {example1_output}

        ## Workflow
        1. 接收对话内容：仔细阅读并收集 {user_name} 和你之间的对话文本。
        2. 分析对话：深入理解对话内容。
        3. 评估需求：根据对话内容更新之前用户画像，生成新的用户画像。
        4. 输出结果：以JSON数组格式输出，用户画像数据应简洁明了。

    你是 {role_name} , 拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat>, 参考<Example> , 基于对话内容，执行 <Workflow> , 输出结果。
        """
    output_example: str = """{
            "portrait": {
                "Persona": "描述用户的职业，如果没有设置为未知",
                "Fictional name": "描述用户的名称，如果没有设置为未知",
                "Sex": "描述用户的性别，如果没有设置为未知",
                "Job title/major responsibilities": "描述用户的职责和工作内容，如果没有设置为未知",
                "Demographics": "描述用户的人际关系，家庭关系，如果没有设置为未知",
                "Goals and tasks": "描述用户最近目标和想法，如果没有设置为未知",
                "Hobby": "描述用户的爱好，如果没有设置为未知",
                "Promise": "描述用户与别人的约定，如果没有设置为未知",
                "Topic": "描述用户喜欢聊什么话题，如果没有设置为未知"
            }
        }"""
    example1_input: str = """{
            "portrait": {
                "Persona": "软件工程师",
                "Fictional name": "张三",
                "Sex": "男",
                "Job title/major responsibilities": "人工智能专家",
                "Demographics": "人工智能博士",
                "Goals and tasks": "专注人工智能领域",
                "Hobby": "玩游戏和电竞，如LoL、泰拉瑞亚",
                "Promise": "和爱莉约好周末去吃烧烤",
                "Topic": "喜欢聊动漫的话题"
            }
        }"""
    example1_output: str = """{
            "portrait": {
                "Persona": "软件工程师",
                "Fictional name": "张三",
                "Sex": "男",
                "Job title/major responsibilities": "人工智能专家",
                "Demographics": "人工智能博士",
                "Goals and tasks": "专注人工智能领域",
                "Hobby": "玩游戏和电竞，如泰拉瑞亚",
                "Promise": "和爱莉约好周末去吃烧烤",
                "Topic": "喜欢聊动漫的话题"
            }
        }"""
    portrait_prompt: str = """### {user_name} 之前的用户画像：
        {portrait}
        """
    input_prompt: str = """### {user_name} 和你的对话内容：
        {text}
        """
    
    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def portrait(self, user_name: str, role_name: str, text: str, portrait: str) -> str:
        prompt=self.prompt.format(user_name=user_name, role_name=role_name,
                                  output_example=self.output_example,
                                  example1_input=self.example1_input,
                                  example1_output=self.example1_output)
        portrait = self.portrait_prompt.format(user_name=user_name, portrait=portrait)
        content = self.input_prompt.format(user_name=user_name, text=text)
        logger.info(f"=> PortraitAnalysis content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=prompt,
                                            content=portrait + "\n" + content,
                                            user_name=None,
                                            user_text=None,
                                            role_name=None,
                                            short_history=[])
        logger.info(f"=> PortraitAnalysis: {result}")
        portrait = {}
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                portrait = json.loads(json_str)
                if portrait["portrait"]:
                    return portrait
            else:
                logger.warn("=> PortraitAnalysis 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> PortraitAnalysis error: %s" % str(e))
        return portrait


class PortraitObservation:
    """用户画像实体识别"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 用户画像实体识别

        ## 角色设定
        - 你是 {role_name}，一个专业的用户画像实体识别分析师。

        ## Skill
        1. 从文本中识别用户画像实体。
        2. 输出用户画像实体名称。

        ## Rules
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
        1. 仔细阅读，识别文本中的用户画像实体。
        2. 输出用户画像实体名称。

        你是 {role_name}, 拥有 <Skill> , 严格遵守 <Rules> 和 <OutputFormat> , 参考<Example>, 基于文本，执行 <Workflow> ，输出结果。
        """

    input_prompt: str = """下面是文本：
        - Text
        {text}
        """

    def __init__(self) -> None:
        self.llm_model_driver = singleton_sys_config.llm_model_driver
        self.llm_model_driver_type = singleton_sys_config.conversation_llm_model_driver_type

    def observation(self, user_name: str, role_name: str, text: str) -> str:
        prompt=self.prompt.format(user_name=user_name, role_name=role_name)
        content = self.input_prompt.format(text=text)
        logger.info(f"=> PortraitObservation content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=prompt,
                                            content=content,
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
