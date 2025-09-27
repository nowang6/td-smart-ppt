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
from app.agents.outline import agent


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/stream')
async def run_agent(request: Request) -> Response:
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)
    try:
        run_input = RunAgentInput.model_validate(await request.json())
    except ValidationError as e:  # pragma: no cover
        return Response(
            content=json.dumps(e.json()),
            media_type='application/json',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    event_stream = run_ag_ui(agent, run_input, accept=accept)

    return StreamingResponse(event_stream, media_type=accept)
