import json
import logging
import os
from http import HTTPStatus
from dotenv import load_dotenv

from ag_ui.core import RunAgentInput
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from pydantic import ValidationError

from pydantic_ai import Agent
from pydantic_ai.ag_ui import SSE_CONTENT_TYPE, run_ag_ui
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings

llm_provider = OpenAIProvider(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)


# 初始化LLM模型
llm = OpenAIChatModel(model_name=settings.LLM_MODEL, provider=llm_provider)

# 创建Agent
agent = Agent(llm, instructions='Be fun!')