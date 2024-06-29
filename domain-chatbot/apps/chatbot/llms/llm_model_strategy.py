from __future__ import annotations
import threading
import asyncio

from .base_llm_model import ChatHistroy, BaseLlmModel
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
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: list[ChatHistroy],
             long_history: str) -> str:
        strategy = self.get_strategy(type)
        result = strategy.chat(prompt=prompt,
                               user_name=user_name,
                               user_text=user_text,
                               role_name=role_name,
                               short_history=short_history,
                               long_history=long_history)
        return result

    def chatStream(self,
                   type: str,
                   prompt: str,
                   user_name: str,
                   user_text: str,
                   role_name: str,
                   history: list[str, str],
                   realtime_callback=None,
                   conversation_end_callback=None):
        strategy = self.get_strategy(type)
        asyncio.run(strategy.chatStream(prompt=prompt,
                                        user_name=user_name,
                                        user_text=user_text,
                                        role_name=role_name,
                                        history=history,
                                        realtime_callback=realtime_callback,
                                        conversation_end_callback=conversation_end_callback))
        
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
