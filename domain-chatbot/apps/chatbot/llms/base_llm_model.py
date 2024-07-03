from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ChatHistroy:
    role: str
    content: str

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class BaseLlmModel(ABC):

    def get_messages(self,
                     prompt: str,
                     content: str,
                     user_name: str,
                     user_text: str,
                     role_name: str,
                     short_history: List[Dict[str, str]]) -> list:
        messages = []
        if prompt is not None and prompt != "":
            messages.append({"role": "system", "content": prompt})
        if short_history is not None:
            for item in short_history:
                print(f"chat item={item}")
                if item.get("user") and item.get("user") != "":
                    messages.append({"role": "user", "content": item["user"]})
                if item.get("assistant") and item.get("assistant") != "":
                    messages.append({"role": "assistant", "content": item["assistant"]})
        if content and content != "":
            messages.append({"role": "user", "content": content})
        if user_text and user_text != "":
            messages.append({"role": "user", "content": user_text})
        return messages
    
    @abstractmethod
    def chat(self,
             prompt: str,
             content: str,
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: List[Dict[str, str]],
             model_name: str=None,
             temperature: float=-1) -> str:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_embedding(self, text: str):
        pass
