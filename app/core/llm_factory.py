from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm(provider: str = "gemini", model_name: Optional[str] = None) -> BaseChatModel:
    """
    Factory function returning a configured LangChain ChatModel for Gemini or OpenAI.
    """
    provider = provider.lower()
    
    if provider == "gemini":
        model = model_name or settings.DEFAULT_GEMINI_MODEL
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            import os
            api_key = os.getenv("GEMINI_API_KEY", "")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7,
        )
    elif provider == "openai":
        model = model_name or settings.DEFAULT_OPENAI_MODEL
        return ChatOpenAI(
            model=model,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
    else:
        raise ValueError(f"Unsupported provider '{provider}'. Must be 'gemini' or 'openai'.")
