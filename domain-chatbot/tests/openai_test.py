import os
import logging
from typing import List
from litellm import completion
from litellm import embedding


logger = logging.getLogger(__name__)


class OpenAIGeneration:
    # completion_model_name: str = "gpt-4o"
    completion_model_name: str = "gpt-3.5-turbo"
    embedding_model_name: str = "text-embedding-ada-002"
    temperature: float = 0.7
    openai_base_url: str
    openai_api_key: str

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = "sk-proj-xuMwAoRDRqykJ2yDiUVzT3BlbkFJgtw5NHuvB86gW7Yj6wye"
        # self.openai_base_url = os.environ["OPENAI_BASE_URL"]
        # self.openai_api_key = os.environ["OPENAI_API_KEY"]
    
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
text_embedding = openAIGeneration.get_embedding("中国")
print(len(text_embedding))
