import os
import logging
from typing import Any, Dict, List
from litellm import completion
from litellm import embedding


logger = logging.getLogger(__name__)
OPENAI_API_KEY = "sk-"


class OpenAIGeneration:
    completion_model_name: str = "openai/gpt-4o"
    # completion_model_name: str = "openai/gpt-3.5-turbo"
    embedding_model_name: str = "openai/text-embedding-ada-002"
    temperature: float = 0.7
    openai_base_url: str
    openai_api_key: str

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        # self.openai_base_url = os.environ["OPENAI_BASE_URL"]
        # self.openai_api_key = os.environ["OPENAI_API_KEY"]
    
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
        response = completion(
            model=completion_model_name,
            messages=messages,
            temperature=temperature,
        )
        llm_result_text = response.choices[0].message.content if response.choices else ""
        return llm_result_text

    def get_embedding(self, text: str):
        text = text.replace("\n", " ")

        response = embedding(
            model=self.embedding_model_name,
            input=[text]
        )
        if response.data and len(response.data) > 0:
            text_embedding = response.data[0]["embedding"]
            return text_embedding
        return None


openAIGeneration = OpenAIGeneration()
llm_result_text = openAIGeneration.chat(prompt=None,
                                       content=None,
                                       user_name=None,
                                       user_text="你好！",
                                       role_name=None,
                                       short_history=None)
print(llm_result_text)
# text_embedding = openAIGeneration.get_embedding("中国")
# print(len(text_embedding))


import os 
from litellm import completion

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# openai call
response = completion(
    model = "openai/gpt-4o", 
    messages=[{ "content": "Hello, how are you?", "role": "user"}]
)
llm_result_text = response.choices[0].message.content if response.choices else ""
print(llm_result_text)
