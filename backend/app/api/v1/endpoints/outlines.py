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
from app.agents.outline import agent
from services.documents_loader import DocumentsLoader
from models.sql.presentation import presentation_cache
import uuid
import dirtyjson
from models.presentation_outline_model import PresentationOutlineModel
from utils.ppt_utils import get_presentation_title_from_outlines


logger = logging.getLogger(__name__)
router = APIRouter()


# async def get_outline_from_stream(event_stream) -> PresentationOutlineModel:
    
#     agent_outlines_text = ""
    
#     async for chunk in event_stream:
#         agent_outlines_text += chunk
#         yield chunk
    
#     try:
#         agent_outlines_json = dict(
#             dirtyjson.loads(agent_outlines_text)
#         )
#     except Exception as e:
#         yield SSEErrorResponse(
#             detail=f"Failed to generate presentation outlines. Please try again. {str(e)}",
#         ).to_string()
#         return

#     presentation_outlines = PresentationOutlineModel(**agent_outlines_json)
    
#     return presentation_outlines

    

@router.post("/stream")
async def run_agent(request: Request) -> Response:
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)
    
    # 从请求体中获取数据
    request_data = await request.json()
    # 从 messages[0].id 获取 id
    id = request_data.get('messages', [{}])[0].get('id')
    uuid_id = uuid.UUID(id)
    
    presentation = presentation_cache.get(uuid_id)
    
    files_content = ""
    
    for file_path in presentation.file_paths:
        with open(file_path, "r") as file:
            files_content += file.read()
    request_data['messages'][0]['content'] = files_content
    try:
        run_input = RunAgentInput.model_validate(request_data)
    except ValidationError as e:  # pragma: no cover
        return Response(
            content=json.dumps(e.json()),
            media_type='application/json',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    event_stream = run_ag_ui(agent, run_input, accept=accept)
    
    # # 使用包装器保存流内容
    # presentation_outlines = get_outline_from_stream(event_stream)
    
    # n_slides_to_generate = presentation.n_slides
    # presentation_outlines.slides = presentation_outlines.slides[
    #     :n_slides_to_generate
    # ]

    # presentation.outlines = presentation_outlines.model_dump()
    # presentation.title = get_presentation_title_from_outlines(presentation_outlines)


    return StreamingResponse(event_stream, media_type=accept)



