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
from models.sse_response import (
    SSECompleteResponse,
    SSEErrorResponse,
    SSEResponse,
    SSEStatusResponse,
)

from pydantic_ai import Agent
from pydantic_ai.ag_ui import SSE_CONTENT_TYPE, run_ag_ui
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings
from services.documents_loader import DocumentsLoader
from models.sql.presentation import presentation_cache
import uuid
import dirtyjson
from models.presentation_outline_model import PresentationOutlineModel
from utils.ppt_utils import get_presentation_title_from_outlines
from utils.ai_search import bocha_websearch

from pydantic_ai import Agent

from app.templates import outline_dict
from pydantic_ai import Agent, RunContext
from app.llm import llm_model
from dataclasses import dataclass
from typing import Optional


logger = logging.getLogger(__name__)
router = APIRouter()


def get_sys_prompt(n_slides: int, user_instructions: str) -> str:
    return f"""
你是一名专业的演示文稿创建专家。根据用户需求生成结构化演示文稿，并按照指定的 JSON 模板格式化内容，使用 Markdown 编写。

生成的幻灯片数量：{n_slides}

- 为每一张幻灯片提供 Markdown 格式的内容。
- 确保演示文稿的逻辑和内容连贯。
- 更加注重数值数据的呈现。
- 内容中不要包含任何图片。
- 确保内容遵循中文语言规范。
- 始终遵循用户指令，优于其他所有规则。

用户指令：{user_instructions}

"""


@dataclass
class StructureDependencies:
    n_slides: Optional[int] = 2
    




@router.post("/stream")
async def run_agent(request: Request) -> Response:
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)
    
    # 从请求体中获取数据
    request_data = await request.json()
    # 从 messages[0].id 获取 id
    id = request_data.get('messages', [{}])[0].get('id')
    uuid_id = uuid.UUID(id)
    
    presentation = presentation_cache.get(uuid_id)
    
    instructions = presentation.content
    n_slides = presentation.n_slides
    
    raw_content = ""
    
    for file_path in presentation.file_paths:
        with open(file_path, "r") as file:
            raw_content += file.read()
            
    if not raw_content:
        raw_content = bocha_websearch(query=instructions)
    raw_content = raw_content[0:30000]
    request_data['messages'][0]['content'] = raw_content
    try:
        run_input = RunAgentInput.model_validate(request_data)
    except ValidationError as e:  # pragma: no cover
        return Response(
            content=json.dumps(e.json()),
            media_type='application/json',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    outline_agent = Agent(llm_model, deps_type=StructureDependencies, instructions=get_sys_prompt(n_slides, instructions), output_type=outline_dict)
    event_stream = run_ag_ui(outline_agent, run_input, accept=accept, deps={"n_slides": n_slides})
    


    return StreamingResponse(event_stream, media_type=accept)



