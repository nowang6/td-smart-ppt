from fastapi import APIRouter
from app.api.v1.endpoints import chat, outline, files

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(outline.router, prefix="/outline", tags=["outline"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
