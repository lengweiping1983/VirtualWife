import os
import logging
from typing import List
from litellm import completion
from litellm import embedding

from ...utils.chat_message_utils import format_chat_text, format_user_message
from ...utils.str_utils import remove_spaces_and_tabs
from ..base_llm_model import ChatHistroy, BaseLlmModel


logger = logging.getLogger(__name__)


class OpenAIGeneration(BaseLlmModel):
    # completion_model_name: str = "gpt-4o"
    completion_model_name: str = "gpt-3.5-turbo"
    embedding_model_name: str = "text-embedding-ada-002"
    temperature: float = 0.7
    openai_base_url: str
    openai_api_key: str

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_base_url = os.environ["OPENAI_BASE_URL"]
        self.openai_api_key = os.environ["OPENAI_API_KEY"]

    def chat(self,
             prompt: str,
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: list[ChatHistroy],
             long_history: str) -> str:
        messages = []
        if prompt is not None and prompt != "":
            messages.append({"role": "system", "content": prompt})
        messages.append({"role": "user", "content": user_text})
        if self.openai_base_url:
            response = completion(
                model=self.completion_model_name,
                messages=messages,
                api_base=self.openai_base_url,
                temperature=self.temperature,
            )
        else:
            response = completion(
                model=self.completion_model_name,
                messages=messages,
                temperature=self.temperature,
            )
        llm_result_text = response.choices[0].message.content if response.choices else ""
        return llm_result_text

    async def chatStream(self,
                         prompt: str,
                         user_name: str,
                         user_text: str,
                         role_name: str,
                         history: list[str, str],
                         realtime_callback=None,
                         conversation_end_callback=None):
        messages = []
        if prompt is not None and prompt != "":
            messages.append({"role": "system", "content": prompt})
        for item in history:
            print("chatStream item=")
            print(item)
            messages.append({"role": "user", "content": item["user"]})
            messages.append({"role": "assistant", "content": item["ai"]})
        messages.append({"role": "user", "content": format_user_message(user_name, user_text, need_speaker=True)})
        if self.openai_base_url:
            response = completion(
                model=self.completion_model_name,
                messages=messages,
                api_base=self.openai_base_url,
                stream=True,
                temperature=self.temperature,
            )
        else:
            response = completion(
                model=self.completion_model_name,
                messages=messages,
                stream=True,
                temperature=self.temperature,
            )

        role_text = ""
        for event in response:
            if not isinstance(event, dict):
                event = event.model_dump()
            if isinstance(event["choices"], List) and len(event["choices"]) > 0:
                event_text = event["choices"][0]["delta"]["content"]
                if isinstance(event_text, str) and event_text != "":
                    content = event_text
                    # 过滤空格和制表符
                    content = remove_spaces_and_tabs(content)
                    if content == "":
                        continue
                    role_text += content
                    if realtime_callback:
                        realtime_callback(user_name, role_name, content, False)  # 调用实时消息推送的回调函数

        if realtime_callback:
            realtime_callback(user_name, role_name, "", True)
        
        role_text = format_chat_text(user_name, role_name, role_text)
        if conversation_end_callback:
            conversation_end_callback(user_name, user_text, role_name, role_text)  # 调用对话结束消息的回调函数

    def get_embedding(self, text: str):
        text = text.replace("\n", " ")
        if self.openai_base_url:
            response = embedding(
                model=self.embedding_model_name,
                input=[text],
                api_base=self.openai_base_url
            )
        else:
            response = embedding(
                model=self.embedding_model_name,
                input=[text]
            )
        if response.data and len(response.data) > 0:
            text_embedding = response.data[0]["embedding"]
            return text_embedding
        return None
