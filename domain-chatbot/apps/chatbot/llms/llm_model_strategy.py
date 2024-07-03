from __future__ import annotations
import threading
import asyncio
from typing import Any, Dict, List

from .base_llm_model import BaseLlmModel
from .openai.openai_chat_robot import OpenAIGeneration
from .ollama.ollama_chat_robot import OllamaGeneration


class LlmModelDriver:

    def __init__(self):
        self.openai = OpenAIGeneration()
        self.ollama = OllamaGeneration()
        self.chat_stream_lock = threading.Lock()

    def chat(self,
             type: str,
             prompt: str,
             content: str,
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: List[Dict[str, str]],
             model_name: str=None,
             temperature: float=-1) -> str:
        strategy = self.get_strategy(type)
        result = strategy.chat(prompt=prompt,
                               content=content,
                               user_name=user_name,
                               user_text=user_text,
                               role_name=role_name,
                               short_history=short_history,
                               model_name=model_name,
                               temperature=temperature)
        return result

    def chatStream(self,
                   type: str,
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
        strategy = self.get_strategy(type)
        asyncio.run(strategy.chatStream(prompt=prompt,
                                        content=content,
                                        user_name=user_name,
                                        user_text=user_text,
                                        role_name=role_name,
                                        short_history=short_history,
                                        automatic=automatic,
                                        realtime_callback=realtime_callback,
                                        conversation_end_callback=conversation_end_callback,
                                        model_name=model_name,
                                        temperature=temperature))
        
    def get_embedding(self, type: str, text: str):
        strategy = self.get_strategy(type)
        result = strategy.get_embedding(text)
        return result

    def get_strategy(self, type: str) -> BaseLlmModel:
        if type == "openai":
            return self.openai
        elif type == "ollama":
            return self.ollama
        else:
            raise ValueError("Unknown type")
