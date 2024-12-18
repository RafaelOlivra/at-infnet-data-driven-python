import os

from services.chat_agent import FootballChatAgent
from langchain_openai import ChatOpenAI


class OpenAIAgent(FootballChatAgent):
    def _setup_llm(self) -> ChatOpenAI:
        self.name = "OpenAI Chat Agent"
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=600,
            streaming=True,
        )
