from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings


llm_provider = OpenAIProvider(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
llm_model = OpenAIChatModel(model_name=settings.LLM_MODEL, provider=llm_provider)