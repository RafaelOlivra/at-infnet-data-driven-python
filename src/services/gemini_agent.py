import os

from services.chat_agent import SmartChatAgent
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiAgent(SmartChatAgent):
    def _setup_llm(self) -> ChatGoogleGenerativeAI:
        self.name = "Gemini Chat Agent"
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
