import os
import logging
from typing import Any, Dict, List
from litellm import completion
from litellm import embedding

from ...utils.chat_message_utils import format_chat_text
from ...utils.str_utils import remove_spaces_and_tabs
from ..base_llm_model import BaseLlmModel


logger = logging.getLogger(__name__)


class OllamaGeneration(BaseLlmModel):
    completion_model_name: str
    temperature: float = 0.7
    ollama_base_url: str

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        self.ollama_base_url = os.environ.get("OLLAMA_API_BASE")
        self.completion_model_name = "ollama/" + os.environ.get("OLLAMA_API_MODEL_NAME")

    def chat(self,
             prompt: str,
             content: str,
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: List[Dict[str, str]],
             model_name: str=None,
             temperature: float=-1) -> str:
        messages = self.get_messages(prompt=prompt,
                                     content=content,
                                     user_name=user_name,
                                     user_text=user_text,
                                     role_name=role_name,
                                     short_history=short_history)
        completion_model_name = model_name if model_name is not None and model_name != "" else self.completion_model_name
        temperature = temperature if temperature > 0 else self.temperature
        if self.ollama_base_url:
            response = completion(
                model=completion_model_name,
                messages=messages,
                api_base=self.ollama_base_url,
                temperature=temperature,
            )
        else:
            response = completion(
                model=completion_model_name,
                messages=messages,
                temperature=temperature,
            )
        llm_result_text = response.choices[0].message.content if response.choices else ""
        return llm_result_text

    async def chatStream(self,
                         prompt: str,
                         content: str,
                         user_name: str,
                         user_text: str,
                         role_name: str,
                         short_history: List[Dict[str, str]],
                         automatic: int=0,
                         realtime_callback=None,
                         conversation_end_callback=None,
                         model_name: str=None,
                         temperature: float=-1):
        messages = self.get_messages(prompt=prompt,
                                     content=content,
                                     user_name=user_name,
                                     user_text=user_text,
                                     role_name=role_name,
                                     short_history=short_history)
        completion_model_name = model_name if model_name is not None and model_name != "" else self.completion_model_name
        temperature = temperature if temperature > 0 else self.temperature
        if self.ollama_base_url:
            response = completion(
                model=completion_model_name,
                messages=messages,
                api_base=self.ollama_base_url,
                stream=True,
                temperature=temperature,
            )
        else:
            response = completion(
                model=completion_model_name,
                messages=messages,
                stream=True,
                temperature=temperature,
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
                        realtime_callback(user_name, role_name, content, automatic, False)  # 调用实时消息推送的回调函数

        if realtime_callback:
            realtime_callback(user_name, role_name, "", automatic, True)
        
        role_text = format_chat_text(user_name, role_name, role_text)
        if conversation_end_callback:
            conversation_end_callback(user_name, user_text, role_name, role_text, automatic)  # 调用对话结束消息的回调函数

    def get_embedding(self, text: str):
        text = text.replace("\n", " ")
        if self.ollama_base_url:
            response = embedding(
                model=self.embedding_model_name,
                input=[text],
                api_base=self.ollama_base_url
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
