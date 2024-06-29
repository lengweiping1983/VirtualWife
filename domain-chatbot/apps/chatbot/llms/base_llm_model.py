from abc import ABC, abstractmethod


class ChatHistroy:
    role: str
    content: str

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class BaseLlmModel(ABC):

    @abstractmethod
    def chat(self,
             prompt: str,
             user_name: str,
             user_text: str,
             role_name: str,
             short_history: list[ChatHistroy],
             long_history: str) -> str:
        pass

    @abstractmethod
    async def chatStream(self,
                         prompt: str,
                         user_name: str,
                         user_text: str,
                         role_name: str,
                         history: list[str, str],
                         realtime_callback=None,
                         conversation_end_callback=None):
        pass

    @abstractmethod
    def get_embedding(self, text: str):
        pass
