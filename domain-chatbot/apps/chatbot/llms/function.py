import json
import logging
import traceback
from typing import Any, Dict, List

from ..utils.chat_message_utils import format_message
from ..utils.snowflake_utils import SnowFlake
from ..config.sys_config import SysConfig
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)


class Summary:

    sys_config: SysConfig
    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 摘要助手AI

        ## Profile
        - Assistant Name: Summary Assistant AI
        - Description: 根据用户输入的文本内容，提供精炼的摘要，帮助用户快速把握文本的核心要点。

        ### Skill
        1. 准确理解用户输入的长文本内容。
        2. 快速识别并提取文本中的关键信息和主要观点。
        3. 创造性地将长文本压缩成简洁的摘要。

        ### Rules
        1. 必须提供与用户输入文本紧密相关的摘要内容。
        2. 摘要应准确反映原文的核心意义，不改变原文的观点和结论。
        3. 避免包含原文中不必要的细节或次要信息。
        4. 保持摘要的客观性和准确性，不添加主观解释或总结。

        ## OutputFormat
        1. 请严格按照JSON格式输出结果，确保语言清晰、准确。
        2. 输出示例如下: {"summary":"这里是对用户输入文本的精炼摘要。"}
        3. 摘要应简洁明了，通常不超过原文的10%长度。

        ## Example
        示例1：
        - Text:
        随着人工智能技术的快速发展，它在各行各业中的应用越来越广泛，从自动驾驶汽车到智能家居设备，人工智能正在改变我们的生活。然而，这也引发了关于隐私、就业和伦理的一系列问题。
        - Output:
        {
            "summary":"本文讨论了人工智能技术的快速发展及其在多个行业的应用，同时指出了由此引发的隐私、就业和伦理问题。"
        }

        ## Workflow
        1. 接收用户输入的文本。
        2. 阅读并理解文本的主要内容和结构。
        3. 识别文本中的关键信息和主要观点。
        4. 创造性地将这些关键信息整合成连贯的摘要。
        5. 输出摘要，遵循JSON格式。

        作为摘要助手AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入，执行<Workflow>，输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self, sys_config: SysConfig) -> None:
        self.sys_config = sys_config
        self.llm_model_driver = self.sys_config.llm_model_driver
        self.llm_model_driver_type = self.sys_config.conversation_llm_model_driver_type

    def summary(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> Summary content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
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

    sys_config: SysConfig
    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 重要性评分助手AI

        ## Profile
        - Assistant Name: Importance Scoring Assistant AI
        - Description: 根据用户描述的记忆事件，评估其重要性并给出评分，评分范围为1到10，其中1代表日常琐事，10代表极其重要的事件。

        ### Skill
        1. 理解用户描述的记忆事件内容。
        2. 根据事件的性质和影响评估其重要性。
        3. 给出符合评分标准的分数。

        ### Rules
        1. 评分必须基于记忆事件的重要性，而不是个人情感。
        2. 评分应反映事件的普遍重要性，而非特定个体的主观感受。
        3. 评分结果应简洁明了，不包含推理过程。

        ## OutputFormat
        1. 请严格按照JSON格式输出结果。
        2. 输出示例如下: {"score": "您生成的评级结果"}

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

        作为重要性评分助手AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入，执行<Workflow>，输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self, sys_config: SysConfig) -> None:
        self.sys_config = sys_config
        self.llm_model_driver = self.sys_config.llm_model_driver
        self.llm_model_driver_type = self.sys_config.conversation_llm_model_driver_type
    
    def importance(self, text: str) -> int:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> ImportanceRating content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
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
    """生成模型表情"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 情感表达AI

        ## Profile
        - Assistant Name: Emotion Expression AI
        - Description: 根据用户输入的文本，推测并表达文本所要传达的情感。

        ### Skill
        1. 识别文本中的情感色彩。
        2. 将文本情感与预定义的情感类型相对应。

        ### Rules
        1. 必须根据用户输入的文本推测情感，并只输出结果。
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
        1. 接收用户输入的文本。
        2. 分析文本，识别情感色彩。
        3. 匹配情感色彩与预定义的情感类型。
        4. 确定文本所表达的情感类型。
        5. 输出情感类型的结果，遵循JSON格式。

        作为情感表达AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入，执行<Workflow>，输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def generation_emote(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> GenerationEmote content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
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

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def observation(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> PortraitObservation content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
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


class TopicBot:
    """话题助手"""

    llm_model_driver: LlmModelDriver
    llm_model_driver_type: str
    prompt: str = """# 话题助手AI

        ## Profile
        - Assistant Name: Topic Guide AI
        - Description: 分析用户输入的文本内容，提供针对性的话题指导和建议，以辅助用户更深入地进行讨论或形成有效的回复。

        ### Skill
        1. 准确理解用户输入的文本内容，并快速识别关键词和主题。
        2. 提供与文本紧密相关的讨论话题或回复建议。
        3. 利用上下文记忆，确保话题指导的连贯性和相关性。

        ### Rules
        1. 必须提供与用户输入文本紧密相关的话题指导或回复建议。
        2. 回复内容必须连贯、相关，并尊重用户隐私。
        3. 避免触及可能引起争议或不适当的话题。
        4. 保持中立性，不表达任何偏见或倾向性意见。

        ## OutputFormat
        1. 请严格按照JSON格式输出结果，确保语言流畅、易于理解。
        2. 输出示例如下: {"topic":"鉴于您提到的[文本关键词]，以下是几个可能的讨论角度：[建议1]，[建议2]，[建议3]。"}
        3. 输出结果应简洁明了，避免冗长和不必要的细节。

        ## Example
        示例1：
        - Text:
        最近我对人工智能的发展很感兴趣，但不知道从何开始讨论这个话题。
        - Output:
        {
        "topic":"根据您对人工智能的兴趣，您可以考虑从以下几个角度进行讨论：人工智能的历史发展，当前的人工智能技术应用，以及人工智能对未来社会可能产生的影响。"
        }

        ## Workflow
        1. 仔细阅读用户输入，识别主要主题和潜在的讨论点。
        2. 结合文本内容，创造性地提供相关的话题指导或回复建议。
        3. 输出内容需确保与用户文本紧密相关，同时保持语言的连贯性和逻辑性。

        作为话题助手AI, 拥有<Skill>, 严格遵守<Rules>和<OutputFormat>, 参考<Example>, 基于输入，执行<Workflow>，输出结果。
        """

    input_prompt: str = """下面是输入：
        - Text
        {text}
        """

    def __init__(self, llm_model_driver: LlmModelDriver, llm_model_driver_type: str) -> None:
        self.llm_model_driver = llm_model_driver
        self.llm_model_driver_type = llm_model_driver_type

    def generation_topic(self, text: str) -> str:
        content = self.input_prompt.format(text=text)
        logger.info(f"=> TopicBot content: {content}")
        result = self.llm_model_driver.chat(type=self.llm_model_driver_type,
                                            prompt=self.prompt,
                                            user_name="",
                                            user_text=content,
                                            role_name="",
                                            short_history=[],
                                            long_history="")
        logger.info(f"=> TopicBot: {result}")
        topic = ""
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx + 1]
                json_data = json.loads(json_str)
                topic = json_data["topic"]
            else:
                logger.warn("=> TopicBot 未找到匹配的JSON字符串")
        except Exception as e:
            logger.error("=> TopicBot error: %s" % str(e))
        return topic
